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


# ============================================================================
# GitLab Commits Controller - for GitLab integration commit queries
# ============================================================================

import logging
from datetime import timedelta
from app.models.gitlab import GitLabRepository, Commit
from app.models import Project, User

logger = logging.getLogger(__name__)


class GitLabCommitsController:
    """Controller for GitLab commit queries and filtering."""

    @staticmethod
    async def list_gitlab_commits(
        project_id: Optional[int] = None,
        days: int = 30,
        author_email: Optional[str] = None,
        branch: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = None,
        current_user: User = None,
    ) -> dict:
        """List GitLab commits with optional filtering."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # Build query
            stmt = select(Commit)

            if project_id:
                # Get repository for project
                repo_stmt = select(GitLabRepository).where(
                    GitLabRepository.project_id == project_id
                )
                repo_result = await db.execute(repo_stmt)
                repository = repo_result.scalars().first()

                if not repository:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="No GitLab repository linked to this project",
                    )

                stmt = stmt.where(Commit.repository_id == repository.id)

            # Apply filters
            stmt = stmt.where(Commit.committed_at >= cutoff_date)

            if author_email:
                stmt = stmt.where(Commit.author_email == author_email)

            if branch:
                stmt = stmt.where(Commit.branch == branch)

            # Count total
            from sqlalchemy import and_
            count_stmt = select(func.count()).select_from(Commit)
            if project_id:
                count_stmt = count_stmt.where(Commit.repository_id == repository.id)
            count_stmt = count_stmt.where(Commit.committed_at >= cutoff_date)
            if author_email:
                count_stmt = count_stmt.where(Commit.author_email == author_email)
            if branch:
                count_stmt = count_stmt.where(Commit.branch == branch)

            count_result = await db.execute(count_stmt)
            total = count_result.scalar()

            # Pagination and sorting
            stmt = stmt.order_by(Commit.committed_at.desc()).offset(skip).limit(limit)

            result = await db.execute(stmt)
            commits = result.scalars().all()

            return {
                "total": total,
                "skip": skip,
                "limit": limit,
                "commits": [
                    {
                        "id": c.id,
                        "git_hash": c.git_hash,
                        "author_name": c.author_name,
                        "author_email": c.author_email,
                        "message": c.message,
                        "committed_at": c.committed_at.isoformat(),
                        "branch": c.branch,
                        "created_at": c.created_at.isoformat(),
                    }
                    for c in commits
                ],
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error listing GitLab commits: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list commits",
            )

    @staticmethod
    async def get_gitlab_commit_stats(
        project_id: int,
        days: int = 30,
        db: AsyncSession = None,
        current_user: User = None,
    ) -> dict:
        """Get aggregated commit statistics for a project."""
        try:
            from sqlalchemy import and_
            # Get repository
            repo_stmt = select(GitLabRepository).where(
                GitLabRepository.project_id == project_id
            )
            repo_result = await db.execute(repo_stmt)
            repository = repo_result.scalars().first()

            if not repository:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No GitLab repository linked to this project",
                )

            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # Total commits
            total_stmt = select(func.count()).select_from(Commit).where(
                and_(
                    Commit.repository_id == repository.id,
                    Commit.committed_at >= cutoff_date,
                )
            )
            total_result = await db.execute(total_stmt)
            total_commits = total_result.scalar()

            # Unique contributors
            unique_authors_stmt = (
                select(func.count(func.distinct(Commit.author_email)))
                .select_from(Commit)
                .where(
                    and_(
                        Commit.repository_id == repository.id,
                        Commit.committed_at >= cutoff_date,
                    )
                )
            )
            unique_result = await db.execute(unique_authors_stmt)
            unique_contributors = unique_result.scalar()

            # Commits by branch
            branch_stmt = (
                select(Commit.branch, func.count(Commit.id).label("count"))
                .where(
                    and_(
                        Commit.repository_id == repository.id,
                        Commit.committed_at >= cutoff_date,
                    )
                )
                .group_by(Commit.branch)
                .order_by(func.count(Commit.id).desc())
            )
            branch_result = await db.execute(branch_stmt)
            branch_data = branch_result.all()

            # Top contributors
            contributors_stmt = (
                select(
                    Commit.author_name,
                    Commit.author_email,
                    func.count(Commit.id).label("count"),
                )
                .where(
                    and_(
                        Commit.repository_id == repository.id,
                        Commit.committed_at >= cutoff_date,
                    )
                )
                .group_by(Commit.author_email, Commit.author_name)
                .order_by(func.count(Commit.id).desc())
                .limit(10)
            )
            contributors_result = await db.execute(contributors_stmt)
            contributors_data = contributors_result.all()

            return {
                "project_id": project_id,
                "period_days": days,
                "total_commits": total_commits,
                "unique_contributors": unique_contributors,
                "commits_per_day": round(total_commits / days, 2) if days > 0 else 0,
                "branches": [
                    {"name": b[0], "commits": b[1]}
                    for b in branch_data
                ],
                "top_contributors": [
                    {
                        "name": c[0],
                        "email": c[1],
                        "commits": c[2],
                    }
                    for c in contributors_data
                ],
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting GitLab commit stats: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get commit statistics",
            )
