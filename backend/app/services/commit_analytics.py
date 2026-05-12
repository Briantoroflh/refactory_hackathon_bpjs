"""
Commit analytics service for calculating dashboard metrics.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.gitlab import GitLabRepository, Commit
from app.services.cache import cache_metric, get_metrics_cache

logger = logging.getLogger(__name__)


class CommitAnalyticsService:
    """
    Service for calculating commit-based metrics for dashboard display.
    """

    @staticmethod
    @cache_metric(ttl_seconds=300)
    async def get_commit_frequency(
        session: AsyncSession,
        repository_id: int,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Calculate commit frequency metrics.

        Args:
            session: AsyncSession for database operations
            repository_id: GitLabRepository ID
            days: Number of days to analyze

        Returns:
            Dictionary with frequency metrics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        stmt = select(func.count(Commit.id)).where(
            and_(
                Commit.repository_id == repository_id,
                Commit.committed_at >= cutoff_date,
            )
        )
        result = await session.execute(stmt)
        total_commits = result.scalar() or 0

        commits_per_day = round(total_commits / days, 2) if days > 0 else 0

        return {
            "total_commits": total_commits,
            "commits_per_day": commits_per_day,
            "period_days": days,
        }

    @staticmethod
    @cache_metric(ttl_seconds=300)
    async def get_top_contributors(
        session: AsyncSession,
        repository_id: int,
        days: int = 30,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get top contributors by commit count.

        Args:
            session: AsyncSession for database operations
            repository_id: GitLabRepository ID
            days: Number of days to analyze
            limit: Number of top contributors to return

        Returns:
            List of contributor dictionaries
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        stmt = (
            select(
                Commit.author_name,
                Commit.author_email,
                func.count(Commit.id).label("commit_count"),
            )
            .where(
                and_(
                    Commit.repository_id == repository_id,
                    Commit.committed_at >= cutoff_date,
                )
            )
            .group_by(Commit.author_email, Commit.author_name)
            .order_by(func.count(Commit.id).desc())
            .limit(limit)
        )

        result = await session.execute(stmt)
        rows = result.all()

        return [
            {
                "name": row[0],
                "email": row[1],
                "commits": row[2],
            }
            for row in rows
        ]

    @staticmethod
    @cache_metric(ttl_seconds=300)
    async def get_branch_activity(
        session: AsyncSession,
        repository_id: int,
        days: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Get commit activity by branch.

        Args:
            session: AsyncSession for database operations
            repository_id: GitLabRepository ID
            days: Number of days to analyze

        Returns:
            List of branch activity dictionaries
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        stmt = (
            select(
                Commit.branch,
                func.count(Commit.id).label("commit_count"),
            )
            .where(
                and_(
                    Commit.repository_id == repository_id,
                    Commit.committed_at >= cutoff_date,
                )
            )
            .group_by(Commit.branch)
            .order_by(func.count(Commit.id).desc())
        )

        result = await session.execute(stmt)
        rows = result.all()

        return [
            {
                "branch": row[0],
                "commits": row[1],
            }
            for row in rows
        ]

    @staticmethod
    @cache_metric(ttl_seconds=300)
    async def get_commit_velocity(
        session: AsyncSession,
        repository_id: int,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Calculate commit velocity (trend analysis).

        Compares current period to previous period to determine velocity direction.

        Args:
            session: AsyncSession for database operations
            repository_id: GitLabRepository ID
            days: Number of days to analyze for current period

        Returns:
            Velocity metrics with trend direction
        """
        now = datetime.utcnow()
        current_start = now - timedelta(days=days)
        previous_start = now - timedelta(days=days * 2)
        previous_end = current_start

        # Current period commits
        current_stmt = select(func.count(Commit.id)).where(
            and_(
                Commit.repository_id == repository_id,
                Commit.committed_at >= current_start,
                Commit.committed_at <= now,
            )
        )
        current_result = await session.execute(current_stmt)
        current_commits = current_result.scalar() or 0

        # Previous period commits
        previous_stmt = select(func.count(Commit.id)).where(
            and_(
                Commit.repository_id == repository_id,
                Commit.committed_at >= previous_start,
                Commit.committed_at <= previous_end,
            )
        )
        previous_result = await session.execute(previous_stmt)
        previous_commits = previous_result.scalar() or 0

        # Calculate velocity
        if previous_commits == 0:
            trend = "increasing" if current_commits > 0 else "stable"
            change_percent = 0
        else:
            change_percent = round(
                ((current_commits - previous_commits) / previous_commits) * 100, 2
            )
            if change_percent > 5:
                trend = "increasing"
            elif change_percent < -5:
                trend = "decreasing"
            else:
                trend = "stable"

        return {
            "current_period_commits": current_commits,
            "previous_period_commits": previous_commits,
            "change_percent": change_percent,
            "trend": trend,
            "period_days": days,
        }

    @staticmethod
    @cache_metric(ttl_seconds=300)
    async def get_repository_health_status(
        session: AsyncSession,
        repository_id: int,
        days: int = 30,
    ) -> str:
        """
        Determine repository health status based on activity.

        Returns one of: "healthy", "yellow", "red"
        - healthy: Good commit activity and contributor engagement
        - yellow: Moderate activity or declining trend
        - red: Low activity or no commits

        Args:
            session: AsyncSession for database operations
            repository_id: GitLabRepository ID
            days: Number of days to analyze

        Returns:
            Health status string
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get commit count
        commit_stmt = select(func.count(Commit.id)).where(
            and_(
                Commit.repository_id == repository_id,
                Commit.committed_at >= cutoff_date,
            )
        )
        commit_result = await session.execute(commit_stmt)
        total_commits = commit_result.scalar() or 0

        # Get unique contributors
        contributors_stmt = (
            select(func.count(func.distinct(Commit.author_email)))
            .where(
                and_(
                    Commit.repository_id == repository_id,
                    Commit.committed_at >= cutoff_date,
                )
            )
        )
        contributors_result = await session.execute(contributors_stmt)
        unique_contributors = contributors_result.scalar() or 0

        # Simple health scoring
        commits_per_day = total_commits / days if days > 0 else 0
        contributors_ratio = unique_contributors / (days / 7) if days > 0 else 0

        # Thresholds (adjustable)
        if commits_per_day >= 2 and unique_contributors >= 2:
            return "healthy"
        elif commits_per_day >= 0.5 or unique_contributors >= 1:
            return "yellow"
        else:
            return "red"

    @staticmethod
    @cache_metric(ttl_seconds=300)
    async def get_dashboard_metrics(
        session: AsyncSession,
        repository_id: int,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Get comprehensive dashboard metrics for a repository.

        Aggregates all analytics for dashboard display.

        Args:
            session: AsyncSession for database operations
            repository_id: GitLabRepository ID
            days: Number of days to analyze

        Returns:
            Dictionary with all dashboard metrics
        """
        frequency = await CommitAnalyticsService.get_commit_frequency(
            session, repository_id, days
        )
        velocity = await CommitAnalyticsService.get_commit_velocity(
            session, repository_id, days
        )
        top_contributors = await CommitAnalyticsService.get_top_contributors(
            session, repository_id, days
        )
        branch_activity = await CommitAnalyticsService.get_branch_activity(
            session, repository_id, days
        )
        health = await CommitAnalyticsService.get_repository_health_status(
            session, repository_id, days
        )

        return {
            "repository_id": repository_id,
            "period_days": days,
            "frequency": frequency,
            "velocity": velocity,
            "health_status": health,
            "top_contributors": top_contributors,
            "branch_activity": branch_activity,
            "timestamp": datetime.utcnow().isoformat(),
        }
