"""
Task management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, func
from typing import List, Optional
from app.models import (
    ProjectTask,
    ProjectTaskWorkload,
    ProjectTaskComment,
    ProjectTaskHistory,
    Project,
)
from app.databases import get_db
from app.services.schemas import (
    ProjectTaskResponse,
    ProjectTaskCreateRequest,
    ProjectTaskUpdateRequest,
    ProjectTaskStatusUpdateRequest,
    ProjectTaskWorkloadRequest,
    ProjectTaskCommentRequest,
)
from app.services.audit import log_action, log_field_change
from datetime import datetime, timezone

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
    # Verify project exists
    stmt = select(Project).where(Project.project_id == project_id)
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    task = ProjectTask(
        project_id=project_id,
        title=req.title,
        description=req.description,
        story_points=req.story_points,
        assigned_to=req.assigned_to,
        priority=req.priority,
        deadline=req.deadline,
        status="backlog",
        created_by=1,  # TODO: Get from current user
    )
    
    db.add(task)
    await db.flush()
    
    # Log task creation
    await log_action(
        db,
        user_id=1,  # TODO: Get from current user
        action="CREATE",
        resource_type="TASK",
        resource_id=task.task_id,
        details=f"Created task: {req.title} in project {project_id}"
    )
    
    await db.commit()
    await db.refresh(task)
    
    return task


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
    stmt = select(ProjectTask).where(ProjectTask.project_id == project_id)
    
    if status:
        stmt = stmt.where(ProjectTask.status == status)
    if assigned_to:
        stmt = stmt.where(ProjectTask.assigned_to == assigned_to)
    if priority:
        stmt = stmt.where(ProjectTask.priority == priority)
    
    stmt = stmt.offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    tasks = result.scalars().all()
    
    return tasks


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
    stmt = select(ProjectTask).where(
        and_(
            ProjectTask.task_id == task_id,
            ProjectTask.project_id == project_id
        )
    )
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task


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
    stmt = select(ProjectTask).where(
        and_(
            ProjectTask.task_id == task_id,
            ProjectTask.project_id == project_id,
            ProjectTask.version == req.version
        )
    )
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task not found or version mismatch"
        )
    
    # Update fields
    if req.title:
        task.title = req.title
    if req.description is not None:
        task.description = req.description
    if req.story_points:
        task.story_points = req.story_points
    if req.priority:
        task.priority = req.priority
    if req.deadline:
        task.deadline = req.deadline
    
    task.version += 1
    task.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(task)
    
    return task


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
    stmt = select(ProjectTask).where(
        and_(
            ProjectTask.task_id == task_id,
            ProjectTask.project_id == project_id,
            ProjectTask.version == req.version
        )
    )
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task not found or version mismatch"
        )
    
    valid_statuses = {"backlog", "in_progress", "in_review", "completed", "closed"}
    if req.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    task.status = req.status
    task.version += 1
    task.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(task)
    
    return task


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
    stmt = select(ProjectTask).where(
        and_(
            ProjectTask.task_id == task_id,
            ProjectTask.project_id == project_id
        )
    )
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task.assigned_to = assigned_to
    task.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    
    return {"message": "Assignee updated"}


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
    # Verify task exists
    stmt = select(ProjectTask).where(
        and_(
            ProjectTask.task_id == task_id,
            ProjectTask.project_id == project_id
        )
    )
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    workload = ProjectTaskWorkload(
        task_id=task_id,
        worker_id=1,  # TODO: Get from current user
        work_date=req.work_date,
        hours_worked=req.hours_worked,
        description=req.description,
    )
    
    db.add(workload)
    await db.commit()
    
    return {"message": "Worklog recorded successfully"}


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
    stmt = select(ProjectTaskWorkload).where(ProjectTaskWorkload.task_id == task_id)
    result = await db.execute(stmt)
    worklogs = result.scalars().all()
    
    return {"task_id": task_id, "worklogs": worklogs}


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
    # Verify task exists
    stmt = select(ProjectTask).where(
        and_(
            ProjectTask.task_id == task_id,
            ProjectTask.project_id == project_id
        )
    )
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    comment = ProjectTaskComment(
        task_id=task_id,
        user_id=1,  # TODO: Get from current user
        content=req.content,
    )
    
    db.add(comment)
    await db.commit()
    
    return {"message": "Comment added successfully"}


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
    stmt = select(ProjectTaskComment).where(ProjectTaskComment.task_id == task_id)
    result = await db.execute(stmt)
    comments = result.scalars().all()
    
    return {"task_id": task_id, "comments": comments}


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
    stmt = select(ProjectTaskHistory).where(ProjectTaskHistory.task_id == task_id)
    result = await db.execute(stmt)
    history = result.scalars().all()
    
    return {"task_id": task_id, "history": history}


# Additional route for assigned tasks
tasks_assigned_router = APIRouter(prefix="/tasks", tags=["tasks"])


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
    # Placeholder - needs current user context from JWT
    return {"tasks": []}
