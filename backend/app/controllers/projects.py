"""
Project controller logic.
"""
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Project, ProjectDetail, ProjectTeam
from app.services.audit import log_action
from app.services.time_utils import utcnow_naive
from app.services.schemas import ProjectCreateRequest, ProjectStatusUpdateRequest, ProjectUpdateRequest
from app.services.realtime import manager


async def create_project(req: ProjectCreateRequest, db: AsyncSession):
    project = Project(
        name=req.name,
        description=req.description,
        created_by=1,
        status="planning",
        workspace_id=req.workspace_id,
    )

    db.add(project)
    await db.flush()

    await log_action(
        db,
        user_id=1,
        action="CREATE",
        resource_type="PROJECT",
        resource_id=project.project_id,
        details=f"Created project: {req.name}",
    )

    if req.team_ids:
        for team_id in req.team_ids:
            db.add(ProjectTeam(project_id=project.project_id, team_id=team_id))

    await db.commit()
    await db.refresh(project)
    return project


async def list_projects(db: AsyncSession, skip: int, limit: int, status_filter: Optional[str], workspace_id: Optional[int]):
    stmt = select(Project)

    if status_filter:
        stmt = stmt.where(Project.status == status_filter)
    if workspace_id:
        stmt = stmt.where(Project.workspace_id == workspace_id)

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_project(project_id: int, db: AsyncSession):
    stmt = select(Project).where(Project.project_id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


async def update_project(project_id: int, req: ProjectUpdateRequest, db: AsyncSession):
    stmt = select(Project).where(and_(Project.project_id == project_id, Project.version == req.version))
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Project not found or version mismatch")

    if req.name:
        project.name = req.name
    if req.description is not None:
        project.description = req.description

    project.version += 1
    project.updated_at = utcnow_naive()
    await db.commit()
    await db.refresh(project)
    return project


async def update_project_status(project_id: int, req: ProjectStatusUpdateRequest, db: AsyncSession):
    stmt = select(Project).where(and_(Project.project_id == project_id, Project.version == req.version))
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Project not found or version mismatch")

    valid_statuses = {"planning", "active", "completed", "archived"}
    if req.status not in valid_statuses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status. Must be one of: {valid_statuses}")

    project.status = req.status
    project.version += 1
    project.updated_at = utcnow_naive()
    await db.commit()
    await db.refresh(project)
    return project


async def link_repository(project_id: int, repository_url: str, repository_type: str, token: Optional[str], db: AsyncSession):
    stmt = select(Project).where(Project.project_id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    project.repository_url = repository_url
    project.repository_type = repository_type
    project.repository_token = token
    project.updated_at = utcnow_naive()
    await db.commit()
    return {"message": "Repository linked successfully"}


async def get_project_details(project_id: int, db: AsyncSession):
    stmt = select(ProjectDetail).where(ProjectDetail.project_id == project_id)
    result = await db.execute(stmt)
    details = result.scalars().all()
    return {"project_id": project_id, "details": details}


async def get_project_teams(project_id: int, db: AsyncSession):
    stmt = select(ProjectTeam).where(ProjectTeam.project_id == project_id)
    result = await db.execute(stmt)
    teams = result.scalars().all()
    return {"project_id": project_id, "teams": teams}


async def list_workspace_projects(workspace_id: int, db: AsyncSession):
    stmt = select(Project).where(Project.workspace_id == workspace_id)
    result = await db.execute(stmt)
    projects = result.scalars().all()
    return {"workspace_id": workspace_id, "projects": projects}