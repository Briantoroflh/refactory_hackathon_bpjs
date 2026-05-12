"""
Commit tracking and analytics routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, func, or_
from typing import Optional
from app.models import ProjectCommitTracking, CommitChangeLogs, ProjectTask
from app.databases import get_db
from datetime import datetime, timezone

router = APIRouter(tags=["commits"])


async def require_auth():
    """Dependency to check authentication"""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )


@router.post("/projects/{project_id}/commits")
async def store_commit(
    project_id: int,
    commit_hash: str = Query(...),
    worker_id: int = Query(...),
    commit_message: str = Query(...),
    commit_date: str = Query(...),
    files_changed: int = Query(0),
    additions: int = Query(0),
    deletions: int = Query(0),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Store commit data for a project
    
    - **project_id**: Project ID
    - **commit_hash**: Unique commit hash
    - **worker_id**: Worker ID who made the commit
    - **commit_message**: Commit message
    - **commit_date**: Commit date (ISO format)
    - **files_changed**: Number of files changed
    - **additions**: Lines added
    - **deletions**: Lines deleted
    """
    # Check for duplicate commit
    stmt = select(ProjectCommitTracking).where(
        ProjectCommitTracking.commit_hash == commit_hash
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Commit already recorded"
        )
    
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


@router.get("/projects/{project_id}/commits")
async def list_commits(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    worker_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """
    Get commits for project with filtering
    
    - **project_id**: Project ID
    - **skip**: Pagination offset
    - **limit**: Max records
    - **worker_id**: Filter by worker
    - **start_date**: Filter from date (ISO format)
    - **end_date**: Filter to date (ISO format)
    """
    stmt = select(ProjectCommitTracking).where(
        ProjectCommitTracking.project_id == project_id
    )
    
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


@router.get("/commits")
async def search_commits(
    message_search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Search commits by message across all projects
    
    - **message_search**: Search term for commit message
    """
    stmt = select(ProjectCommitTracking)
    
    if message_search:
        stmt = stmt.where(
            ProjectCommitTracking.commit_message.ilike(f"%{message_search}%")
        )
    
    stmt = stmt.limit(100)
    
    result = await db.execute(stmt)
    commits = result.scalars().all()
    
    return {"commits": commits}


@router.get("/projects/{project_id}/commits/file/{file_path:path}")
async def get_file_history(
    project_id: int,
    file_path: str,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get commit history for specific file
    
    - **project_id**: Project ID
    - **file_path**: File path to search
    """
    # TODO: Implement file-level tracking
    # This requires storing file paths in commits table
    return {
        "project_id": project_id,
        "file_path": file_path,
        "commits": []
    }


@router.post("/commits/{commit_id}/attribution")
async def correct_commit_attribution(
    commit_id: int,
    correct_worker_id: int = Query(...),
    reason: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Correct attribution of commit to different worker
    
    - **commit_id**: Commit ID to correct
    - **correct_worker_id**: Correct worker ID
    - **reason**: Reason for correction
    """
    stmt = select(ProjectCommitTracking).where(
        ProjectCommitTracking.commit_id == commit_id
    )
    result = await db.execute(stmt)
    commit = result.scalar_one_or_none()
    
    if not commit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commit not found"
        )
    
    # Log the change
    change_log = CommitChangeLogs(
        commit_id=commit_id,
        field_name="worker_id",
        old_value=str(commit.worker_id),
        new_value=str(correct_worker_id),
        changed_by_user_id=1,  # TODO: Get from current user
        change_reason=reason,
    )
    
    db.add(change_log)
    commit.worker_id = correct_worker_id
    
    await db.commit()
    
    return {"message": "Commit attribution corrected"}


@router.get("/projects/{project_id}/commit-stats")
async def get_commit_statistics(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get commit statistics for project
    
    - **project_id**: Project ID
    
    Returns:
    - Total commits
    - Commits by worker
    - Total lines changed
    - Commit frequency
    """
    # Total commits
    stmt = select(func.count(ProjectCommitTracking.commit_id)).where(
        ProjectCommitTracking.project_id == project_id
    )
    result = await db.execute(stmt)
    total_commits = result.scalar() or 0
    
    # Total lines changed
    stmt = select(
        func.sum(ProjectCommitTracking.additions),
        func.sum(ProjectCommitTracking.deletions)
    ).where(ProjectCommitTracking.project_id == project_id)
    result = await db.execute(stmt)
    row = result.first()
    total_additions = row[0] or 0
    total_deletions = row[1] or 0
    
    return {
        "project_id": project_id,
        "total_commits": total_commits,
        "total_additions": total_additions,
        "total_deletions": total_deletions,
        "files_changed_avg": 0,  # TODO: Calculate average
    }
