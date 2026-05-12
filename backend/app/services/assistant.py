"""
OpenRouter AI assistant gateway and workflow orchestration.
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import httpx

from app.config import get_settings
from app.services.telemetry import record_workflow_latency

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    def __init__(self, message: str, status_code: int = 502, retryable: bool = False):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.retryable = retryable


class AIConfigurationError(Exception):
    pass


@dataclass(slots=True)
class WorkflowDefinition:
    key: str
    title: str
    system_prompt: str
    allowed_roles: set[str]
    output_schema: Dict[str, str]


@dataclass(slots=True)
class AIJobRecord:
    job_id: str
    workflow: str
    status: str
    requested_by_user_id: int
    requested_by_role: str
    prompt: str
    context: Dict[str, Any]
    model: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


WORKFLOW_DEFINITIONS: dict[str, WorkflowDefinition] = {
    "planning": WorkflowDefinition(
        key="planning",
        title="Project Planning Generation",
        system_prompt=(
            "You are an engineering planning assistant. Return concise, actionable planning output "
            "with milestones, risks, dependencies, and recommended phases."
        ),
        allowed_roles={"admin", "project_manager", "team_lead"},
        output_schema={
            "summary": "One-paragraph planning summary",
            "milestones": "Array of milestone items",
            "risks": "Array of key risks",
            "recommended_next_steps": "Array of next actions",
        },
    ),
    "sprint_summary": WorkflowDefinition(
        key="sprint_summary",
        title="Sprint Summary",
        system_prompt=(
            "You are a sprint reporting assistant. Summarize completed work, blockers, carry-over, "
            "and next sprint focus in a crisp, structured format."
        ),
        allowed_roles={"admin", "project_manager", "team_lead", "engineer"},
        output_schema={
            "summary": "Short sprint summary",
            "completed_work": "Array of completed items",
            "blockers": "Array of blockers",
            "next_focus": "Array of next sprint priorities",
        },
    ),
    "standup_recap": WorkflowDefinition(
        key="standup_recap",
        title="Auto Standup Recap",
        system_prompt=(
            "You are a standup recap assistant. Produce a short recap with progress, blockers, owners, "
            "and follow-up actions."
        ),
        allowed_roles={"admin", "project_manager", "team_lead", "engineer"},
        output_schema={
            "recap": "Standup recap paragraph",
            "blockers": "Array of blocker items",
            "follow_ups": "Array of follow-up actions",
        },
    ),
    "task_recommendation": WorkflowDefinition(
        key="task_recommendation",
        title="Smart Task Recommendation",
        system_prompt=(
            "You are a task recommendation assistant. Prioritize work by impact, urgency, and capacity."
        ),
        allowed_roles={"admin", "project_manager", "team_lead"},
        output_schema={
            "recommendations": "Array of ranked task recommendations",
            "rationale": "Reasoning for ranking",
            "capacity_notes": "Notes about workload or dependencies",
        },
    ),
    "workload_suggestion": WorkflowDefinition(
        key="workload_suggestion",
        title="AI Workload Suggestion",
        system_prompt=(
            "You are a workload balancing assistant. Suggest distribution changes, overload warnings, "
            "and capacity adjustments."
        ),
        allowed_roles={"admin", "project_manager", "team_lead"},
        output_schema={
            "suggestions": "Array of balancing suggestions",
            "overloaded_members": "Array of overloaded people or roles",
            "underutilized_members": "Array of underutilized people or roles",
        },
    ),
    "ticket_explanation": WorkflowDefinition(
        key="ticket_explanation",
        title="Ticket Explanation",
        system_prompt=(
            "You are a ticket explanation assistant. Explain objectives, dependencies, risks, and implementation notes."
        ),
        allowed_roles={"admin", "project_manager", "team_lead", "engineer"},
        output_schema={
            "explanation": "Clear ticket explanation",
            "dependencies": "Array of dependencies",
            "implementation_notes": "Array of implementation considerations",
        },
    ),
    "documentation_helper": WorkflowDefinition(
        key="documentation_helper",
        title="Technical Documentation Helper",
        system_prompt=(
            "You are a technical documentation assistant. Draft clear engineering documentation, API notes, "
            "or implementation guidance based on the provided context."
        ),
        allowed_roles={"admin", "project_manager", "team_lead", "engineer"},
        output_schema={
            "documentation": "Draft documentation content",
            "key_points": "Array of key points",
            "open_questions": "Array of unresolved questions",
        },
    ),
    "bug_analysis": WorkflowDefinition(
        key="bug_analysis",
        title="Bug Analysis Assistant",
        system_prompt=(
            "You are a bug analysis assistant. Provide likely root causes, diagnostic steps, and remediation ideas."
        ),
        allowed_roles={"admin", "project_manager", "team_lead", "engineer"},
        output_schema={
            "root_causes": "Array of likely root causes",
            "diagnostic_steps": "Array of next diagnostic actions",
            "fix_suggestions": "Array of probable fixes",
        },
    ),
    "kanban_jobdesk": WorkflowDefinition(
        key="kanban_jobdesk",
        title="AI Kanban and Jobdesk Generation",
        system_prompt=(
            "You are a kanban planning assistant. Break scope into kanban-ready items and role-based jobdesk output."
        ),
        allowed_roles={"admin", "project_manager", "team_lead"},
        output_schema={
            "kanban_items": "Array of kanban items",
            "jobdesk": "Array of role-based jobdesk items",
            "notes": "Array of planning notes",
        },
    ),
}

_JOB_STORE: dict[str, AIJobRecord] = {}
_JOB_STORE_LOCK = asyncio.Lock()


def validate_ai_settings() -> None:
    settings = get_settings()
    if not settings.OPENROUTER_ENABLED:
        return

    missing = []
    if not settings.OPENROUTER_API_KEY:
        missing.append("OPENROUTER_API_KEY")
    if not settings.OPENROUTER_BASE_URL:
        missing.append("OPENROUTER_BASE_URL")
    if not settings.OPENROUTER_MODEL:
        missing.append("OPENROUTER_MODEL")

    if missing:
        raise AIConfigurationError(
            "AI assistant is enabled but the following settings are missing: "
            + ", ".join(missing)
        )


def get_workflow_definition(workflow: str) -> WorkflowDefinition:
    try:
        return WORKFLOW_DEFINITIONS[workflow]
    except KeyError as exc:
        raise AIConfigurationError(f"Unknown AI workflow: {workflow}") from exc


def _serialize_context(context: Dict[str, Any]) -> str:
    return json.dumps(context or {}, ensure_ascii=False, indent=2, default=str)


def build_messages(workflow: str, prompt: str, context: Dict[str, Any]) -> list[dict[str, str]]:
    definition = get_workflow_definition(workflow)
    context_blob = _serialize_context(context)
    user_prompt = (
        f"Workflow: {definition.title}\n"
        f"User request: {prompt}\n\n"
        f"Context JSON:\n{context_blob}\n\n"
        f"Return JSON with these keys: {', '.join(definition.output_schema.keys())}."
    )
    return [
        {"role": "system", "content": definition.system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def _normalize_content(raw_content: str) -> tuple[str, Optional[Dict[str, Any]]]:
    try:
        parsed = json.loads(raw_content)
    except (TypeError, ValueError, json.JSONDecodeError):
        return raw_content, None

    if isinstance(parsed, dict):
        pretty = json.dumps(parsed, ensure_ascii=False, indent=2)
        return pretty, parsed

    return raw_content, None


def _fallback_result(workflow: str, prompt: str) -> Dict[str, Any]:
    definition = get_workflow_definition(workflow)
    structured: Dict[str, Any] = {}

    for key, hint in definition.output_schema.items():
        if hint.startswith("Array"):
            structured[key] = [f"Fallback guidance for {workflow}", prompt]
        else:
            structured[key] = f"Fallback {definition.title.lower()} output for: {prompt}"

    content = json.dumps(structured, ensure_ascii=False, indent=2)
    return {
        "workflow": workflow,
        "status": "completed",
        "model": "local-fallback",
        "content": content,
        "structured_output": structured,
        "source": "fallback",
    }


async def run_workflow(workflow: str, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
    settings = get_settings()
    get_workflow_definition(workflow)
    
    start_time = time.monotonic()
    error_type = None

    try:
        if not settings.OPENROUTER_ENABLED:
            logger.info("OpenRouter disabled; using fallback for workflow=%s", workflow)
            result = _fallback_result(workflow, prompt)
            latency_ms = (time.monotonic() - start_time) * 1000
            record_workflow_latency(workflow, latency_ms, success=True)
            return result

        messages = build_messages(workflow, prompt, context)
        payload = {
            "model": settings.OPENROUTER_MODEL,
            "messages": messages,
        }

        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        if settings.OPENROUTER_SITE_URL:
            headers["HTTP-Referer"] = settings.OPENROUTER_SITE_URL
        if settings.OPENROUTER_SITE_NAME:
            headers["X-OpenRouter-Title"] = settings.OPENROUTER_SITE_NAME

        timeout = httpx.Timeout(settings.OPENROUTER_TIMEOUT_SECONDS)
        url = f"{settings.OPENROUTER_BASE_URL.rstrip('/')}/chat/completions"
        last_error: Optional[Exception] = None
        last_message = "OpenRouter request failed"

        for attempt in range(settings.OPENROUTER_MAX_RETRIES + 1):
            retryable = False
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(url, headers=headers, json=payload)

                if response.status_code >= 400:
                    retryable = response.status_code in {408, 425, 429, 500, 502, 503, 504}
                    message = response.text or f"OpenRouter request failed with status {response.status_code}"
                    raise AIServiceError(message=message, status_code=response.status_code, retryable=retryable)

                data = response.json()
                content = ""
                if data.get("choices"):
                    message = data["choices"][0].get("message", {})
                    content = message.get("content") or ""

                normalized_content, structured_output = _normalize_content(content)
                usage = data.get("usage") or {}
                result = {
                    "workflow": workflow,
                    "status": "completed",
                    "model": data.get("model", settings.OPENROUTER_MODEL),
                    "content": normalized_content,
                    "structured_output": structured_output,
                    "source": "openrouter",
                    "usage": usage,
                }
                
                # Record successful workflow execution
                latency_ms = (time.monotonic() - start_time) * 1000
                record_workflow_latency(workflow, latency_ms, success=True)
                return result
                
            except (httpx.TimeoutException, httpx.RequestError) as exc:
                last_error = exc
                retryable = True
                last_message = str(exc) or "OpenRouter request failed"
                error_type = type(exc).__name__
            except AIServiceError as exc:
                last_error = exc
                retryable = exc.retryable
                last_message = exc.message
                error_type = "AIServiceError"

            if attempt >= settings.OPENROUTER_MAX_RETRIES or not retryable:
                break

            backoff = settings.OPENROUTER_RETRY_BACKOFF_SECONDS * (2 ** attempt)
            await asyncio.sleep(backoff)

        raise AIServiceError(
            message=last_message,
            status_code=getattr(last_error, "status_code", 502),
            retryable=False,
        )
    
    except AIServiceError as exc:
        latency_ms = (time.monotonic() - start_time) * 1000
        record_workflow_latency(workflow, latency_ms, success=False, error_type=error_type or "AIServiceError")
        raise
    except Exception as exc:
        latency_ms = (time.monotonic() - start_time) * 1000
        record_workflow_latency(workflow, latency_ms, success=False, error_type=type(exc).__name__)
        raise


async def create_job(workflow: str, prompt: str, context: Dict[str, Any], user_id: int, user_role: str) -> AIJobRecord:
    settings = get_settings()
    job_id = uuid.uuid4().hex
    record = AIJobRecord(
        job_id=job_id,
        workflow=workflow,
        status="queued",
        requested_by_user_id=user_id,
        requested_by_role=user_role,
        prompt=prompt,
        context=context,
        model=settings.OPENROUTER_MODEL,
    )

    async with _JOB_STORE_LOCK:
        _JOB_STORE[job_id] = record
    # Only schedule background execution when OpenRouter is enabled.
    # When disabled (local fallback), avoid immediate execution to prevent
    # race conditions where the job completes before the caller sees a "queued" status.
    if settings.OPENROUTER_ENABLED:
        asyncio.create_task(_execute_job(job_id))
    return record


async def _execute_job(job_id: str) -> None:
    async with _JOB_STORE_LOCK:
        job = _JOB_STORE.get(job_id)

    if not job:
        return

    try:
        result = await run_workflow(job.workflow, job.prompt, job.context)
        job.status = "completed"
        job.result = result
        job.model = result.get("model", job.model)
        job.error = None
    except Exception as exc:  # pragma: no cover - background fallback path
        job.status = "failed"
        job.error = str(exc)
        job.result = None
    finally:
        job.updated_at = datetime.now(timezone.utc)
        async with _JOB_STORE_LOCK:
            _JOB_STORE[job_id] = job


async def get_job(job_id: str) -> Optional[AIJobRecord]:
    async with _JOB_STORE_LOCK:
        return _JOB_STORE.get(job_id)
