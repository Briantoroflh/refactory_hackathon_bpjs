"""
Commit tracking and analytics routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.databases import get_db
from app.controllers.commits import (
    correct_commit_attribution as controller_correct_commit_attribution,
    get_commit_statistics as controller_get_commit_statistics,
    get_file_history as controller_get_file_history,
    list_commits as controller_list_commits,
    search_commits as controller_search_commits,
    store_commit as controller_store_commit,
)

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
    return await controller_store_commit(project_id, commit_hash, worker_id, commit_message, commit_date, files_changed, additions, deletions, db)


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
    return await controller_list_commits(project_id, db, skip, limit, worker_id, start_date, end_date)


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
    return await controller_search_commits(db, message_search)


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
    return await controller_get_file_history(project_id, file_path)


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
    return await controller_correct_commit_attribution(commit_id, correct_worker_id, reason, db)


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
    return await controller_get_commit_statistics(project_id, db)
