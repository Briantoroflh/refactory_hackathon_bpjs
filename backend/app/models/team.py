"""
Team and team management models
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.project import ProjectWorkspace


class Team(Base, TimestampMixin):
    """Team entity containing multiple workers"""
    __tablename__ = "teams"

    team_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active", nullable=False)  # active, inactive, archived
    capacity_hours = Column(Float, default=160, nullable=False)  # Total available hours per sprint
    
    # Relationships
    category = relationship("Category", back_populates="teams")
    team_members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    project_teams = relationship("ProjectTeam", back_populates="team", cascade="all, delete-orphan")


class TeamMember(Base, TimestampMixin):
    """Membership of workers in teams"""
    __tablename__ = "team_members"

    team_member_id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=False, index=True)
    worker_id = Column(Integer, ForeignKey("workers.worker_id"), nullable=False, index=True)
    role = Column(String(50), default="member", nullable=False)  # member, lead, manager
    is_active = Column(Boolean, default=True, nullable=False)
    join_date = Column(String(50), nullable=False)  # ISO date string
    
    # Relationships
    team = relationship("Team", back_populates="team_members")
    worker = relationship("Worker", back_populates="team_members")


class TeamWorkspace(Base, TimestampMixin):
    """Linking teams to workspaces"""
    __tablename__ = "team_workspaces"

    team_workspace_id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=False, index=True)
    workspace_id = Column(Integer, ForeignKey("project_workspaces.workspace_id"), nullable=False, index=True)
    is_primary = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    workspace = relationship("ProjectWorkspace", back_populates="team_workspaces")
