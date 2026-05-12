"""
User management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.databases import get_db
from app.controllers.users import (
    assign_role_to_user as controller_assign_role_to_user,
    get_user as controller_get_user,
    get_user_roles as controller_get_user_roles,
    remove_role_from_user as controller_remove_role_from_user,
    update_user as controller_update_user,
)
from app.services.schemas import UserResponse, RoleResponse

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
    return await controller_get_user(user_id, db)


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
    return await controller_update_user(user_id, update_data, db)


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
    return await controller_assign_role_to_user(user_id, role_id, db)


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
    return await controller_remove_role_from_user(user_id, role_id, db)


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
    return await controller_get_user_roles(user_id, db)
