"""
Project and task management models
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, JSON, DateTime, Float, Numeric
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.team import TeamWorkspace


class ProjectWorkspace(Base, TimestampMixin):
    """Workspace containing projects"""
    __tablename__ = "project_workspaces"

    workspace_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    projects = relationship("Project", back_populates="workspace", cascade="all, delete-orphan")
    team_workspaces = relationship("TeamWorkspace", back_populates="workspace", cascade="all, delete-orphan")


class Project(Base, TimestampMixin):
    """Project entity"""
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("project_workspaces.workspace_id"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="planning", nullable=False)  # planning, active, completed, archived
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    start_date = Column(String(50), nullable=True)  # ISO date
    end_date = Column(String(50), nullable=True)  # ISO date
    repository_url = Column(String(500), nullable=True)
    repository_token = Column(String(500), nullable=True)  # Encrypted in production
    repository_type = Column(String(50), nullable=True)  # github, gitlab, bitbucket
    version = Column(Integer, default=1, nullable=False)  # For optimistic locking
    
    # Relationships
    workspace = relationship("ProjectWorkspace", back_populates="projects")
    created_by_user = relationship("User", back_populates="created_projects", foreign_keys=[created_by])
    project_teams = relationship("ProjectTeam", back_populates="project", cascade="all, delete-orphan")
    project_details = relationship("ProjectDetail", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("ProjectTask", back_populates="project", cascade="all, delete-orphan")
    commits = relationship("ProjectCommitTracking", back_populates="project", cascade="all, delete-orphan")
    summaries = relationship("ProjectSummary", back_populates="project", cascade="all, delete-orphan")


class ProjectTeam(Base, TimestampMixin):
    """Assignment of teams to projects"""
    __tablename__ = "project_teams"

    project_team_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=False, index=True)
    role = Column(String(50), default="contributor", nullable=False)  # contributor, lead, manager
    
    # Relationships
    project = relationship("Project", back_populates="project_teams")
    team = relationship("Team", back_populates="project_teams")
    team_selections = relationship("ProjectTeamSelection", back_populates="project_team")
    team_members = relationship("ProjectTeamMember", back_populates="project_team")


class ProjectTeamSelection(Base, TimestampMixin):
    """Team selection process for project"""
    __tablename__ = "project_team_selections"

    selection_id = Column(Integer, primary_key=True, index=True)
    project_team_id = Column(Integer, ForeignKey("project_teams.project_team_id"), nullable=False, index=True)
    status = Column(String(50), default="pending", nullable=False)  # pending, approved, rejected
    selection_notes = Column(Text, nullable=True)
    
    # Relationships
    project_team = relationship("ProjectTeam", back_populates="team_selections")


class ProjectTeamMember(Base, TimestampMixin):
    """Individual worker assignment to project team"""
    __tablename__ = "project_team_members"

    member_id = Column(Integer, primary_key=True, index=True)
    project_team_id = Column(Integer, ForeignKey("project_teams.project_team_id"), nullable=False, index=True)
    worker_id = Column(Integer, ForeignKey("workers.worker_id"), nullable=False, index=True)
    role = Column(String(50), default="engineer", nullable=False)  # engineer, lead, manager
    allocation_percentage = Column(Float, default=100, nullable=False)  # 0-100%
    
    # Relationships
    project_team = relationship("ProjectTeam", back_populates="team_members")
    worker = relationship("Worker", back_populates="project_team_members")


class ProjectDetail(Base, TimestampMixin):
    """Detailed project information"""
    __tablename__ = "project_details"

    detail_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False, index=True)
    content = Column(Text, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="project_details")
    images = relationship("ProjectDetailImage", back_populates="detail", cascade="all, delete-orphan")
    docs = relationship("ProjectDetailDoc", back_populates="detail", cascade="all, delete-orphan")


class ProjectDetailImage(Base, TimestampMixin):
    """Images attached to project details"""
    __tablename__ = "project_detail_images"

    image_id = Column(Integer, primary_key=True, index=True)
    detail_id = Column(Integer, ForeignKey("project_details.detail_id"), nullable=False, index=True)
    image_url = Column(String(500), nullable=False)
    caption = Column(String(500), nullable=True)
    
    # Relationships
    detail = relationship("ProjectDetail", back_populates="images")


class ProjectDetailDoc(Base, TimestampMixin):
    """Documents attached to project details"""
    __tablename__ = "project_detail_docs"

    doc_id = Column(Integer, primary_key=True, index=True)
    detail_id = Column(Integer, ForeignKey("project_details.detail_id"), nullable=False, index=True)
    doc_url = Column(String(500), nullable=False)
    doc_name = Column(String(255), nullable=False)
    doc_type = Column(String(50), nullable=True)  # pdf, doc, spreadsheet, etc.
    
    # Relationships
    detail = relationship("ProjectDetail", back_populates="docs")


class ProjectTask(Base, TimestampMixin):
    """Individual task in a project"""
    __tablename__ = "project_tasks"

    task_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="backlog", nullable=False)  # backlog, in_progress, in_review, completed, closed
    priority = Column(String(50), default="medium", nullable=False)  # high, medium, low
    story_points = Column(Integer, nullable=True)  # 1-21 scale
    assigned_to = Column(Integer, ForeignKey("workers.worker_id"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    deadline = Column(String(50), nullable=True)  # ISO date
    version = Column(Integer, default=1, nullable=False)  # For optimistic locking
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    assignee_worker = relationship("Worker", back_populates="assigned_tasks", foreign_keys=[assigned_to])
    created_by_user = relationship("User", back_populates="created_tasks", foreign_keys=[created_by])
    workloads = relationship("ProjectTaskWorkload", back_populates="task", cascade="all, delete-orphan")
    histories = relationship("ProjectTaskHistory", back_populates="task", cascade="all, delete-orphan")
    comments = relationship("ProjectTaskComment", back_populates="task", cascade="all, delete-orphan")
    summaries = relationship("ProjectTaskSummary", back_populates="task", cascade="all, delete-orphan")


class ProjectTaskWorkload(Base, TimestampMixin):
    """Work hours logged for a task"""
    __tablename__ = "project_task_workloads"

    workload_id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("project_tasks.task_id"), nullable=False, index=True)
    worker_id = Column(Integer, ForeignKey("workers.worker_id"), nullable=False, index=True)
    work_date = Column(String(50), nullable=False)  # ISO date
    hours_worked = Column(Float, nullable=False)  # 0-8+ hours
    description = Column(Text, nullable=True)
    
    # Relationships
    task = relationship("ProjectTask", back_populates="workloads")
    worker = relationship("Worker", back_populates="worklog_entries")


class ProjectTaskHistory(Base, TimestampMixin):
    """History of changes to tasks"""
    __tablename__ = "project_task_histories"

    history_id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("project_tasks.task_id"), nullable=False, index=True)
    action = Column(String(100), nullable=False)  # status_changed, assigned, deadline_updated, etc.
    field_name = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    changed_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    reason = Column(Text, nullable=True)
    
    # Relationships
    task = relationship("ProjectTask", back_populates="histories")


class ProjectTaskComment(Base, TimestampMixin):
    """Comments on tasks"""
    __tablename__ = "project_task_comments"

    comment_id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("project_tasks.task_id"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    content = Column(Text, nullable=False)
    mentions = Column(JSON, nullable=True)  # List of mentioned user IDs
    is_resolved = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    task = relationship("ProjectTask", back_populates="comments")


class ProjectTaskSummary(Base, TimestampMixin):
    """Summary of completed task"""
    __tablename__ = "project_task_summaries"

    summary_id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("project_tasks.task_id"), nullable=False, index=True)
    total_effort = Column(Float, nullable=True)  # Total hours worked
    completion_date = Column(String(50), nullable=True)  # ISO date
    contributors = Column(JSON, nullable=True)  # List of worker IDs
    notes = Column(Text, nullable=True)
    
    # Relationships
    task = relationship("ProjectTask", back_populates="summaries")


class ProjectSummary(Base, TimestampMixin):
    """Summary of completed project"""
    __tablename__ = "project_summaries"

    project_summary_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False, index=True)
    total_tasks = Column(Integer, nullable=False)
    completed_tasks = Column(Integer, nullable=False)
    total_effort = Column(Float, nullable=True)
    actual_duration_days = Column(Integer, nullable=True)
    key_achievements = Column(Text, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="summaries")
