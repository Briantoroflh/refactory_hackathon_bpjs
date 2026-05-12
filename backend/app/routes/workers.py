"""
Worker and KPI management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.databases import get_db
from app.services.schemas import WorkerResponse, WorkerKPIResponse, WorkerKPISummaryResponse
from app.controllers.workers import (
    create_kpi_definition as controller_create_kpi_definition,
    create_worker as controller_create_worker,
    get_project_worker_kpi as controller_get_project_worker_kpi,
    get_worker as controller_get_worker,
    get_worker_kpi_scores as controller_get_worker_kpi_scores,
    get_worker_kpi_summary as controller_get_worker_kpi_summary,
    list_kpi_definitions as controller_list_kpi_definitions,
    record_worker_kpi as controller_record_worker_kpi,
    update_worker as controller_update_worker,
    update_worker_kpi as controller_update_worker_kpi,
)

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
    return await controller_create_worker(full_name, email, division_id, phone, skills, db)


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
    return await controller_get_worker(worker_id, db)


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
    return await controller_update_worker(worker_id, full_name, phone, skills, employment_status, db)


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
    return await controller_get_worker_kpi_scores(worker_id, db)


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
    return await controller_get_worker_kpi_summary(worker_id, db)


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
    return await controller_create_kpi_definition(project_id, name, description, db)


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
    return await controller_list_kpi_definitions(project_id, db)


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
    return await controller_record_worker_kpi(worker_id, project_id, score, db)


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
    return await controller_get_project_worker_kpi(project_id, db)


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
    return await controller_update_worker_kpi(worker_id, project_id, score, override_reason, db)
