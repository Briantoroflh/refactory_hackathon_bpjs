"""
Audit logs retrieval and filtering endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.databases import get_db
from app.controllers.audit import (
    get_audit_logs as controller_get_audit_logs,
    get_logs_by_action as controller_get_logs_by_action,
    get_logs_by_resource as controller_get_logs_by_resource,
    get_system_audit_logs as controller_get_system_audit_logs,
    get_user_audit_logs as controller_get_user_audit_logs,
)

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


async def require_auth():
    """Dependency to check authentication"""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )


async def require_admin():
    """Dependency to check admin permission"""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin access required",
    )


@router.get("")
async def get_audit_logs(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """
    Get audit logs (admin only) with pagination
    
    - **skip**: Pagination offset
    - **limit**: Max records
    - **start_date**: Filter from date (ISO format)
    - **end_date**: Filter to date (ISO format)
    """
    return await controller_get_audit_logs(db, skip, limit, start_date, end_date)


@router.get("/user/{user_id}")
async def get_user_audit_logs(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Get audit logs for specific user (admin only)
    
    - **user_id**: User ID to search for
    - **skip**: Pagination offset
    - **limit**: Max records
    """
    return await controller_get_user_audit_logs(user_id, db, skip, limit)


@router.get("/action/{action}")
async def get_logs_by_action(
    action: str,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Get audit logs filtered by action (admin only)
    
    - **action**: Action type to search (e.g., 'CREATE', 'UPDATE', 'DELETE')
    - **skip**: Pagination offset
    - **limit**: Max records
    """
    return await controller_get_logs_by_action(action, db, skip, limit)


@router.get("/resource/{resource_id}")
async def get_logs_by_resource(
    resource_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    resource_type: Optional[str] = None,
):
    """
    Get audit logs for specific resource (admin only)
    
    - **resource_id**: Resource ID to search for
    - **resource_type**: Optional filter by resource type
    - **skip**: Pagination offset
    - **limit**: Max records
    """
    return await controller_get_logs_by_resource(resource_id, db, skip, limit, resource_type)


@router.get("/system")
async def get_system_audit_logs(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    resource_type: Optional[str] = None,
    action: Optional[str] = None,
):
    """
    Get system audit logs (admin only) - for sensitive operations
    
    - **skip**: Pagination offset
    - **limit**: Max records
    - **resource_type**: Filter by resource type
    - **action**: Filter by action
    """
    return await controller_get_system_audit_logs(db, skip, limit, resource_type, action)
