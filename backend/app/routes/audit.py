"""
Audit logs retrieval and filtering endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_
from typing import Optional
from app.models import UserLog, AuditSystemLog
from app.databases import get_db
from datetime import datetime, timezone

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
    stmt = select(UserLog)
    
    if start_date:
        stmt = stmt.where(UserLog.timestamp >= start_date)
    
    if end_date:
        stmt = stmt.where(UserLog.timestamp <= end_date)
    
    stmt = stmt.offset(skip).limit(limit).order_by(UserLog.timestamp.desc())
    
    result = await db.execute(stmt)
    logs = result.scalars().all()
    
    return {"logs": logs, "skip": skip, "limit": limit}


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
    stmt = select(UserLog).where(UserLog.user_id == user_id)
    
    stmt = stmt.offset(skip).limit(limit).order_by(UserLog.timestamp.desc())
    
    result = await db.execute(stmt)
    logs = result.scalars().all()
    
    return {"user_id": user_id, "logs": logs, "skip": skip, "limit": limit}


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
    stmt = select(UserLog).where(UserLog.action == action)
    
    stmt = stmt.offset(skip).limit(limit).order_by(UserLog.timestamp.desc())
    
    result = await db.execute(stmt)
    logs = result.scalars().all()
    
    return {"action": action, "logs": logs, "skip": skip, "limit": limit}


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
    stmt = select(UserLog).where(UserLog.resource_id == resource_id)
    
    if resource_type:
        stmt = stmt.where(UserLog.resource_type == resource_type)
    
    stmt = stmt.offset(skip).limit(limit).order_by(UserLog.timestamp.desc())
    
    result = await db.execute(stmt)
    logs = result.scalars().all()
    
    return {
        "resource_id": resource_id,
        "resource_type": resource_type,
        "logs": logs,
        "skip": skip,
        "limit": limit
    }


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
    stmt = select(AuditSystemLog)
    
    if resource_type:
        stmt = stmt.where(AuditSystemLog.resource_type == resource_type)
    
    if action:
        stmt = stmt.where(AuditSystemLog.action == action)
    
    stmt = stmt.offset(skip).limit(limit).order_by(AuditSystemLog.timestamp.desc())
    
    result = await db.execute(stmt)
    logs = result.scalars().all()
    
    return {"logs": logs, "skip": skip, "limit": limit}
