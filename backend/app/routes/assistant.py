"""
AI assistant routes.
"""
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.controllers.assistant import fetch_job_status, run_assistant_workflow
from app.databases import get_db
from app.models import Role, User, UserRole
from app.services import AIJobResponse, AIWorkflowRequest, AIWorkflowResponse, verify_token
from app.services.telemetry import get_ai_metrics

router = APIRouter(prefix="/ai-assistant", tags=["ai-assistant"])

AI_ROLE_ACCESS: dict[str, set[str]] = {
    "planning": {"admin", "project_manager", "team_lead"},
    "sprint_summary": {"admin", "project_manager", "team_lead", "engineer"},
    "standup_recap": {"admin", "project_manager", "team_lead", "engineer"},
    "task_recommendation": {"admin", "project_manager", "team_lead"},
    "workload_suggestion": {"admin", "project_manager", "team_lead"},
    "ticket_explanation": {"admin", "project_manager", "team_lead", "engineer"},
    "documentation_helper": {"admin", "project_manager", "team_lead", "engineer"},
    "bug_analysis": {"admin", "project_manager", "team_lead", "engineer"},
    "kanban_jobdesk": {"admin", "project_manager", "team_lead"},
}


async def get_current_ai_user(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = authorization.split(" ", 1)[1].strip()
    payload = verify_token(token)
    if not payload or payload.get("type") == "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    stmt = select(User).where(User.user_id == int(user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    stmt = select(Role.name).join(UserRole, UserRole.role_id == Role.role_id).where(UserRole.user_id == user.user_id)
    result = await db.execute(stmt)
    roles = result.scalars().all()

    if not roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="AI access requires a role assignment")

    return {
        "user_id": user.user_id,
        "email": user.email,
        "full_name": user.full_name,
        "role": roles[0],
        "roles": roles,
    }


def require_ai_roles(*allowed_roles: str):
    async def dependency(current_user: Dict[str, Any] = Depends(get_current_ai_user)) -> Dict[str, Any]:
        user_roles = set(current_user["roles"])
        if "admin" in user_roles:
            return current_user

        if not user_roles.intersection(allowed_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="AI access denied for this workflow")
        return current_user

    return dependency


@router.post("/planning", response_model=AIWorkflowResponse)
async def generate_planning(
    req: AIWorkflowRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_ai_roles(*AI_ROLE_ACCESS["planning"])),
):
    return await run_assistant_workflow("planning", req, db, current_user, request)


@router.post("/sprint-summary", response_model=AIWorkflowResponse)
async def generate_sprint_summary(
    req: AIWorkflowRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_ai_roles(*AI_ROLE_ACCESS["sprint_summary"])),
):
    return await run_assistant_workflow("sprint_summary", req, db, current_user, request)


@router.post("/standup-recap", response_model=AIWorkflowResponse)
async def generate_standup_recap(
    req: AIWorkflowRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_ai_roles(*AI_ROLE_ACCESS["standup_recap"])),
):
    return await run_assistant_workflow("standup_recap", req, db, current_user, request)


@router.post("/task-recommendation", response_model=AIWorkflowResponse)
async def generate_task_recommendation(
    req: AIWorkflowRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_ai_roles(*AI_ROLE_ACCESS["task_recommendation"])),
):
    return await run_assistant_workflow("task_recommendation", req, db, current_user, request)


@router.post("/workload-suggestion", response_model=AIWorkflowResponse)
async def generate_workload_suggestion(
    req: AIWorkflowRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_ai_roles(*AI_ROLE_ACCESS["workload_suggestion"])),
):
    return await run_assistant_workflow("workload_suggestion", req, db, current_user, request)


@router.post("/ticket-explanation", response_model=AIWorkflowResponse)
async def generate_ticket_explanation(
    req: AIWorkflowRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_ai_roles(*AI_ROLE_ACCESS["ticket_explanation"])),
):
    return await run_assistant_workflow("ticket_explanation", req, db, current_user, request)


@router.post("/documentation-helper", response_model=AIWorkflowResponse)
async def generate_documentation_helper(
    req: AIWorkflowRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_ai_roles(*AI_ROLE_ACCESS["documentation_helper"])),
):
    return await run_assistant_workflow("documentation_helper", req, db, current_user, request)


@router.post("/bug-analysis", response_model=AIWorkflowResponse)
async def generate_bug_analysis(
    req: AIWorkflowRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_ai_roles(*AI_ROLE_ACCESS["bug_analysis"])),
):
    return await run_assistant_workflow("bug_analysis", req, db, current_user, request)


@router.post("/kanban-jobdesk", response_model=AIWorkflowResponse)
async def generate_kanban_jobdesk(
    req: AIWorkflowRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_ai_roles(*AI_ROLE_ACCESS["kanban_jobdesk"])),
):
    return await run_assistant_workflow("kanban_jobdesk", req, db, current_user, request)


@router.get("/jobs/{job_id}", response_model=AIJobResponse)
async def get_ai_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_ai_user),
):
    return await fetch_job_status(job_id, current_user, db)


@router.get("/health", tags=["health"])
async def ai_health_check() -> Dict[str, Any]:
    """
    Get AI assistant health metrics and telemetry.
    
    Returns:
        Dictionary with health status, request counts, latency metrics, and error rates.
    """
    metrics = get_ai_metrics()
    success_rate = (
        (metrics.successful_requests / metrics.total_requests * 100)
        if metrics.total_requests > 0
        else 0.0
    )
    
    return {
        "status": "healthy" if metrics.total_requests == 0 or success_rate >= 80.0 else "degraded",
        "total_requests": metrics.total_requests,
        "successful_requests": metrics.successful_requests,
        "failed_requests": metrics.failed_requests,
        "success_rate_percent": round(success_rate, 2),
        "latency_ms": {
            "avg": round(metrics.avg_latency_ms, 2),
            "min": round(metrics.min_latency_ms, 2) if metrics.min_latency_ms != float("inf") else None,
            "max": round(metrics.max_latency_ms, 2),
        },
        "error_counts": metrics.error_counts,
        "workflow_counts": metrics.workflow_counts,
        "last_updated": metrics.last_updated.isoformat(),
    }
