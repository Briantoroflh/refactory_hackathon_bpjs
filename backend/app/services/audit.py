"""
Audit logging utilities for automatic logging of system actions
"""
from datetime import datetime, timezone
from typing import Optional, Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import UserLog, AuditSystemLog, CommitChangeLogs
import json


async def log_action(
    db: AsyncSession,
    user_id: Optional[int],
    action: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[str] = None,
) -> UserLog:
    """
    Log a user action
    
    - **user_id**: ID of user performing the action
    - **action**: Action type (e.g., 'CREATE', 'UPDATE', 'DELETE', 'LOGIN')
    - **resource_type**: Type of resource affected (e.g., 'PROJECT', 'TASK', 'USER')
    - **resource_id**: ID of resource affected
    - **ip_address**: IP address of request
    - **user_agent**: User agent string
    - **details**: Additional details in JSON string format
    """
    log = UserLog(
        user_id=user_id,
        action=action,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details,
        created_at=datetime.now(),
    )
    
    db.add(log)
    await db.flush()  # Flush to get the log ID without committing
    
    return log


async def log_field_change(
    db: AsyncSession,
    action: str,
    resource_type: str,
    resource_id: int,
    field_name: str,
    old_value: Any,
    new_value: Any,
    changed_by_user_id: Optional[int] = None,
) -> AuditSystemLog:
    """
    Log a field change for audit trail
    
    - **action**: Action type ('CREATE', 'UPDATE', 'DELETE')
    - **resource_type**: Type of resource (e.g., 'PROJECT', 'TASK')
    - **resource_id**: ID of resource
    - **field_name**: Name of field that changed
    - **old_value**: Previous value
    - **new_value**: New value
    - **changed_by_user_id**: ID of user making the change
    """
    # Convert values to string representation
    old_str = json.dumps(old_value) if old_value is not None else None
    new_str = json.dumps(new_value) if new_value is not None else None
    
    log = AuditSystemLog(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        field_name=field_name,
        old_value=old_str,
        new_value=new_str,
        changed_by_user_id=changed_by_user_id,
        timestamp=datetime.now(timezone.utc),
    )
    
    db.add(log)
    await db.flush()
    
    return log


async def log_auth_event(
    db: AsyncSession,
    user_id: Optional[int],
    event_type: str,  # 'LOGIN', 'LOGOUT', 'LOGIN_FAILED'
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    reason: Optional[str] = None,
) -> UserLog:
    """
    Log authentication event
    
    - **user_id**: ID of user (None for failed logins)
    - **event_type**: 'LOGIN', 'LOGOUT', 'LOGIN_FAILED'
    - **ip_address**: IP address
    - **user_agent**: User agent
    - **reason**: Reason for failed login
    """
    return await log_action(
        db,
        user_id=user_id,
        action=event_type,
        ip_address=ip_address,
        user_agent=user_agent,
        details=reason,
    )


async def log_authorization_event(
    db: AsyncSession,
    user_id: Optional[int],
    denied_action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> UserLog:
    """
    Log unauthorized access attempt
    
    - **user_id**: ID of user attempting action
    - **denied_action**: Action that was denied
    - **resource_type**: Type of resource
    - **resource_id**: ID of resource
    - **ip_address**: IP address
    - **user_agent**: User agent
    """
    return await log_action(
        db,
        user_id=user_id,
        action="UNAUTHORIZED_ACCESS",
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        user_agent=user_agent,
        details=f"Denied: {denied_action}",
    )


async def log_commit_change(
    db: AsyncSession,
    commit_id: int,
    field_name: str,
    old_value: str,
    new_value: str,
    changed_by_user_id: Optional[int] = None,
    change_reason: Optional[str] = None,
) -> CommitChangeLogs:
    """
    Log commit change for audit trail
    
    - **commit_id**: ID of commit
    - **field_name**: Field that changed
    - **old_value**: Previous value
    - **new_value**: New value
    - **changed_by_user_id**: User making the change
    - **change_reason**: Reason for change
    """
    log = CommitChangeLogs(
        commit_id=commit_id,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value,
        changed_by_user_id=changed_by_user_id,
        change_reason=change_reason,
        timestamp=datetime.now(timezone.utc),
    )
    
    db.add(log)
    await db.flush()
    
    return log
