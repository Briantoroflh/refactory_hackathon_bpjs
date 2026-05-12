"""
GitLab commit synchronization service.
Handles periodic sync of commits from linked repositories.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.gitlab import GitLabRepository, Commit
from app.models.audit import AuditSystemLog
from app.services.gitlab_client import GitLabClientFactory
from app.services.token_encryption import get_encryption_helper
from gitlab.exceptions import GitlabError

logger = logging.getLogger(__name__)


class CommitSyncService:
    """
    Service for synchronizing commits from GitLab repositories to the database.
    Implements incremental sync with checkpoint-based tracking.
    """

    BATCH_SIZE = 500  # Insert commits in batches

    @staticmethod
    async def sync_all_repositories(
        session: AsyncSession,
        gitlab_url: str,
        lookback_days: int = 90,
    ) -> Tuple[int, int, str]:
        """
        Synchronize all linked GitLab repositories.

        Args:
            session: AsyncSession for database operations
            gitlab_url: GitLab instance URL
            lookback_days: Days to look back on first sync (default: 90)

        Returns:
            Tuple of (total_commits_synced, errors_count, status_message)
        """
        try:
            # Fetch all linked repositories
            stmt = select(GitLabRepository)
            result = await session.execute(stmt)
            repositories = result.scalars().all()

            if not repositories:
                logger.info("No GitLab repositories linked for sync")
                return 0, 0, "No repositories to sync"

            total_synced = 0
            total_errors = 0
            start_time = datetime.utcnow()

            for repo in repositories:
                try:
                    synced, errors = await CommitSyncService.sync_repository(
                        session,
                        repo,
                        gitlab_url,
                        lookback_days,
                    )
                    total_synced += synced
                    total_errors += errors

                except Exception as e:
                    logger.error(f"Error syncing repository {repo.id}: {str(e)}")
                    total_errors += 1
                    await CommitSyncService._audit_sync_error(
                        session, repo.id, str(e)
                    )

            duration_seconds = (datetime.utcnow() - start_time).total_seconds()

            # Audit successful sync
            audit_entry = AuditSystemLog(
                action="gitlab_sync_completed",
                resource_type="gitlab_repository",
                field_name="commits_synced",
                new_value=str(total_synced),
                severity="info" if total_errors == 0 else "warning",
                details={
                    "total_synced": total_synced,
                    "total_errors": total_errors,
                    "duration_seconds": int(duration_seconds),
                    "repositories_synced": len(repositories),
                },
            )
            session.add(audit_entry)
            await session.commit()

            status_msg = (
                f"Synced {total_synced} commits from {len(repositories)} repositories "
                f"in {duration_seconds:.1f}s"
            )
            if total_errors > 0:
                status_msg += f" ({total_errors} errors)"

            logger.info(status_msg)
            return total_synced, total_errors, status_msg

        except Exception as e:
            logger.error(f"Fatal error during sync_all_repositories: {str(e)}")
            raise

    @staticmethod
    async def sync_repository(
        session: AsyncSession,
        repository: GitLabRepository,
        gitlab_url: str,
        lookback_days: int = 90,
    ) -> Tuple[int, int]:
        """
        Synchronize a single GitLab repository.

        Args:
            session: AsyncSession for database operations
            repository: GitLabRepository model instance
            gitlab_url: GitLab instance URL
            lookback_days: Days to look back on first sync

        Returns:
            Tuple of (commits_synced, errors_count)
        """
        try:
            # Create GitLab client
            client = GitLabClientFactory.create_client(
                gitlab_url, get_encryption_helper().decrypt(repository.gitlab_access_token)
            )

            # Determine sync period
            if repository.last_sync_timestamp:
                since = repository.last_sync_timestamp
            else:
                # First sync: look back N days
                since = datetime.utcnow() - timedelta(days=lookback_days)

            until = datetime.utcnow()

            logger.info(
                f"Starting sync for repository {repository.id} "
                f"(GitLab project {repository.gitlab_project_id}) "
                f"from {since.isoformat()} to {until.isoformat()}"
            )

            # Fetch commits from GitLab
            commits_data = client.fetch_commits(
                repository.gitlab_project_id,
                since=since,
                until=until,
                branch="main",
            )

            if not commits_data:
                logger.info(f"No new commits for repository {repository.id}")
                repository.last_sync_timestamp = datetime.utcnow()
                session.add(repository)
                await session.commit()
                return 0, 0

            # Insert commits in batches
            commits_synced = 0
            sync_errors = 0

            for i in range(0, len(commits_data), CommitSyncService.BATCH_SIZE):
                batch = commits_data[i : i + CommitSyncService.BATCH_SIZE]

                try:
                    await CommitSyncService._insert_commit_batch(
                        session, repository.id, batch
                    )
                    commits_synced += len(batch)
                except Exception as e:
                    logger.error(f"Error inserting commit batch: {str(e)}")
                    sync_errors += len(batch)

            # Update last sync timestamp
            repository.last_sync_timestamp = datetime.utcnow()
            session.add(repository)
            await session.commit()

            logger.info(
                f"Synced {commits_synced} commits for repository {repository.id} "
                f"({sync_errors} errors)"
            )

            return commits_synced, sync_errors

        except GitlabError as e:
            logger.error(f"GitLab API error syncing repository {repository.id}: {str(e)}")
            await CommitSyncService._audit_sync_error(
                session, repository.id, f"GitLab API error: {str(e)}"
            )
            return 0, 1
        except Exception as e:
            logger.error(f"Unexpected error syncing repository {repository.id}: {str(e)}")
            await CommitSyncService._audit_sync_error(
                session, repository.id, str(e)
            )
            return 0, 1

    @staticmethod
    async def _insert_commit_batch(
        session: AsyncSession, repository_id: int, commits: list
    ) -> None:
        """
        Insert a batch of commits, skipping duplicates.

        Args:
            session: AsyncSession for database operations
            repository_id: GitLabRepository ID
            commits: List of commit data dictionaries
        """
        for commit_data in commits:
            # Check if commit already exists
            stmt = select(Commit).where(
                and_(
                    Commit.repository_id == repository_id,
                    Commit.git_hash == commit_data["hash"],
                )
            )
            result = await session.execute(stmt)
            if result.scalars().first():
                logger.debug(
                    f"Skipping duplicate commit {commit_data['hash']}"
                )
                continue

            # Create new commit record
            commit = Commit(
                repository_id=repository_id,
                git_hash=commit_data["hash"],
                author_name=commit_data["author_name"],
                author_email=commit_data["author_email"],
                message=commit_data["message"],
                committed_at=commit_data["committed_date"],
                branch=commit_data["branch"],
            )
            session.add(commit)

        await session.commit()

    @staticmethod
    async def _audit_sync_error(
        session: AsyncSession, repository_id: int, error_message: str
    ) -> None:
        """
        Audit a synchronization error.

        Args:
            session: AsyncSession for database operations
            repository_id: GitLabRepository ID
            error_message: Error description
        """
        try:
            audit_entry = AuditSystemLog(
                action="gitlab_sync_failed",
                resource_type="gitlab_repository",
                resource_id=repository_id,
                new_value=error_message,
                severity="warning",
            )
            session.add(audit_entry)
            await session.commit()
        except Exception as e:
            logger.error(f"Failed to audit sync error: {str(e)}")
