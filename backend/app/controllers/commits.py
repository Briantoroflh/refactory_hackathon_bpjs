"""
Commit controller logic.
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import CommitChangeLogs, ProjectCommitTracking


async def store_commit(project_id: int, commit_hash: str, worker_id: int, commit_message: str, commit_date: str, files_changed: int, additions: int, deletions: int, db: AsyncSession):
    stmt = select(ProjectCommitTracking).where(ProjectCommitTracking.commit_hash == commit_hash)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Commit already recorded")

    commit = ProjectCommitTracking(
        project_id=project_id,
        commit_hash=commit_hash,
        worker_id=worker_id,
        commit_message=commit_message,
        commit_date=commit_date,
        files_changed=files_changed,
        additions=additions,
        deletions=deletions,
    )
    db.add(commit)
    await db.commit()
    await db.refresh(commit)
    return commit


async def list_commits(project_id: int, db: AsyncSession, skip: int, limit: int, worker_id: Optional[int], start_date: Optional[str], end_date: Optional[str]):
    stmt = select(ProjectCommitTracking).where(ProjectCommitTracking.project_id == project_id)
    if worker_id:
        stmt = stmt.where(ProjectCommitTracking.worker_id == worker_id)
    if start_date:
        stmt = stmt.where(ProjectCommitTracking.commit_date >= start_date)
    if end_date:
        stmt = stmt.where(ProjectCommitTracking.commit_date <= end_date)
    stmt = stmt.offset(skip).limit(limit).order_by(ProjectCommitTracking.commit_date.desc())
    result = await db.execute(stmt)
    commits = result.scalars().all()
    return {"project_id": project_id, "commits": commits}


async def search_commits(db: AsyncSession, message_search: Optional[str]):
    stmt = select(ProjectCommitTracking)
    if message_search:
        stmt = stmt.where(ProjectCommitTracking.commit_message.ilike(f"%{message_search}%"))
    stmt = stmt.limit(100)
    result = await db.execute(stmt)
    commits = result.scalars().all()
    return {"commits": commits}


async def get_file_history(project_id: int, file_path: str):
    return {"project_id": project_id, "file_path": file_path, "commits": []}


async def correct_commit_attribution(commit_id: int, correct_worker_id: int, reason: Optional[str], db: AsyncSession):
    stmt = select(ProjectCommitTracking).where(ProjectCommitTracking.commit_id == commit_id)
    result = await db.execute(stmt)
    commit = result.scalar_one_or_none()
    if not commit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commit not found")

    change_log = CommitChangeLogs(
        commit_id=commit_id,
        field_name="worker_id",
        old_value=str(commit.worker_id),
        new_value=str(correct_worker_id),
        changed_by_user_id=1,
        change_reason=reason,
    )

    db.add(change_log)
    commit.worker_id = correct_worker_id
    await db.commit()
    return {"message": "Commit attribution corrected"}


async def get_commit_statistics(project_id: int, db: AsyncSession):
    stmt = select(func.count(ProjectCommitTracking.commit_id)).where(ProjectCommitTracking.project_id == project_id)
    result = await db.execute(stmt)
    total_commits = result.scalar() or 0

    stmt = select(func.sum(ProjectCommitTracking.additions), func.sum(ProjectCommitTracking.deletions)).where(ProjectCommitTracking.project_id == project_id)
    result = await db.execute(stmt)
    row = result.first()
    total_additions = row[0] or 0
    total_deletions = row[1] or 0

    return {
        "project_id": project_id,
        "total_commits": total_commits,
        "total_additions": total_additions,
        "total_deletions": total_deletions,
        "files_changed_avg": 0,
    }