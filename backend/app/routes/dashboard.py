"""
FastAPI routes for dashboard metrics endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases import get_db
from app.models import User, Project
from app.controllers.auth import get_current_user
from app.services.commit_analytics import CommitAnalyticsService
from app.models.gitlab import GitLabRepository
from app.schemas.commits import (
    DashboardMetricsResponse,
    CommitFrequencyResponse,
    CommitVelocityResponse,
    RepositoryHealthResponse,
    FrequencyMetrics,
    VelocityMetrics,
    ContributorActivity,
    BranchActivity,
)
from sqlalchemy import select
from datetime import datetime

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get(
    "/gitlab-metrics/{project_id}",
    summary="Get GitLab metrics for dashboard",
    response_model=dict,
)
async def get_gitlab_dashboard_metrics(
    project_id: int,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get comprehensive GitLab metrics for dashboard display.

    Returns aggregated commit analytics including:
    - Commit frequency and velocity
    - Top contributors
    - Branch activity
    - Repository health status

    Query Parameters:
    - **project_id**: Project ID
    - **days**: Analysis period in days (1-365, default: 30)
    """
    try:
        # Verify project exists and user has access
        project = await db.get(Project, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        # Get linked GitLab repository
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

        # Get comprehensive metrics
        metrics = await CommitAnalyticsService.get_dashboard_metrics(
            db, repository.id, days
        )

        return {
            "project_id": project_id,
            "project_name": getattr(project, "project_name", "Unknown"),
            "metrics": metrics,
        }

    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting dashboard metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard metrics",
        )


@router.get(
    "/gitlab-metrics/{project_id}/frequency",
    summary="Get commit frequency metrics",
)
async def get_commit_frequency(
    project_id: int,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get commit frequency metrics for a project.

    Returns:
    - Total commits in period
    - Commits per day average
    """
    try:
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

        frequency = await CommitAnalyticsService.get_commit_frequency(
            db, repository.id, days
        )

        return {"project_id": project_id, "frequency": frequency}

    except HTTPException:
        raise
    except Exception as e:
        logger = __import__("logging").getLogger(__name__)
        logger.error(f"Error getting commit frequency: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get commit frequency",
        )


@router.get(
    "/gitlab-metrics/{project_id}/velocity",
    summary="Get commit velocity (trend)",
)
async def get_commit_velocity(
    project_id: int,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get commit velocity metrics showing trend direction.

    Returns:
    - Current period commits
    - Previous period commits
    - Trend (increasing, decreasing, stable)
    - Change percentage
    """
    try:
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

        velocity = await CommitAnalyticsService.get_commit_velocity(
            db, repository.id, days
        )

        return {"project_id": project_id, "velocity": velocity}

    except HTTPException:
        raise
    except Exception as e:
        logger = __import__("logging").getLogger(__name__)
        logger.error(f"Error getting commit velocity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get commit velocity",
        )


@router.get(
    "/gitlab-metrics/{project_id}/health",
    summary="Get repository health status",
)
async def get_repository_health(
    project_id: int,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get repository health status.

    Returns:
    - Health status: 'healthy', 'yellow', or 'red'
    - Based on commit activity and contributor engagement
    """
    try:
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

        health = await CommitAnalyticsService.get_repository_health_status(
            db, repository.id, days
        )

        return {"project_id": project_id, "health_status": health}

    except HTTPException:
        raise
    except Exception as e:
        logger = __import__("logging").getLogger(__name__)
        logger.error(f"Error getting health status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get health status",
        )
