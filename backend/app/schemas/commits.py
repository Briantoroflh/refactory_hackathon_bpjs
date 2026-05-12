"""
Pydantic schemas for GitLab commit-related API requests and responses.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# ============================================================================
# Commit Schemas
# ============================================================================

class CommitBase(BaseModel):
    """Base commit model with common fields."""
    git_hash: str
    author_name: str
    author_email: str
    message: str
    committed_at: datetime
    branch: str


class CommitResponse(CommitBase):
    """Response schema for a single commit."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CommitListResponse(BaseModel):
    """Response schema for paginated commits list."""
    total: int
    skip: int
    limit: int
    commits: List[CommitResponse]


class CommitStatsResponse(BaseModel):
    """Response schema for commit statistics."""
    project_id: int
    period_days: int
    total_commits: int
    unique_contributors: int
    commits_per_day: float
    
    branches: List[dict]  # [{"name": "main", "commits": 10}, ...]
    top_contributors: List[dict]  # [{"name": "John", "email": "john@example.com", "commits": 5}, ...]


# ============================================================================
# Dashboard Metrics Schemas
# ============================================================================

class FrequencyMetrics(BaseModel):
    """Commit frequency metrics."""
    total_commits: int
    commits_per_day: float
    period_days: int


class VelocityMetrics(BaseModel):
    """Commit velocity (trend) metrics."""
    current_period_commits: int
    previous_period_commits: int
    change_percent: float
    trend: str  # "increasing", "decreasing", "stable"
    period_days: int


class BranchActivity(BaseModel):
    """Activity metrics for a single branch."""
    name: str
    commits: int


class ContributorActivity(BaseModel):
    """Activity metrics for a single contributor."""
    name: str
    email: str
    commits: int


class DashboardMetricsResponse(BaseModel):
    """Comprehensive dashboard metrics response."""
    repository_id: int
    period_days: int
    frequency: FrequencyMetrics
    velocity: VelocityMetrics
    health_status: str  # "healthy", "yellow", "red"
    top_contributors: List[ContributorActivity]
    branch_activity: List[BranchActivity]
    timestamp: str  # ISO 8601 datetime string


class RepositoryHealthResponse(BaseModel):
    """Repository health status response."""
    project_id: int
    health_status: str  # "healthy", "yellow", "red"


class CommitFrequencyResponse(BaseModel):
    """Commit frequency metrics response."""
    project_id: int
    frequency: FrequencyMetrics


class CommitVelocityResponse(BaseModel):
    """Commit velocity response."""
    project_id: int
    velocity: VelocityMetrics
