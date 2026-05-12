"""
User authentication and authorization models
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User account entity"""
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    user_logs = relationship("UserLog", back_populates="user", cascade="all, delete-orphan")
    created_projects = relationship("Project", back_populates="created_by_user", foreign_keys="Project.created_by")
    created_tasks = relationship("ProjectTask", back_populates="created_by_user", foreign_keys="ProjectTask.created_by")


class Role(Base, TimestampMixin):
    """Role for access control"""
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, default=False, nullable=False)  # System roles can't be deleted

    # Relationships
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")


class Permission(Base, TimestampMixin):
    """Permission for granular access control"""
    __tablename__ = "permissions"

    permission_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    resource = Column(String(100), nullable=False)  # e.g., "project", "task", "user"
    action = Column(String(50), nullable=False)  # e.g., "create", "read", "update", "delete"

    # Relationships
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")


class RolePermission(Base):
    """Association between roles and permissions"""
    __tablename__ = "role_permissions"

    role_permission_id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.role_id"), nullable=False, index=True)
    permission_id = Column(Integer, ForeignKey("permissions.permission_id"), nullable=False, index=True)

    # Relationships
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")


class UserRole(Base, TimestampMixin):
    """Assignment of roles to users"""
    __tablename__ = "user_roles"

    user_role_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.role_id"), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
