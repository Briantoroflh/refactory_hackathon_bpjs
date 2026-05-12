"""
Base model configuration for SQLAlchemy ORM
"""
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, func
from datetime import datetime

Base = declarative_base()


class TimestampMixin:
    """Mixin for automatic created_at and updated_at timestamps"""
    created_at = Column(
        DateTime,
        default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
