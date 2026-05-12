"""
Controller for GitLab repository management endpoints.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.common import get_db
from app.models import Project, User
from app.models.gitlab import GitLabRepository, Commit
from app.services.gitlab_client import GitLabClientFactory
from app.services.commit_sync import CommitSyncService
from app.services.token_encryption import get_encryption_helper
from app.controllers.auth import get_current_user
from gitlab.exceptions import GitlabError

logger = logging.getLogger(__name__)


class GitLabRepositoryController:
    """Controller for GitLab repository linking and management."""

    @staticmethod
    async def link_repository(
        project_id: int,
        gitlab_project_id: int,
        gitlab_url: str,
        gitlab_token: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> dict:
        """
        Link a GitLab repository to a project.

        Args:
            project_id: Platform project ID
            gitlab_project_id: GitLab project ID
            gitlab_url: GitLab instance URL
            gitlab_token: GitLab personal access token
            db: Database session
            current_user: Current authenticated user

        Returns:
            Repository metadata
        """
        try:
            # Verify project exists and user has permission
            project = await db.get(Project, project_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found",
                )

            # Check if repository is already linked
            from sqlalchemy import select
            stmt = select(GitLabRepository).where(
                GitLabRepository.project_id == project_id
            )
            result = await db.execute(stmt)
            if result.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Project already linked to a GitLab repository",
                )

            # Validate GitLab credentials
            try:
                client = GitLabClientFactory.create_client(gitlab_url, gitlab_token)
                metadata = client.get_repository_metadata(gitlab_project_id)
            except GitlabError as e:
                logger.error(f"Failed to validate GitLab credentials: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid GitLab credentials or project not found",
                )

            # Create repository record
            repository = GitLabRepository(
                project_id=project_id,
                gitlab_project_id=gitlab_project_id,
                gitlab_url=gitlab_url,
                gitlab_access_token=get_encryption_helper().encrypt(gitlab_token),
            )
            db.add(repository)
            await db.commit()
            await db.refresh(repository)

            # Audit log
            from app.models.audit import AuditSystemLog
            audit_entry = AuditSystemLog(
                action="gitlab_repository_linked",
                resource_type="gitlab_repository",
                resource_id=repository.id,
                changed_by=current_user.user_id if hasattr(current_user, "user_id") else None,
                new_value=f"Linked GitLab project {gitlab_project_id} to project {project_id}",
                severity="info",
            )
            db.add(audit_entry)
            await db.commit()

            logger.info(f"Linked repository {repository.id} to project {project_id}")

            return {
                "id": repository.id,
                "project_id": repository.project_id,
                "gitlab_project_id": repository.gitlab_project_id,
                "gitlab_url": repository.gitlab_url,
                "repository_name": metadata.get("name"),
                "repository_url": metadata.get("url"),
                "last_sync": repository.last_sync_timestamp,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error linking repository: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to link repository",
            )

    @staticmethod
    async def get_repository(
        project_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> dict:
        """
        Get metadata for a project's linked GitLab repository.

        Args:
            project_id: Platform project ID
            db: Database session
            current_user: Current authenticated user

        Returns:
            Repository metadata
        """
        try:
            from sqlalchemy import select
            stmt = select(GitLabRepository).where(
                GitLabRepository.project_id == project_id
            )
            result = await db.execute(stmt)
            repository = result.scalars().first()

            if not repository:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No GitLab repository linked to this project",
                )

            return {
                "id": repository.id,
                "project_id": repository.project_id,
                "gitlab_project_id": repository.gitlab_project_id,
                "gitlab_url": repository.gitlab_url,
                "last_sync": repository.last_sync_timestamp,
                "created_at": repository.created_at,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting repository metadata: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get repository metadata",
            )

    @staticmethod
    async def unlink_repository(
        project_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> dict:
        """
        Unlink a GitLab repository from a project.

        Args:
            project_id: Platform project ID
            db: Database session
            current_user: Current authenticated user

        Returns:
            Confirmation message
        """
        try:
            from sqlalchemy import select
            stmt = select(GitLabRepository).where(
                GitLabRepository.project_id == project_id
            )
            result = await db.execute(stmt)
            repository = result.scalars().first()

            if not repository:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No GitLab repository linked to this project",
                )

            # Delete repository and associated commits
            await db.delete(repository)
            await db.commit()

            # Audit log
            from app.models.audit import AuditSystemLog
            audit_entry = AuditSystemLog(
                action="gitlab_repository_unlinked",
                resource_type="gitlab_repository",
                resource_id=repository.id,
                changed_by=current_user.user_id if hasattr(current_user, "user_id") else None,
                old_value=f"Linked GitLab project {repository.gitlab_project_id} to project {project_id}",
                severity="info",
            )
            db.add(audit_entry)
            await db.commit()

            logger.info(f"Unlinked repository {repository.id} from project {project_id}")

            return {"message": "Repository unlinked successfully"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error unlinking repository: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to unlink repository",
            )

    @staticmethod
    async def trigger_manual_sync(
        project_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> dict:
        """
        Trigger manual synchronization of commits for a project.

        Args:
            project_id: Platform project ID
            db: Database session
            current_user: Current authenticated user

        Returns:
            Sync result
        """
        try:
            # Get repository
            from sqlalchemy import select
            stmt = select(GitLabRepository).where(
                GitLabRepository.project_id == project_id
            )
            result = await db.execute(stmt)
            repository = result.scalars().first()

            if not repository:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No GitLab repository linked to this project",
                )

            # Trigger sync
            from app.config import settings
            synced, errors = await CommitSyncService.sync_repository(
                db,
                repository,
                settings.GITLAB_API_BASE_URL,
            )

            return {
                "project_id": project_id,
                "commits_synced": synced,
                "errors": errors,
                "status": "success" if errors == 0 else "partial_success",
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error triggering manual sync: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to trigger sync",
            )
