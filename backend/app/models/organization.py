"""
Organization structure models: divisions, categories, and workers
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class Division(Base, TimestampMixin):
    """Organizational division (e.g., Engineering, Product, Operations)"""
    __tablename__ = "divisions"

    division_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    categories = relationship("Category", back_populates="division", cascade="all, delete-orphan")
    workers = relationship("Worker", back_populates="division")


class Category(Base, TimestampMixin):
    """Work category within a division (e.g., Backend, Frontend, QA)"""
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    division_id = Column(Integer, ForeignKey("divisions.division_id"), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    division = relationship("Division", back_populates="categories")
    teams = relationship("Team", back_populates="category")


class Worker(Base, TimestampMixin):
    """Worker/Engineer in the system"""
    __tablename__ = "workers"

    worker_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True, unique=True, index=True)
    division_id = Column(Integer, ForeignKey("divisions.division_id"), nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    employment_status = Column(String(50), default="active", nullable=False)  # active, inactive, on_leave
    skills = Column(JSON, nullable=True)  # List of skills
    bio = Column(Text, nullable=True)

    # Relationships
    division = relationship("Division", back_populates="workers")
    team_members = relationship("TeamMember", back_populates="worker", cascade="all, delete-orphan")
    project_team_members = relationship("ProjectTeamMember", back_populates="worker")
    worker_kpi = relationship("WorkerKPI", back_populates="worker", cascade="all, delete-orphan")
    worker_kpi_summaries = relationship("WorkerKPISummary", back_populates="worker", cascade="all, delete-orphan")
    worklog_entries = relationship("ProjectTaskWorkload", back_populates="worker")
    assigned_tasks = relationship("ProjectTask", back_populates="assignee_worker")


class WorkerProfile(Base, TimestampMixin):
    """Extended worker profile information"""
    __tablename__ = "worker_profiles"

    profile_id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.worker_id"), unique=True, nullable=False, index=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    preferred_contact = Column(String(100), nullable=True)  # email, phone, slack
    timezone = Column(String(50), nullable=True)
    languages = Column(JSON, nullable=True)  # List of languages spoken
    certifications = Column(JSON, nullable=True)  # List of certifications
