"""
Role controller logic.
"""
from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Permission, Role, RolePermission


async def list_roles(db: AsyncSession, skip: int, limit: int):
    stmt = select(Role).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_role(name: str, description: str | None, db: AsyncSession):
    stmt = select(Role).where(Role.name == name)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role with this name already exists")

    role = Role(name=name, description=description, is_system=False)
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


async def assign_permission_to_role(role_id: int, permission_id: int, db: AsyncSession):
    stmt = select(Role).where(Role.role_id == role_id)
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    stmt = select(Permission).where(Permission.permission_id == permission_id)
    result = await db.execute(stmt)
    permission = result.scalar_one_or_none()
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")

    stmt = select(RolePermission).where(and_(RolePermission.role_id == role_id, RolePermission.permission_id == permission_id))
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Permission already assigned to this role")

    db.add(RolePermission(role_id=role_id, permission_id=permission_id))
    await db.commit()
    return {"message": "Permission assigned to role successfully"}


async def remove_permission_from_role(role_id: int, permission_id: int, db: AsyncSession):
    stmt = select(RolePermission).where(and_(RolePermission.role_id == role_id, RolePermission.permission_id == permission_id))
    result = await db.execute(stmt)
    role_permission = result.scalar_one_or_none()
    if not role_permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not assigned to this role")

    await db.delete(role_permission)
    await db.commit()
    return {"message": "Permission removed from role successfully"}