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
from app.models import Category, Division, Permission, Team, TeamMember, Worker


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


def _member_role_label(role: str) -> str:
    normalized = (role or "").lower()
    if normalized in {"lead", "manager", "admin"}:
        return "Admin"
    if normalized == "member":
        return "Developer"
    return "Viewer"


def _member_status_label(status: str) -> str:
    normalized = (status or "").lower()
    if normalized == "active":
        return "Active"
    if normalized == "on_leave":
        return "Pending"
    return "Inactive"


def _member_avatar(name: str) -> str:
    parts = [part for part in (name or "").split() if part]
    initials = "".join(part[0] for part in parts[:2]).upper()
    return initials or "?"


def _module_name(resource: str) -> str:
    return " ".join(part.capitalize() for part in (resource or "").replace("_", " ").split())


async def get_team_access_control(team_id: Optional[int], db: AsyncSession):
    team_stmt = select(Team).order_by(Team.team_id.asc())
    teams_result = await db.execute(team_stmt)
    teams = list(teams_result.scalars().all())

    if not teams:
        return {
            "team": None,
            "teams": [],
            "members": [],
            "total_members": 0,
            "permissions": [],
            "notice": "No teams available yet.",
        }

    selected_team = next((team for team in teams if team.team_id == team_id), None) if team_id else teams[0]
    notice = None
    if team_id and selected_team is None:
        selected_team = teams[0]
        notice = "Requested team was not found. Showing the first available team instead."

    member_stmt = (
        select(TeamMember, Worker)
        .join(Worker, TeamMember.worker_id == Worker.worker_id)
        .where(TeamMember.team_id == selected_team.team_id)
        .order_by(TeamMember.team_member_id.asc())
    )
    members_result = await db.execute(member_stmt)
    member_rows = members_result.all()

    team_member_counts: dict[int, int] = {}
    count_stmt = select(TeamMember.team_id, TeamMember.team_member_id)
    count_result = await db.execute(count_stmt)
    for team_member_team_id, _ in count_result.all():
        team_member_counts[team_member_team_id] = team_member_counts.get(team_member_team_id, 0) + 1

    permission_stmt = select(Permission).order_by(Permission.resource.asc(), Permission.action.asc())
    permission_result = await db.execute(permission_stmt)
    permissions = permission_result.scalars().all()

    module_permissions = {}
    for permission in permissions:
        key = permission.resource
        module = module_permissions.setdefault(
            key,
            {
                "id": key,
                "name": _module_name(permission.resource),
                "read": False,
                "write": False,
                "delete": False,
            },
        )

        action = (permission.action or "").lower()
        if action == "read":
            module["read"] = True
        elif action in {"create", "update", "write"}:
            module["write"] = True
        elif action == "delete":
            module["delete"] = True

    def build_team_summary(team: Team):
        return {
            "team_id": team.team_id,
            "name": team.name,
            "description": team.description,
            "category_id": team.category_id,
            "status": team.status,
            "capacity_hours": team.capacity_hours,
            "member_count": team_member_counts.get(team.team_id, 0),
        }

    members = []
    for team_member, worker in member_rows:
        members.append(
            {
                "id": str(team_member.team_member_id),
                "name": worker.full_name,
                "email": worker.email,
                "role": _member_role_label(team_member.role),
                "status": _member_status_label(worker.employment_status),
                "avatar": _member_avatar(worker.full_name),
                "joinDate": team_member.join_date,
            }
        )

    return {
        "team": build_team_summary(selected_team),
        "teams": [build_team_summary(team) for team in teams],
        "members": members,
        "total_members": len(members),
        "permissions": list(module_permissions.values()),
        "notice": notice,
    }


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