## Context

The backend will integrate OpenRouter as a centralized AI gateway so client apps do not call external models directly. This keeps keys and usage control in server environments and allows consistent prompt orchestration, response normalization, and auditability.

Constraints:
- Backend uses FastAPI, async patterns, and Pydantic schemas.
- Secrets must not be committed; use environment variables.
- Free model endpoints (e.g., NVIDIA Nemotron 3 Super) may log requests—avoid sending confidential data in production.

## Goals / Non-Goals

**Goals:**
- Implement OpenRouter gateway service with retry, timeout, and structured JSON responses where practical.
- Expose per-workflow endpoints (planning, sprint summary, standup recap, task recommendation, workload suggestion, ticket explanation, documentation helper, bug analysis, kanban/jobdesk).
- Provide role-based access, audit logging, and optional async job mode for long-running tasks.

**Non-Goals:**
- Frontend provider calls or streaming UI integration (this change is backend-only).
- Model training, fine-tuning, or dataset storage.

## Decisions

- Use a service layer `app/services/assistant.py` that encapsulates OpenRouter calls and retry logic.
- Add controller `app/controllers/assistant.py` and route group `app/routes/assistant.py` with explicit workflow endpoints.
- Model selection via environment config (default: `nvidia/nemotron-3-super-120b-a12b:free`).
- Feature flag `OPENROUTER_ENABLED` to disable external calls and fall back to safe local guidance.

## Risks / Trade-offs

- External provider downtime: mitigated by retries and feature flag.
- Data leakage to free provider logs: mitigate via redaction and avoid confidential payloads in production.

## Migration Plan

1. Add config keys and load them from environment.
2. Implement service + controllers + routes behind feature flag.
3. Add unit tests for gateway, controller, and role checks.
4. Deploy to staging with `OPENROUTER_ENABLED=false` for validation, then enable in staged rollout.
