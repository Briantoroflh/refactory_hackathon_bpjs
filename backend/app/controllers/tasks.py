"""
Task controller logic.
"""
from typing import Optional

from fastapi import HTTPException, Query, status
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Project, ProjectTask, ProjectTaskComment, ProjectTaskHistory, ProjectTaskWorkload
from app.services.audit import log_action
from app.services.time_utils import utcnow_naive
from app.services.schemas import (
    ProjectTaskCommentRequest,
    ProjectTaskCreateRequest,
    ProjectTaskStatusUpdateRequest,
    ProjectTaskUpdateRequest,
    ProjectTaskWorkloadRequest,
)
from app.services.realtime import manager


async def create_task(project_id: int, req: ProjectTaskCreateRequest, db: AsyncSession):
    stmt = select(Project).where(Project.project_id == project_id)
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    task = ProjectTask(
        project_id=project_id,
        title=req.title,
        description=req.description,
        story_points=req.story_points,
        assigned_to=req.assigned_to,
        priority=req.priority,
        deadline=req.deadline,
        status="backlog",
        created_by=1,
    )

    db.add(task)
    await db.flush()

    await log_action(
        db,
        user_id=1,
        action="CREATE",
        resource_type="TASK",
        resource_id=task.task_id,
        details=f"Created task: {req.title} in project {project_id}",
    )

    await db.commit()
    await db.refresh(task)
    return task


async def list_tasks(project_id: int, db: AsyncSession, skip: int, limit: int, status_filter: Optional[str], assigned_to: Optional[int], priority: Optional[str]):
    stmt = select(ProjectTask).where(ProjectTask.project_id == project_id)
    if status_filter:
        stmt = stmt.where(ProjectTask.status == status_filter)
    if assigned_to:
        stmt = stmt.where(ProjectTask.assigned_to == assigned_to)
    if priority:
        stmt = stmt.where(ProjectTask.priority == priority)

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_task(project_id: int, task_id: int, db: AsyncSession):
    stmt = select(ProjectTask).where(and_(ProjectTask.task_id == task_id, ProjectTask.project_id == project_id))
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


async def update_task(project_id: int, task_id: int, req: ProjectTaskUpdateRequest, db: AsyncSession):
    stmt = select(ProjectTask).where(and_(ProjectTask.task_id == task_id, ProjectTask.project_id == project_id, ProjectTask.version == req.version))
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Task not found or version mismatch")

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
    task.updated_at = utcnow_naive()
    await db.commit()
    await db.refresh(task)
    return task


async def update_task_status(project_id: int, task_id: int, req: ProjectTaskStatusUpdateRequest, db: AsyncSession):
    stmt = select(ProjectTask).where(and_(ProjectTask.task_id == task_id, ProjectTask.project_id == project_id, ProjectTask.version == req.version))
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Task not found or version mismatch")

    valid_statuses = {"backlog", "in_progress", "in_review", "completed", "closed"}
    if req.status not in valid_statuses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status. Must be one of: {valid_statuses}")

    task.status = req.status
    task.version += 1
    task.updated_at = utcnow_naive()
    await db.commit()
    await db.refresh(task)
    return task


async def update_task_assignee(project_id: int, task_id: int, assigned_to: int, db: AsyncSession):
    stmt = select(ProjectTask).where(and_(ProjectTask.task_id == task_id, ProjectTask.project_id == project_id))
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task.assigned_to = assigned_to
    task.updated_at = utcnow_naive()
    await db.commit()
    return {"message": "Assignee updated"}


async def log_workload(project_id: int, task_id: int, req: ProjectTaskWorkloadRequest, db: AsyncSession):
    stmt = select(ProjectTask).where(and_(ProjectTask.task_id == task_id, ProjectTask.project_id == project_id))
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    workload = ProjectTaskWorkload(
        task_id=task_id,
        worker_id=1,
        work_date=req.work_date,
        hours_worked=req.hours_worked,
        description=req.description,
    )
    db.add(workload)
    await db.commit()
    return {"message": "Worklog recorded successfully"}


async def get_worklog(project_id: int, task_id: int, db: AsyncSession):
    stmt = select(ProjectTaskWorkload).where(ProjectTaskWorkload.task_id == task_id)
    result = await db.execute(stmt)
    worklogs = result.scalars().all()
    return {"task_id": task_id, "worklogs": worklogs}


async def add_comment(project_id: int, task_id: int, req: ProjectTaskCommentRequest, db: AsyncSession):
    stmt = select(ProjectTask).where(and_(ProjectTask.task_id == task_id, ProjectTask.project_id == project_id))
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    comment = ProjectTaskComment(task_id=task_id, user_id=1, content=req.content)
    db.add(comment)
    await db.commit()
    return {"message": "Comment added successfully"}


async def get_comments(project_id: int, task_id: int, db: AsyncSession):
    stmt = select(ProjectTaskComment).where(ProjectTaskComment.task_id == task_id)
    result = await db.execute(stmt)
    comments = result.scalars().all()
    return {"task_id": task_id, "comments": comments}


async def get_task_history(project_id: int, task_id: int, db: AsyncSession):
    stmt = select(ProjectTaskHistory).where(ProjectTaskHistory.task_id == task_id)
    result = await db.execute(stmt)
    history = result.scalars().all()
    return {"task_id": task_id, "history": history}


async def get_task_by_id(task_id: int, db: AsyncSession):
    stmt = select(ProjectTask).where(ProjectTask.task_id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


async def get_assigned_to_me():
    return {"tasks": []}