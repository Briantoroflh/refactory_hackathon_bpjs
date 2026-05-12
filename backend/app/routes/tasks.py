"""
Task management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.databases import get_db
from app.controllers.tasks import (
    add_comment as controller_add_comment,
    create_task as controller_create_task,
    get_assigned_to_me as controller_get_assigned_to_me,
    get_comments as controller_get_comments,
    get_task as controller_get_task,
    get_task_by_id as controller_get_task_by_id,
    get_task_history as controller_get_task_history,
    get_worklog as controller_get_worklog,
    list_tasks as controller_list_tasks,
    log_workload as controller_log_workload,
    update_task as controller_update_task,
    update_task_assignee as controller_update_task_assignee,
    update_task_status as controller_update_task_status,
)
from app.services.schemas import (
    ProjectTaskResponse,
    ProjectTaskCreateRequest,
    ProjectTaskUpdateRequest,
    ProjectTaskStatusUpdateRequest,
    ProjectTaskWorkloadRequest,
    ProjectTaskCommentRequest,
)

router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["tasks"])


async def require_auth():
    """Dependency to check authentication - TODO: Implement token validation"""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )


@router.post("", response_model=ProjectTaskResponse)
async def create_task(
    project_id: int,
    req: ProjectTaskCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Create a new task in project
    
    - **project_id**: Project ID
    - **title**: Task title (required)
    - **description**: Task description
    - **story_points**: Story points (1-21)
    - **assigned_to**: User ID to assign task
    - **priority**: Priority level (high, medium, low)
    - **deadline**: Deadline date (ISO format)
    """
    return await controller_create_task(project_id, req, db)


@router.get("", response_model=List[ProjectTaskResponse])
async def list_tasks(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    assigned_to: Optional[int] = None,
    priority: Optional[str] = None,
):
    """
    List tasks with pagination and filtering
    
    - **project_id**: Project ID
    - **skip**: Pagination offset
    - **limit**: Max records (1-100)
    - **status**: Filter by status
    - **assigned_to**: Filter by assignee
    - **priority**: Filter by priority
    """
    return await controller_list_tasks(project_id, db, skip, limit, status, assigned_to, priority)


@router.get("/{task_id}", response_model=ProjectTaskResponse)
async def get_task(
    project_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get task by ID
    
    - **project_id**: Project ID
    - **task_id**: Task ID
    """
    return await controller_get_task(project_id, task_id, db)


@router.put("/{task_id}", response_model=ProjectTaskResponse)
async def update_task(
    project_id: int,
    task_id: int,
    req: ProjectTaskUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Update task with optimistic locking
    
    - **project_id**: Project ID
    - **task_id**: Task ID
    - **version**: Current version (for optimistic locking)
    """
    return await controller_update_task(project_id, task_id, req, db)


@router.patch("/{task_id}/status", response_model=ProjectTaskResponse)
async def update_task_status(
    project_id: int,
    task_id: int,
    req: ProjectTaskStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Update task status
    
    - **project_id**: Project ID
    - **task_id**: Task ID
    - **status**: New status (backlog, in_progress, in_review, completed, closed)
    - **version**: Current version
    """
    return await controller_update_task_status(project_id, task_id, req, db)


@router.patch("/{task_id}/assignee")
async def update_task_assignee(
    project_id: int,
    task_id: int,
    assigned_to: int = Query(...),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Update task assignee
    
    - **project_id**: Project ID
    - **task_id**: Task ID
    - **assigned_to**: New assignee user ID
    """
    return await controller_update_task_assignee(project_id, task_id, assigned_to, db)


@router.post("/{task_id}/worklog")
async def log_workload(
    project_id: int,
    task_id: int,
    req: ProjectTaskWorkloadRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Log work hours on task
    
    - **project_id**: Project ID
    - **task_id**: Task ID
    - **work_date**: Work date (ISO format)
    - **hours_worked**: Hours worked (0-24)
    - **description**: Work description
    """
    return await controller_log_workload(project_id, task_id, req, db)


@router.get("/{task_id}/worklog")
async def get_worklog(
    project_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get work logs for task
    
    - **project_id**: Project ID
    - **task_id**: Task ID
    """
    return await controller_get_worklog(project_id, task_id, db)


@router.post("/{task_id}/comments")
async def add_comment(
    project_id: int,
    task_id: int,
    req: ProjectTaskCommentRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Add comment to task
    
    - **project_id**: Project ID
    - **task_id**: Task ID
    - **content**: Comment content
    """
    return await controller_add_comment(project_id, task_id, req, db)


@router.get("/{task_id}/comments")
async def get_comments(
    project_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get comments for task
    
    - **project_id**: Project ID
    - **task_id**: Task ID
    """
    return await controller_get_comments(project_id, task_id, db)


@router.get("/{task_id}/history")
async def get_task_history(
    project_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get change history for task
    
    - **project_id**: Project ID
    - **task_id**: Task ID
    """
    return await controller_get_task_history(project_id, task_id, db)


# Additional route for assigned tasks
tasks_assigned_router = APIRouter(prefix="/tasks", tags=["tasks"])


@tasks_assigned_router.get("/{task_id}", response_model=ProjectTaskResponse)
async def get_task_by_id(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get task by ID without requiring the project route prefix.
    """
    return await controller_get_task_by_id(task_id, db)


@tasks_assigned_router.get("/assigned-to-me")
async def get_assigned_to_me(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Get all tasks assigned to current user
    
    - **skip**: Pagination offset
    - **limit**: Max records
    
    TODO: Filter by current user from JWT token
    """
    return await controller_get_assigned_to_me()
