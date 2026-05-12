"""
KPI and worker performance models
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, JSON, Boolean, Numeric
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class WorkerKPI(Base, TimestampMixin):
    """KPI score for a worker per project"""
    __tablename__ = "worker_kpi"

    kpi_id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.worker_id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False, index=True)
    score = Column(Numeric(5, 2), nullable=False)  # 0-100
    is_manual_override = Column(Boolean, default=False, nullable=False)
    override_reason = Column(Text, nullable=True)
    metrics = Column(JSON, nullable=True)  # Detailed metrics used for calculation
    calculated_by = Column(String(100), nullable=True)  # 'system' or user_id
    
    # Relationships
    worker = relationship("Worker", back_populates="worker_kpi")


class WorkerKPISummary(Base, TimestampMixin):
    """Summary of worker KPI across projects"""
    __tablename__ = "worker_kpi_summaries"

    summary_id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.worker_id"), nullable=False, index=True)
    average_score = Column(Numeric(5, 2), nullable=True)  # Average across projects
    total_projects = Column(Integer, default=0, nullable=False)
    peer_percentile = Column(Integer, nullable=True)  # 0-100 percentile
    trend_data = Column(JSON, nullable=True)  # Historical trend (e.g., last 3 months)
    last_updated = Column(String(50), nullable=True)  # ISO datetime
    
    # Relationships
    worker = relationship("Worker", back_populates="worker_kpi_summaries")


# Project-level KPI definitions will be stored as JSON in projects table
# KPI Definitions structure:
# {
#   "kpi_id": "string",
#   "name": "string",
#   "metric_type": "percentage|numeric",
#   "formula": "string",  # e.g., "completed_tasks / assigned_tasks"
#   "target_value": float,
#   "weight": float,  # 0-1, sum of all weights = 1
# }
