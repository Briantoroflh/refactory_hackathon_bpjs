"""
Worker and KPI management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from typing import List, Optional
from app.models import Worker, WorkerProfile, WorkerKPI, WorkerKPISummary
from app.databases import get_db
from app.services.schemas import WorkerResponse, WorkerKPIResponse, WorkerKPISummaryResponse
from datetime import datetime, timezone

router = APIRouter(prefix="/workers", tags=["workers"])


async def require_auth():
    """Dependency to check authentication"""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )


@router.post("")
async def create_worker(
    full_name: str = Query(...),
    email: str = Query(...),
    division_id: int = Query(...),
    phone: Optional[str] = Query(None),
    skills: Optional[List[str]] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Create a new worker profile
    
    - **full_name**: Full name of worker
    - **email**: Email address (must be unique)
    - **division_id**: Division ID
    - **phone**: Phone number (optional)
    - **skills**: List of skills (optional)
    """
    # Check for duplicate email
    stmt = select(Worker).where(Worker.email == email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    worker = Worker(
        full_name=full_name,
        email=email,
        division_id=division_id,
        phone=phone,
        skills=skills or [],
        employment_status="active",
    )
    
    db.add(worker)
    await db.commit()
    await db.refresh(worker)
    
    return worker


@router.get("/{worker_id}", response_model=WorkerResponse)
async def get_worker(
    worker_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get worker profile
    
    - **worker_id**: Worker ID
    """
    stmt = select(Worker).where(Worker.worker_id == worker_id)
    result = await db.execute(stmt)
    worker = result.scalar_one_or_none()
    
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker not found"
        )
    
    return worker


@router.put("/{worker_id}", response_model=WorkerResponse)
async def update_worker(
    worker_id: int,
    full_name: Optional[str] = Query(None),
    phone: Optional[str] = Query(None),
    skills: Optional[List[str]] = Query(None),
    employment_status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Update worker profile
    
    - **worker_id**: Worker ID
    - **full_name**: New full name
    - **phone**: New phone number
    - **skills**: Updated skills list
    - **employment_status**: New status (active, on_leave, inactive)
    """
    stmt = select(Worker).where(Worker.worker_id == worker_id)
    result = await db.execute(stmt)
    worker = result.scalar_one_or_none()
    
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker not found"
        )
    
    if full_name:
        worker.full_name = full_name
    if phone is not None:
        worker.phone = phone
    if skills is not None:
        worker.skills = skills
    if employment_status:
        worker.employment_status = employment_status
    
    worker.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(worker)
    
    return worker


@router.get("/{worker_id}/kpi-scores", response_model=List[WorkerKPIResponse])
async def get_worker_kpi_scores(
    worker_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get KPI scores for a worker across projects
    
    - **worker_id**: Worker ID
    """
    stmt = select(WorkerKPI).where(WorkerKPI.worker_id == worker_id)
    result = await db.execute(stmt)
    kpis = result.scalars().all()
    
    return kpis


@router.get("/{worker_id}/kpi-summary", response_model=WorkerKPISummaryResponse)
async def get_worker_kpi_summary(
    worker_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get KPI summary for worker across all projects
    
    - **worker_id**: Worker ID
    """
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


# KPI endpoints under projects
kpi_router = APIRouter(tags=["kpi"])


@kpi_router.post("/projects/{project_id}/kpi-definitions")
async def create_kpi_definition(
    project_id: int,
    name: str = Query(...),
    description: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Create KPI definition for project (PM only)
    
    - **project_id**: Project ID
    - **name**: KPI name
    - **description**: KPI description
    """
    # TODO: Implement KPI definitions table
    return {"message": "KPI definition created (TODO)"}


@kpi_router.get("/projects/{project_id}/kpi-definitions")
async def list_kpi_definitions(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get KPI definitions for project
    
    - **project_id**: Project ID
    """
    # TODO: Implement KPI definitions retrieval
    return {"kpi_definitions": []}


@kpi_router.post("/workers/{worker_id}/kpi/{project_id}")
async def record_worker_kpi(
    worker_id: int,
    project_id: int,
    score: float = Query(..., ge=0, le=100),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Record/calculate KPI score for worker on project
    
    - **worker_id**: Worker ID
    - **project_id**: Project ID
    - **score**: KPI score (0-100)
    """
    stmt = select(WorkerKPI).where(
        and_(WorkerKPI.worker_id == worker_id, WorkerKPI.project_id == project_id)
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        existing.score = score
        existing.updated_at = datetime.now(timezone.utc)
    else:
        kpi = WorkerKPI(
            worker_id=worker_id,
            project_id=project_id,
            score=score,
            metrics={},
            is_manual_override=False,
        )
        db.add(kpi)
    
    await db.commit()
    
    return {"message": "KPI recorded successfully"}


@kpi_router.get("/projects/{project_id}/worker-kpi")
async def get_project_worker_kpi(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get KPI scores for all workers on project (PM only)
    
    - **project_id**: Project ID
    """
    stmt = select(WorkerKPI).where(WorkerKPI.project_id == project_id)
    result = await db.execute(stmt)
    kpis = result.scalars().all()
    
    return {"project_id": project_id, "worker_kpis": kpis}


@kpi_router.put("/workers/{worker_id}/kpi/{project_id}")
async def update_worker_kpi(
    worker_id: int,
    project_id: int,
    score: float = Query(..., ge=0, le=100),
    override_reason: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Manually adjust KPI score (PM only)
    
    - **worker_id**: Worker ID
    - **project_id**: Project ID
    - **score**: New KPI score
    - **override_reason**: Reason for override
    """
    stmt = select(WorkerKPI).where(
        and_(WorkerKPI.worker_id == worker_id, WorkerKPI.project_id == project_id)
    )
    result = await db.execute(stmt)
    kpi = result.scalar_one_or_none()
    
    if not kpi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KPI not found for this worker/project combination"
        )
    
    kpi.score = score
    kpi.is_manual_override = True
    kpi.override_reason = override_reason
    kpi.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    
    return {"message": "KPI updated successfully"}
