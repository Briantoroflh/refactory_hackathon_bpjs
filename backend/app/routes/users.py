"""
User management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from typing import List
from app.models import User, Role, UserRole
from app.databases import get_db
from app.services.schemas import UserResponse, RoleResponse
from datetime import datetime, timezone

router = APIRouter(prefix="/users", tags=["users"])


async def require_auth():
    """
    Dependency to check authentication
    TODO: Implement token validation
    """
    # Placeholder for JWT validation
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get user by ID
    
    - **user_id**: User ID
    """
    stmt = select(User).where(User.user_id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    update_data: dict,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Update user profile
    
    - **user_id**: User ID
    - **full_name**: Optional full name
    - **is_active**: Optional active status (admin only)
    """
    # TODO: Check if user_id == current_user.user_id for authorization
    
    stmt = select(User).where(User.user_id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update allowed fields
    if "full_name" in update_data:
        user.full_name = update_data["full_name"]
    
    if "is_active" in update_data:  # TODO: check admin role
        user.is_active = update_data["is_active"]
    
    user.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(user)
    
    return user


@router.post("/{user_id}/roles", response_model=RoleResponse)
async def assign_role_to_user(
    user_id: int,
    role_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Assign role to user (admin only)
    
    - **user_id**: User ID
    - **role_id**: Role ID to assign
    """
    # Check if user is admin (TODO: implement proper admin check)
    
    stmt = select(User).where(User.user_id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    stmt = select(Role).where(Role.role_id == role_id)
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Check if user already has this role
    stmt = select(UserRole).where(
        and_(UserRole.user_id == user_id, UserRole.role_id == role_id)
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has this role"
        )
    
    # Assign role
    user_role = UserRole(user_id=user_id, role_id=role_id)
    db.add(user_role)
    await db.commit()
    
    return role


@router.delete("/{user_id}/roles/{role_id}")
async def remove_role_from_user(
    user_id: int,
    role_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Remove role from user (admin only)
    
    - **user_id**: User ID
    - **role_id**: Role ID to remove
    """
    # Check if user is admin (TODO: implement proper admin check)
    
    stmt = select(UserRole).where(
        and_(UserRole.user_id == user_id, UserRole.role_id == role_id)
    )
    result = await db.execute(stmt)
    user_role = result.scalar_one_or_none()
    
    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User role assignment not found"
        )
    
    await db.delete(user_role)
    await db.commit()
    
    return {"message": "Role removed from user"}


@router.get("/{user_id}/roles", response_model=List[RoleResponse])
async def get_user_roles(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get all roles assigned to a user
    
    - **user_id**: User ID
    """
    stmt = select(Role).join(UserRole).where(UserRole.user_id == user_id)
    result = await db.execute(stmt)
    roles = result.scalars().all()
    
    return roles
