"""
GitLab integration models for repository and commit tracking.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class GitLabRepository(Base):
    """
    Represents a GitLab repository linked to a platform project.
    One-to-one mapping between platform projects and GitLab repositories.
    """

    __tablename__ = "gitlab_repositories"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, unique=True)
    gitlab_project_id = Column(Integer, nullable=False, index=True)
    gitlab_url = Column(String(500), nullable=False)
    gitlab_access_token = Column(String(500), nullable=False)  # Encrypted in practice
    last_sync_timestamp = Column(DateTime, nullable=True, default=None)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", backref="gitlab_repository")
    commits = relationship("Commit", backref="repository", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("project_id", name="uq_gitlab_repositories_project_id"),
    )


class Commit(Base):
    """
    Represents a commit from a GitLab repository.
    Stores commit metadata for analytics and tracking.
    """

    __tablename__ = "commits"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(
        Integer,
        ForeignKey("gitlab_repositories.id"),
        nullable=False,
        index=True,
    )
    git_hash = Column(String(40), nullable=False, index=True)  # SHA-1 hash
    author_name = Column(String(255), nullable=False)
    author_email = Column(String(255), nullable=False, index=True)
    message = Column(Text, nullable=False)
    committed_at = Column(DateTime, nullable=False, index=True)
    branch = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint(
            "repository_id",
            "git_hash",
            name="uq_commits_repository_git_hash",
        ),
        Index("idx_commits_repository_committed_at", "repository_id", "committed_at"),
        Index("idx_commits_author_email", "author_email"),
        Index("idx_commits_branch", "branch"),
    )
