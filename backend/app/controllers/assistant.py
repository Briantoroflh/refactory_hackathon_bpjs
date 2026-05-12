"""
AI assistant controller logic.
"""
from typing import Any, Dict

from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.audit import log_action
from app.services.assistant import AIServiceError, create_job, get_job, run_workflow
from app.services.schemas import AIJobResponse, AIWorkflowRequest, AIWorkflowResponse


async def run_assistant_workflow(
    workflow: str,
    req: AIWorkflowRequest,
    db: AsyncSession,
    current_user: Dict[str, Any],
    request: Request,
) -> AIWorkflowResponse | AIJobResponse:
    user_id = current_user["user_id"]
    user_role = current_user["role"]

    if req.async_mode:
        job = await create_job(workflow, req.prompt, req.context, user_id, user_role)
        await _log_ai_action(
            db=db,
            user_id=user_id,
            action=f"AI_{workflow.upper()}_QUEUED",
            request=request,
            details=f"Queued workflow={workflow}",
        )
        return AIJobResponse(
            job_id=job.job_id,
            workflow=workflow,
            status=job.status,
            model=job.model,
            result=None,
            error=None,
        )

    try:
        result = await run_workflow(workflow, req.prompt, req.context)
        await _log_ai_action(
            db=db,
            user_id=user_id,
            action=f"AI_{workflow.upper()}_SUCCESS",
            request=request,
            details=f"Completed workflow={workflow}",
        )
        return AIWorkflowResponse(**result)
    except AIServiceError as exc:
        await _log_ai_action(
            db=db,
            user_id=user_id,
            action=f"AI_{workflow.upper()}_FAILED",
            request=request,
            details=f"workflow={workflow}; error={exc.message}",
        )
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
        )


async def fetch_job_status(job_id: str, current_user: Dict[str, Any], db: AsyncSession) -> AIJobResponse:
    job = await get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI job not found")

    if current_user["role"] != "admin" and job.requested_by_user_id != current_user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this job")

    result_payload = AIWorkflowResponse(**job.result) if job.result else None
    return AIJobResponse(
        job_id=job.job_id,
        workflow=job.workflow,
        status=job.status,
        model=job.model,
        result=result_payload,
        error=job.error,
    )


async def _log_ai_action(
    db: AsyncSession,
    user_id: int,
    action: str,
    request: Request,
    details: str,
) -> None:
    await log_action(
        db,
        user_id=user_id,
        action=action,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details=details,
    )
    await db.commit()
