"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.databases import get_db
from app.controllers.auth import login_user, refresh_token, register_user
from app.services.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    LoginResponse,
    TokenRefreshRequest,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(req: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    Register a new user
    
    - **email**: User email address
    - **password**: Minimum 8 characters
    - **full_name**: Optional full name
    """
    return await register_user(req, db)


@router.post("/login", response_model=LoginResponse)
async def login(req: UserLoginRequest, db: AsyncSession = Depends(get_db), request: Request = None):
    """
    Login with email and password
    
    - **email**: User email address
    - **password**: User password
    """
    return await login_user(req, db, request)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(req: TokenRefreshRequest):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token from login
    """
    return await refresh_token(req)


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str = Depends(lambda: ""),  # Will be replaced with actual dependency
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user profile
    
    Requires valid access token in Authorization header
    """
    # This is a placeholder - actual implementation needs auth dependency
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
