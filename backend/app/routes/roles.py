"""
Role and permission management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.databases import get_db
from app.controllers.roles import (
    assign_permission_to_role as controller_assign_permission_to_role,
    create_role as controller_create_role,
    list_roles as controller_list_roles,
    remove_permission_from_role as controller_remove_permission_from_role,
)
from app.services.schemas import RoleResponse, PermissionResponse

router = APIRouter(prefix="/roles", tags=["roles"])


from app.routes.dependencies import require_auth



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
    return await controller_list_roles(db, skip, limit)


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
    return await controller_create_role(name, description, db)


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
    return await controller_assign_permission_to_role(role_id, permission_id, db)


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
    return await controller_remove_permission_from_role(role_id, permission_id, db)
