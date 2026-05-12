"""
Authentication controller logic.
"""
from fastapi import HTTPException, Request, status, Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.databases import get_db
from app.models import User, Role, UserRole
from app.services import (
    hash_password,
    create_access_token,
    create_refresh_token,
    verify_password,
    verify_token,
)
from app.services.schemas import (
    LoginResponse,
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)


async def register_user(req: UserRegisterRequest, db: AsyncSession) -> TokenResponse:
    stmt = select(User).where(User.email == req.email)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        full_name=req.full_name,
        is_active=True,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.user_id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.user_id), "email": user.email})

    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=15 * 60,
    )


async def login_user(req: UserLoginRequest, db: AsyncSession, request: Request | None = None) -> LoginResponse:
    stmt = select(User).where(User.email == req.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    ip_address = request.client.host if request else None
    user_agent = request.headers.get("user-agent") if request else None

    if not user or not verify_password(req.password, user.password_hash):
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive",
        )

    access_token = create_access_token(data={"sub": str(user.user_id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.user_id), "email": user.email})

    # load user roles (names)
    stmt = select(Role.name).join(UserRole, Role.role_id == UserRole.role_id).where(UserRole.user_id == user.user_id)
    role_result = await db.execute(stmt)
    role_names = [r for (r,) in role_result.all()]

    await db.commit()

    user_data = UserResponse.model_validate(user)
    user_data.roles = role_names

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=15 * 60,
        user=user_data,
    )


async def refresh_token(req: TokenRefreshRequest) -> TokenResponse:
    payload = verify_token(req.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    email = payload.get("email")

    if not user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token data",
        )

    access_token = create_access_token(data={"sub": user_id, "email": email})

    return TokenResponse(
        access_token=access_token,
        refresh_token=req.refresh_token,
        expires_in=15 * 60,
    )


async def get_current_user(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency to return currently authenticated `User` from Authorization header.

    Raises HTTP 401 when token missing/invalid or user not found/inactive.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = authorization.split(" ", 1)[1].strip()
    payload = verify_token(token)
    if not payload or payload.get("type") == "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    stmt = select(User).where(User.user_id == int(user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return user