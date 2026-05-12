"""
Role and permission management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from typing import List
from app.models import Role, Permission, RolePermission
from app.databases import get_db
from app.services.schemas import RoleResponse, PermissionResponse
from datetime import datetime, timezone

router = APIRouter(prefix="/roles", tags=["roles"])


async def require_auth():
    """Dependency to check authentication - TODO: Implement token validation"""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )


@router.get("", response_model=List[RoleResponse])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """
    List all roles with their permissions
    
    - **skip**: Pagination offset
    - **limit**: Max records (1-100)
    """
    stmt = select(Role).offset(skip).limit(limit)
    result = await db.execute(stmt)
    roles = result.scalars().all()
    
    return roles


@router.post("", response_model=RoleResponse)
async def create_role(
    name: str = Query(...),
    description: str = Query(None),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Create a new role (admin only)
    
    - **name**: Role name (must be unique)
    - **description**: Role description
    """
    # Check if role already exists
    stmt = select(Role).where(Role.name == name)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with this name already exists"
        )
    
    role = Role(
        name=name,
        description=description,
        is_system=False,  # User-created role
    )
    
    db.add(role)
    await db.commit()
    await db.refresh(role)
    
    return role


@router.post("/{role_id}/permissions")
async def assign_permission_to_role(
    role_id: int,
    permission_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Assign a permission to a role (admin only)
    
    - **role_id**: Role ID
    - **permission_id**: Permission ID to assign
    """
    # Verify role exists
    stmt = select(Role).where(Role.role_id == role_id)
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Verify permission exists
    stmt = select(Permission).where(Permission.permission_id == permission_id)
    result = await db.execute(stmt)
    permission = result.scalar_one_or_none()
    
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    # Check if already assigned
    stmt = select(RolePermission).where(
        and_(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id
        )
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission already assigned to this role"
        )
    
    # Assign permission
    role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
    db.add(role_permission)
    await db.commit()
    
    return {"message": "Permission assigned to role successfully"}


@router.delete("/{role_id}/permissions/{permission_id}")
async def remove_permission_from_role(
    role_id: int,
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Remove a permission from a role (admin only)
    
    - **role_id**: Role ID
    - **permission_id**: Permission ID to remove
    """
    stmt = select(RolePermission).where(
        and_(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id
        )
    )
    result = await db.execute(stmt)
    role_permission = result.scalar_one_or_none()
    
    if not role_permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not assigned to this role"
        )
    
    await db.delete(role_permission)
    await db.commit()
    
    return {"message": "Permission removed from role successfully"}
