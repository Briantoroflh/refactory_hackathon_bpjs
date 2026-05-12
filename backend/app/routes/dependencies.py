from fastapi import Depends, HTTPException, status, Cookie, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.databases import get_db
from app.services import verify_token
from app.models.auth import User, UserRole, Role


async def require_auth(
    access_token: str | None = Cookie(None),
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Dependency that validates JWT from access_token cookie or Authorization header.
    Returns User instance on success, raises HTTPException(401) on failure.
    """
    token = access_token
    if not token and authorization:
        if authorization.startswith("Bearer "):
            token = authorization[len("Bearer "):]
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    try:
        user_id_int = int(user_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    stmt = select(User).where(User.user_id == user_id_int)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive")

    return user


async def require_admin(current_user: User = Depends(require_auth)):
    """Simple admin check: verifies user has any role named 'admin' or 'administrator'."""
    # check roles
    for ur in getattr(current_user, 'user_roles', []) or []:
        role = getattr(ur, 'role', None)
        if role and getattr(role, 'name', '').lower() in ("admin", "administrator", "system_admin"):
            return current_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
