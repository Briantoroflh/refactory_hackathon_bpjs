"""
Commit tracking and audit logging models
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Text, JSON, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class ProjectCommitTracking(Base, TimestampMixin):
    """Commits from linked Git repositories"""
    __tablename__ = "project_commit_tracking"

    commit_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False, index=True)
    commit_hash = Column(String(100), unique=True, nullable=False, index=True)
    author_email = Column(String(255), nullable=False, index=True)
    worker_id = Column(Integer, ForeignKey("workers.worker_id"), nullable=True, index=True)  # Matched worker
    commit_message = Column(Text, nullable=False)
    commit_date = Column(String(50), nullable=False)  # ISO datetime
    files_changed = Column(Integer, nullable=True)
    insertions = Column(Integer, nullable=True)
    deletions = Column(Integer, nullable=True)
    file_list = Column(JSON, nullable=True)  # List of files changed
    
    # Relationships
    project = relationship("Project", back_populates="commits")


class CommitChangeLogs(Base, TimestampMixin):
    """Log of commit sync operations"""
    __tablename__ = "commit_change_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=True, index=True)
    action = Column(String(100), nullable=False)  # commit_sync, attribution_corrected, etc.
    commits_fetched = Column(Integer, nullable=True)
    commits_failed = Column(Integer, nullable=True)
    sync_duration_seconds = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    sync_date = Column(String(50), nullable=False)  # ISO datetime


class UserLog(Base, TimestampMixin):
    """User activity logging"""
    __tablename__ = "user_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    action = Column(String(100), nullable=False)  # login, logout, failed_login, api_call, etc.
    resource = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    status = Column(String(50), nullable=True)  # success, failed, denied
    details = Column(JSON, nullable=True)
    resource_type = Column(String)
    
    # Relationships
    user = relationship("User", back_populates="user_logs")


class AuditSystemLog(Base, TimestampMixin):
    """System audit trails for sensitive operations"""
    __tablename__ = "audit_system_logs"

    audit_id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False)  # user_created, permission_assigned, kpi_adjusted, etc.
    resource_type = Column(String(100), nullable=True)  # user, role, project, task, etc.
    resource_id = Column(Integer, nullable=True)
    changed_by = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    field_name = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)
    severity = Column(String(50), nullable=True)  # info, warning, critical


class GlobalJob(Base, TimestampMixin):
    """Global scheduled jobs tracking"""
    __tablename__ = "global_jobs"

    job_id = Column(Integer, primary_key=True, index=True)
    job_name = Column(String(100), nullable=False, index=True)
    job_type = Column(String(100), nullable=False)  # commit_sync, kpi_calculation, notification, etc.
    status = Column(String(50), default="pending", nullable=False)  # pending, running, completed, failed
    last_run = Column(String(50), nullable=True)  # ISO datetime
    next_run = Column(String(50), nullable=True)  # ISO datetime
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    details = Column(JSON, nullable=True)
