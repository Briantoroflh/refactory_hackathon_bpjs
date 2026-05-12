"""
User controller logic.
"""
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Role, User, UserRole


async def get_user(user_id: int, db: AsyncSession):
    stmt = select(User).where(User.user_id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


async def update_user(user_id: int, update_data: dict, db: AsyncSession):
    stmt = select(User).where(User.user_id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if "full_name" in update_data:
        user.full_name = update_data["full_name"]

    if "is_active" in update_data:
        user.is_active = update_data["is_active"]

    user.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(user)
    return user


async def assign_role_to_user(user_id: int, role_id: int, db: AsyncSession):
    stmt = select(User).where(User.user_id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    stmt = select(Role).where(Role.role_id == role_id)
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    stmt = select(UserRole).where(and_(UserRole.user_id == user_id, UserRole.role_id == role_id))
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already has this role")

    db.add(UserRole(user_id=user_id, role_id=role_id))
    await db.commit()
    return role


async def remove_role_from_user(user_id: int, role_id: int, db: AsyncSession):
    stmt = select(UserRole).where(and_(UserRole.user_id == user_id, UserRole.role_id == role_id))
    result = await db.execute(stmt)
    user_role = result.scalar_one_or_none()

    if not user_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User role assignment not found")

    await db.delete(user_role)
    await db.commit()
    return {"message": "Role removed from user"}


async def get_user_roles(user_id: int, db: AsyncSession):
    stmt = select(Role).join(UserRole).where(UserRole.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalars().all()