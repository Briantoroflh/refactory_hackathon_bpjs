"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User
from app.databases import get_db
from app.services import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.services.audit import log_action, log_auth_event
from app.services.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    TokenRefreshRequest,
    UserResponse,
)
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(req: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    Register a new user
    
    - **email**: User email address
    - **password**: Minimum 8 characters
    - **full_name**: Optional full name
    """
    # Check if user already exists
    stmt = select(User).where(User.email == req.email)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        full_name=req.full_name,
        is_active=True,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Log user creation
    await log_action(
        db,
        user_id=user.user_id,
        action="CREATE",
        resource_type="USER",
        resource_id=user.user_id,
        details=f"User registered: {user.email}"
    )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.user_id, "email": user.email})
    refresh_token = create_refresh_token(data={"sub": user.user_id, "email": user.email})
    
    await db.commit()  # Commit audit logs
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=15 * 60,  # 15 minutes
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: UserLoginRequest, db: AsyncSession = Depends(get_db), request: Request = None):
    """
    Login with email and password
    
    - **email**: User email address
    - **password**: User password
    """
    # Find user by email
    stmt = select(User).where(User.email == req.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    ip_address = request.client.host if request else None
    user_agent = request.headers.get("user-agent") if request else None
    
    if not user or not verify_password(req.password, user.password_hash):
        # Log failed login
        # await log_auth_event(
        #     db,
        #     user_id=None,
        #     event_type="LOGIN_FAILED",
        #     ip_address=ip_address,
        #     user_agent=user_agent,
        #     reason="Invalid credentials for email: " + req.email
        # )
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.user_id, "email": user.email})
    refresh_token = create_refresh_token(data={"sub": user.user_id, "email": user.email})
    
    # Log successful login
    # await log_auth_event(
    #     db,
    #     user_id=user.user_id,
    #     event_type="LOGIN",
    #     ip_address=ip_address,
    #     user_agent=user_agent,
    # )
    await db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=15 * 60,  # 15 minutes
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.user_id, "email": user.email})
    refresh_token = create_refresh_token(data={"sub": user.user_id, "email": user.email})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=15 * 60,  # 15 minutes
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(req: TokenRefreshRequest):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token from login
    """
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
    
    # Create new access token
    access_token = create_access_token(data={"sub": user_id, "email": email})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=req.refresh_token,  # Return same refresh token
        expires_in=15 * 60,  # 15 minutes
    )


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
