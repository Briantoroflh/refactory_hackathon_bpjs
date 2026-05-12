"""
FastAPI routes for GitLab repository management.
"""

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.gitlab import GitLabRepositoryController
from app.controllers.common import get_db
from app.models import User
from app.controllers.auth import get_current_user

router = APIRouter(prefix="/api/v1/repositories/gitlab", tags=["gitlab"])


# Request/Response schemas
class LinkRepositoryRequest(BaseModel):
    """Request schema for linking a GitLab repository."""
    gitlab_project_id: int
    gitlab_url: str = "https://gitlab.com"
    gitlab_token: str


class RepositoryResponse(BaseModel):
    """Response schema for repository metadata."""
    id: int
    project_id: int
    gitlab_project_id: int
    gitlab_url: str
    repository_name: str = None
    repository_url: str = None
    last_sync: str = None

    class Config:
        from_attributes = True


@router.post(
    "/link/{project_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=RepositoryResponse,
    summary="Link GitLab repository to project",
)
async def link_repository(
    project_id: int,
    request: LinkRepositoryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Link a GitLab repository to a platform project.

    Establishes a one-to-one mapping between a project and GitLab repository.
    Validates credentials and repository access before linking.
    """
    return await GitLabRepositoryController.link_repository(
        project_id=project_id,
        gitlab_project_id=request.gitlab_project_id,
        gitlab_url=request.gitlab_url,
        gitlab_token=request.gitlab_token,
        db=db,
        current_user=current_user,
    )


@router.get(
    "/{project_id}",
    response_model=RepositoryResponse,
    summary="Get repository metadata",
)
async def get_repository(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get metadata for a project's linked GitLab repository.

    Returns repository details including GitLab project ID, URL, and last sync time.
    """
    return await GitLabRepositoryController.get_repository(
        project_id=project_id,
        db=db,
        current_user=current_user,
    )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unlink GitLab repository",
)
async def unlink_repository(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Unlink a GitLab repository from a project.

    Disables further commit synchronization for the project.
    Soft-deletes the repository record and associated commits.
    """
    return await GitLabRepositoryController.unlink_repository(
        project_id=project_id,
        db=db,
        current_user=current_user,
    )


@router.post(
    "/sync/{project_id}",
    response_model=dict,
    summary="Trigger manual commit sync",
)
async def trigger_manual_sync(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Trigger manual synchronization of commits for a project.

    Immediately fetches and stores commits from the linked GitLab repository.
    Returns count of newly synced commits.
    """
    return await GitLabRepositoryController.trigger_manual_sync(
        project_id=project_id,
        db=db,
        current_user=current_user,
    )
