"""
Team and organization controller logic.
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.controllers.common import commit_and_refresh, fetch_one_or_404
from app.models import Category, Division, Team, TeamMember, Worker


async def create_team(name: str, category_id: int, description: Optional[str], capacity_hours: float, db: AsyncSession):
    stmt = select(Category).where(Category.category_id == category_id)
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    team = Team(name=name, category_id=category_id, description=description, capacity_hours=capacity_hours, status="active")
    db.add(team)
    return await commit_and_refresh(db, team)


async def list_teams(db: AsyncSession, skip: int, limit: int, category_id: Optional[int], status_filter: Optional[str]):
    stmt = select(Team)
    if category_id:
        stmt = stmt.where(Team.category_id == category_id)
    if status_filter:
        stmt = stmt.where(Team.status == status_filter)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_team(team_id: int, db: AsyncSession):
    stmt = select(Team).where(Team.team_id == team_id)
    return await fetch_one_or_404(db, stmt, "Team not found")


async def update_team(team_id: int, name: Optional[str], description: Optional[str], capacity_hours: Optional[float], status_value: Optional[str], db: AsyncSession):
    stmt = select(Team).where(Team.team_id == team_id)
    result = await db.execute(stmt)
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    if name:
        team.name = name
    if description is not None:
        team.description = description
    if capacity_hours:
        team.capacity_hours = capacity_hours
    if status_value:
        team.status = status_value

    team.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(team)
    return team


async def add_team_member(team_id: int, worker_id: int, role: str, db: AsyncSession):
    stmt = select(Team).where(Team.team_id == team_id)
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    stmt = select(Worker).where(Worker.worker_id == worker_id)
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker not found")

    stmt = select(TeamMember).where(and_(TeamMember.team_id == team_id, TeamMember.worker_id == worker_id))
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Worker is already a member of this team")

    member = TeamMember(team_id=team_id, worker_id=worker_id, role=role, join_date=datetime.now(timezone.utc))
    db.add(member)
    await db.commit()
    return {"message": "Member added to team successfully"}


async def remove_team_member(team_id: int, member_id: int, db: AsyncSession):
    stmt = select(TeamMember).where(and_(TeamMember.team_member_id == member_id, TeamMember.team_id == team_id))
    result = await db.execute(stmt)
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team member not found")

    await db.delete(member)
    await db.commit()
    return {"message": "Member removed from team successfully"}


async def get_team_members(team_id: int, db: AsyncSession):
    stmt = select(TeamMember).where(TeamMember.team_id == team_id)
    result = await db.execute(stmt)
    members = result.scalars().all()
    return {"team_id": team_id, "members": members}


async def get_my_teams():
    return {"teams": []}


async def create_division(name: str, description: Optional[str], db: AsyncSession):
    stmt = select(Division).where(Division.name == name)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Division with this name already exists")

    division = Division(name=name, description=description)
    db.add(division)
    return await commit_and_refresh(db, division)


async def list_divisions(db: AsyncSession):
    stmt = select(Division)
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_category(name: str, division_id: int, description: Optional[str], db: AsyncSession):
    stmt = select(Division).where(Division.division_id == division_id)
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Division not found")

    category = Category(name=name, division_id=division_id, description=description)
    db.add(category)
    return await commit_and_refresh(db, category)


async def list_categories(db: AsyncSession, division_id: Optional[int]):
    stmt = select(Category)
    if division_id:
        stmt = stmt.where(Category.division_id == division_id)
    result = await db.execute(stmt)
    return result.scalars().all()