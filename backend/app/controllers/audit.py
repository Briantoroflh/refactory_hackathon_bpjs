"""
Audit controller logic.
"""
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import AuditSystemLog, UserLog


async def get_audit_logs(db: AsyncSession, skip: int, limit: int, start_date: Optional[str], end_date: Optional[str]):
    stmt = select(UserLog)
    if start_date:
        stmt = stmt.where(UserLog.timestamp >= start_date)
    if end_date:
        stmt = stmt.where(UserLog.timestamp <= end_date)
    stmt = stmt.offset(skip).limit(limit).order_by(UserLog.timestamp.desc())
    result = await db.execute(stmt)
    logs = result.scalars().all()
    return {"logs": logs, "skip": skip, "limit": limit}


async def get_user_audit_logs(user_id: int, db: AsyncSession, skip: int, limit: int):
    stmt = select(UserLog).where(UserLog.user_id == user_id)
    stmt = stmt.offset(skip).limit(limit).order_by(UserLog.timestamp.desc())
    result = await db.execute(stmt)
    logs = result.scalars().all()
    return {"user_id": user_id, "logs": logs, "skip": skip, "limit": limit}


async def get_logs_by_action(action: str, db: AsyncSession, skip: int, limit: int):
    stmt = select(UserLog).where(UserLog.action == action)
    stmt = stmt.offset(skip).limit(limit).order_by(UserLog.timestamp.desc())
    result = await db.execute(stmt)
    logs = result.scalars().all()
    return {"action": action, "logs": logs, "skip": skip, "limit": limit}


async def get_logs_by_resource(resource_id: int, db: AsyncSession, skip: int, limit: int, resource_type: Optional[str]):
    stmt = select(UserLog).where(UserLog.resource_id == resource_id)
    if resource_type:
        stmt = stmt.where(UserLog.resource_type == resource_type)
    stmt = stmt.offset(skip).limit(limit).order_by(UserLog.timestamp.desc())
    result = await db.execute(stmt)
    logs = result.scalars().all()
    return {"resource_id": resource_id, "resource_type": resource_type, "logs": logs, "skip": skip, "limit": limit}


async def get_system_audit_logs(db: AsyncSession, skip: int, limit: int, resource_type: Optional[str], action: Optional[str]):
    stmt = select(AuditSystemLog)
    if resource_type:
        stmt = stmt.where(AuditSystemLog.resource_type == resource_type)
    if action:
        stmt = stmt.where(AuditSystemLog.action == action)
    stmt = stmt.offset(skip).limit(limit).order_by(AuditSystemLog.timestamp.desc())
    result = await db.execute(stmt)
    logs = result.scalars().all()
    return {"logs": logs, "skip": skip, "limit": limit}