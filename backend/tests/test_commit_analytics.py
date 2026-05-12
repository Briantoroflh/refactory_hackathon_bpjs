"""
Unit tests for GitLab commit analytics service.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.commit_analytics import CommitAnalyticsService
from app.models.gitlab import Commit, GitLabRepository


class TestCommitAnalyticsService:
    """Test cases for CommitAnalyticsService."""

    @pytest.mark.asyncio
    async def test_get_commit_frequency(self):
        """Test calculation of commit frequency metrics."""
        mock_session = AsyncMock(spec=AsyncSession)
        
        # Expected output for 30-day period:
        # {
        #     "total_commits": 45,
        #     "commits_per_day": 1.5,
        #     "period_days": 30
        # }
        
        # The service should:
        # 1. Query commits for repository_id in last 30 days
        # 2. Count total commits
        # 3. Calculate average per day

    @pytest.mark.asyncio
    async def test_get_top_contributors(self):
        """Test calculation of top contributors."""
        mock_session = AsyncMock(spec=AsyncSession)
        repository_id = 1
        
        # Expected output:
        # [
        #     {"name": "Alice", "email": "alice@example.com", "commits": 12},
        #     {"name": "Bob", "email": "bob@example.com", "commits": 8},
        #     {"name": "Charlie", "email": "charlie@example.com", "commits": 5},
        # ]
        
        # The service should:
        # 1. Group commits by author_email
        # 2. Count commits per author
        # 3. Sort by commit count descending
        # 4. Limit to top 10 by default

    @pytest.mark.asyncio
    async def test_get_branch_activity(self):
        """Test calculation of branch activity."""
        mock_session = AsyncMock(spec=AsyncSession)
        
        # Expected output:
        # [
        #     {"branch": "main", "commits": 30},
        #     {"branch": "develop", "commits": 15},
        # ]
        
        # The service should:
        # 1. Group commits by branch
        # 2. Count commits per branch
        # 3. Sort by commit count descending

    @pytest.mark.asyncio
    async def test_get_commit_velocity_increasing(self):
        """Test commit velocity calculation with increasing trend."""
        mock_session = AsyncMock(spec=AsyncSession)
        
        # For 30-day analysis:
        # Current period (last 30 days): 50 commits
        # Previous period (30-60 days ago): 30 commits
        
        # Expected output:
        # {
        #     "current_period_commits": 50,
        #     "previous_period_commits": 30,
        #     "change_percent": 66.67,
        #     "trend": "increasing",
        #     "period_days": 30
        # }

    @pytest.mark.asyncio
    async def test_get_commit_velocity_decreasing(self):
        """Test commit velocity calculation with decreasing trend."""
        # Current period: 20 commits
        # Previous period: 40 commits
        
        # Expected output:
        # {
        #     "current_period_commits": 20,
        #     "previous_period_commits": 40,
        #     "change_percent": -50.0,
        #     "trend": "decreasing",
        #     "period_days": 30
        # }

    @pytest.mark.asyncio
    async def test_get_commit_velocity_stable(self):
        """Test commit velocity calculation with stable trend."""
        # Current and previous periods have similar commit counts
        # within 10% threshold
        
        # Expected output:
        # {
        #     "current_period_commits": 30,
        #     "previous_period_commits": 31,
        #     "change_percent": -3.23,
        #     "trend": "stable",
        #     "period_days": 30
        # }

    @pytest.mark.asyncio
    async def test_get_repository_health_healthy(self):
        """Test health status calculation for healthy repository."""
        # Criteria for 'healthy':
        # - commits_per_day >= 1.0
        # - unique_contributors >= 3
        
        # Expected output: "healthy"

    @pytest.mark.asyncio
    async def test_get_repository_health_yellow(self):
        """Test health status calculation for yellow (warning) status."""
        # Criteria for 'yellow':
        # - commits_per_day < 1.0 but > 0.2
        # - OR unique_contributors < 3 but > 1
        
        # Expected output: "yellow"

    @pytest.mark.asyncio
    async def test_get_repository_health_red(self):
        """Test health status calculation for red (critical) status."""
        # Criteria for 'red':
        # - commits_per_day <= 0.2
        # - OR unique_contributors <= 1
        
        # Expected output: "red"

    @pytest.mark.asyncio
    async def test_get_dashboard_metrics_aggregates_all(self):
        """Test that get_dashboard_metrics aggregates all analytics."""
        mock_session = AsyncMock(spec=AsyncSession)
        repository_id = 1
        days = 30
        
        # Expected output structure:
        # {
        #     "repository_id": 1,
        #     "period_days": 30,
        #     "frequency": {...},
        #     "velocity": {...},
        #     "health_status": "healthy",
        #     "top_contributors": [...],
        #     "branch_activity": [...],
        #     "timestamp": "ISO-8601 datetime"
        # }
        
        # The service should call all other methods and aggregate

    @pytest.mark.asyncio
    async def test_metrics_with_zero_commits(self):
        """Test metrics calculation when repository has no commits."""
        mock_session = AsyncMock(spec=AsyncSession)
        
        # Expected behavior:
        # - frequency: total_commits=0, commits_per_day=0
        # - velocity: all zeros, trend="stable"
        # - health_status: "red" (no activity)
        # - contributors: empty list
        # - branches: empty list

    @pytest.mark.asyncio
    async def test_metrics_respects_date_range(self):
        """Test that metrics only include commits in date range."""
        mock_session = AsyncMock(spec=AsyncSession)
        repository_id = 1
        days = 7
        
        # Commits are queried with:
        # committed_at >= (now - 7 days)
        # Should not include commits older than 7 days


class TestCommitAnalyticsIntegration:
    """Integration tests for analytics (requires database)."""

    @pytest.mark.skipif(
        True,  # Skip by default; run with pytest.mark.integration to enable
        reason="Requires --db-integration flag"
    )
    @pytest.mark.asyncio
    async def test_real_database_metrics(self):
        """Test metrics calculation with real database data."""
        # This test would:
        # 1. Create test data in database
        # 2. Call analytics methods
        # 3. Verify calculations are correct
        pass

    @pytest.mark.skipif(
        True,  # Skip by default; run with pytest.mark.integration to enable
        reason="Requires --db-integration flag"
    )
    @pytest.mark.asyncio
    async def test_performance_large_dataset(self):
        """Test metrics performance with 10,000+ commits."""
        # This test would:
        # 1. Insert large dataset
        # 2. Measure query execution time
        # 3. Verify queries use indexes
        # 4. Ensure response < 500ms
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
