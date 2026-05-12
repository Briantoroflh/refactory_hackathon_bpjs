"""
Authentication controller logic.
"""
from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import User
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

    await db.commit()

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=15 * 60,
        user=UserResponse.model_validate(user),
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