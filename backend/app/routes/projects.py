"""
Project management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, func
from typing import List, Optional
from app.models import Project, ProjectTeam, ProjectDetail, ProjectTask
from app.databases import get_db
from app.services.schemas import ProjectResponse, ProjectCreateRequest, ProjectUpdateRequest, ProjectStatusUpdateRequest
from app.services.audit import log_action, log_field_change
from datetime import datetime, timezone

router = APIRouter(prefix="/projects", tags=["projects"])


async def require_auth():
    """Dependency to check authentication - TODO: Implement token validation"""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )


@router.post("", response_model=ProjectResponse)
async def create_project(
    req: ProjectCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Create a new project
    
    - **name**: Project name (required)
    - **description**: Project description (optional)
    - **workspace_id**: Workspace ID (required)
    - **team_ids**: List of team IDs to associate (optional)
    """
    # Create project
    project = Project(
        name=req.name,
        description=req.description,
        created_by=1,  # TODO: Get from current user
        status="planning",  # Default status
    )
    
    db.add(project)
    await db.flush()  # Get project_id without committing
    
    # Log project creation
    await log_action(
        db,
        user_id=1,  # TODO: Get from current user
        action="CREATE",
        resource_type="PROJECT",
        resource_id=project.project_id,
        details=f"Created project: {req.name}"
    )
    
    # Assign teams if provided
    if req.team_ids:
        for team_id in req.team_ids:
            project_team = ProjectTeam(project_id=project.project_id, team_id=team_id)
            db.add(project_team)
    
    await db.commit()
    await db.refresh(project)
    
    return project


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    workspace_id: Optional[int] = None,
):
    """
    List projects with pagination and filtering
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Number of records to return (max 100)
    - **status**: Filter by status (planning, active, completed, archived)
    - **workspace_id**: Filter by workspace ID
    """
    stmt = select(Project)
    
    # Apply filters
    if status:
        stmt = stmt.where(Project.status == status)
    if workspace_id:
        stmt = stmt.where(Project.workspace_id == workspace_id)
    
    # Apply pagination
    stmt = stmt.offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    projects = result.scalars().all()
    
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get project by ID
    
    - **project_id**: Project ID
    """
    stmt = select(Project).where(Project.project_id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    req: ProjectUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Update project with optimistic locking
    
    - **project_id**: Project ID
    - **name**: New project name
    - **description**: New description
    - **version**: Current version (for optimistic locking)
    """
    stmt = select(Project).where(
        and_(
            Project.project_id == project_id,
            Project.version == req.version
        )
    )
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project not found or version mismatch"
        )
    
    # Update fields
    if req.name:
        project.name = req.name
    if req.description is not None:
        project.description = req.description
    
    # Increment version
    project.version += 1
    project.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(project)
    
    return project


@router.patch("/{project_id}/status", response_model=ProjectResponse)
async def update_project_status(
    project_id: int,
    req: ProjectStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Update project status (planning → active → completed → archived)
    
    - **project_id**: Project ID
    - **status**: New status
    - **version**: Current version for optimistic locking
    """
    stmt = select(Project).where(
        and_(
            Project.project_id == project_id,
            Project.version == req.version
        )
    )
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project not found or version mismatch"
        )
    
    # Validate status transition
    valid_statuses = {"planning", "active", "completed", "archived"}
    if req.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    project.status = req.status
    project.version += 1
    project.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(project)
    
    return project


@router.post("/{project_id}/repository")
async def link_repository(
    project_id: int,
    repository_url: str = Query(...),
    repository_type: str = Query("github"),
    token: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Link Git repository to project
    
    - **project_id**: Project ID
    - **repository_url**: Repository URL
    - **repository_type**: Repository type (github, gitlab, bitbucket)
    - **token**: Access token (optional)
    """
    stmt = select(Project).where(Project.project_id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project.repository_url = repository_url
    project.repository_type = repository_type
    project.repository_token = token
    project.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    
    return {"message": "Repository linked successfully"}


@router.get("/{project_id}/details")
async def get_project_details(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get extended project details
    
    - **project_id**: Project ID
    """
    stmt = select(ProjectDetail).where(ProjectDetail.project_id == project_id)
    result = await db.execute(stmt)
    details = result.scalars().all()
    
    return {"project_id": project_id, "details": details}


@router.get("/{project_id}/team")
async def get_project_teams(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get teams assigned to project
    
    - **project_id**: Project ID
    """
    stmt = select(ProjectTeam).where(ProjectTeam.project_id == project_id)
    result = await db.execute(stmt)
    teams = result.scalars().all()
    
    return {"project_id": project_id, "teams": teams}


@router.get("")
async def list_workspace_projects(
    workspace_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get all projects in a workspace
    
    - **workspace_id**: Workspace ID
    """
    stmt = select(Project).where(Project.workspace_id == workspace_id)
    result = await db.execute(stmt)
    projects = result.scalars().all()
    
    return {"workspace_id": workspace_id, "projects": projects}
