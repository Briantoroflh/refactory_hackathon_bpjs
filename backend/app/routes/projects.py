"""
Project management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.databases import get_db
from app.controllers.projects import (
    create_project as controller_create_project,
    get_project as controller_get_project,
    get_project_details as controller_get_project_details,
    get_project_teams as controller_get_project_teams,
    list_projects as controller_list_projects,
    list_workspace_projects as controller_list_workspace_projects,
    link_repository as controller_link_repository,
    update_project as controller_update_project,
    update_project_status as controller_update_project_status,
)
from app.services.schemas import ProjectResponse, ProjectCreateRequest, ProjectUpdateRequest, ProjectStatusUpdateRequest

router = APIRouter(prefix="/projects", tags=["projects"])


from app.routes.dependencies import require_auth



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
    return await controller_create_project(req, db)


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
    return await controller_list_projects(db, skip, limit, status, workspace_id)


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
    return await controller_get_project(project_id, db)


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
    return await controller_update_project(project_id, req, db)


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
    return await controller_update_project_status(project_id, req, db)


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
    return await controller_link_repository(project_id, repository_url, repository_type, token, db)


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
    return await controller_get_project_details(project_id, db)


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
    return await controller_get_project_teams(project_id, db)


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
    return await controller_list_workspace_projects(workspace_id, db)
