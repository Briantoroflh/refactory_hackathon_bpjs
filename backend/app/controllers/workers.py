"""
Worker and KPI controller logic.
"""
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.controllers.common import commit_and_refresh, fetch_one_or_404
from app.models import Worker, WorkerKPI, WorkerKPISummary
from app.services.time_utils import utcnow_naive


async def create_worker(full_name: str, email: str, division_id: int, phone: Optional[str], skills: Optional[List[str]], db: AsyncSession):
    stmt = select(Worker).where(Worker.email == email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    worker = Worker(full_name=full_name, email=email, division_id=division_id, phone=phone, skills=skills or [], employment_status="active")
    db.add(worker)
    return await commit_and_refresh(db, worker)


async def get_worker(worker_id: int, db: AsyncSession):
    stmt = select(Worker).where(Worker.worker_id == worker_id)
    return await fetch_one_or_404(db, stmt, "Worker not found")


async def update_worker(worker_id: int, full_name: Optional[str], phone: Optional[str], skills: Optional[List[str]], employment_status: Optional[str], db: AsyncSession):
    stmt = select(Worker).where(Worker.worker_id == worker_id)
    result = await db.execute(stmt)
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker not found")

    if full_name:
        worker.full_name = full_name
    if phone is not None:
        worker.phone = phone
    if skills is not None:
        worker.skills = skills
    if employment_status:
        worker.employment_status = employment_status

    worker.updated_at = utcnow_naive()
    return await commit_and_refresh(db, worker)


async def get_worker_kpi_scores(worker_id: int, db: AsyncSession):
    stmt = select(WorkerKPI).where(WorkerKPI.worker_id == worker_id)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_worker_kpi_summary(worker_id: int, db: AsyncSession):
    stmt = select(WorkerKPISummary).where(WorkerKPISummary.worker_id == worker_id)
    result = await db.execute(stmt)
    summary = result.scalar_one_or_none()

    if not summary:
        return {
            "summary_id": None,
            "worker_id": worker_id,
            "average_score": None,
            "total_projects": 0,
            "peer_percentile": None,
        }

    return summary


async def create_kpi_definition(project_id: int, name: str, description: Optional[str], db: AsyncSession):
    return {"message": "KPI definition created (TODO)"}


async def list_kpi_definitions(project_id: int, db: AsyncSession):
    return {"kpi_definitions": []}


async def record_worker_kpi(worker_id: int, project_id: int, score: float, db: AsyncSession):
    stmt = select(WorkerKPI).where(and_(WorkerKPI.worker_id == worker_id, WorkerKPI.project_id == project_id))
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        existing.score = score
        existing.updated_at = utcnow_naive()
    else:
        db.add(WorkerKPI(worker_id=worker_id, project_id=project_id, score=score, metrics={}, is_manual_override=False))

    await db.commit()
    return {"message": "KPI recorded successfully"}


async def get_project_worker_kpi(project_id: int, db: AsyncSession):
    stmt = select(WorkerKPI).where(WorkerKPI.project_id == project_id)
    result = await db.execute(stmt)
    kpis = result.scalars().all()
    return {"project_id": project_id, "worker_kpis": kpis}


async def update_worker_kpi(worker_id: int, project_id: int, score: float, override_reason: Optional[str], db: AsyncSession):
    stmt = select(WorkerKPI).where(and_(WorkerKPI.worker_id == worker_id, WorkerKPI.project_id == project_id))
    result = await db.execute(stmt)
    kpi = result.scalar_one_or_none()

    if not kpi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KPI not found for this worker/project combination")

    kpi.score = score
    kpi.is_manual_override = True
    kpi.override_reason = override_reason
    kpi.updated_at = utcnow_naive()
    await db.commit()
    return {"message": "KPI updated successfully"}