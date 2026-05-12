## Why

We need a backend-only AI assistant integration to provide automated planning, summaries, recommendations, and technical assistance without coupling provider logic into the frontend. Using OpenRouter centralizes model access, enables model selection (e.g., NVIDIA Nemotron 3 Super), and keeps secrets and usage controls server-side.

## What Changes

- Add a backend AI gateway service that calls the OpenRouter Chat Completions API (no frontend provider calls).
- Add AI assistant endpoints for: project planning, sprint summary, standup recap, task recommendation, workload suggestion, ticket explanation, documentation helper, bug analysis, and kanban/jobdesk generation.
- Implement prompt templating, response normalization (JSON-first when possible), retry & timeout policy, and a feature-flag to disable external calls.
- Add audit logging for AI usage and role-based access enforcement. Persist minimal telemetry (latency, error rates, counts).
- Provide optional background job mode for long-running generations.

## Capabilities

### New Capabilities
- `ai-backend-openrouter`: Backend-only AI gateway and workflows using OpenRouter.
- `ai-backend-workflows`: Workflow definitions and normalized outputs for planning, summaries, recommendations, and engineering assistance.

### Modified Capabilities
- None.

## Impact

- Affected code: backend service layer (new `app/services/assistant.py`), controller and route modules (`app/controllers/assistant.py`, `app/routes/assistant.py`), configuration (`app/config.py`), and tests.
- External dependencies: OpenRouter API (model `nvidia/nemotron-3-super-120b-a12b:free` recommended in config). Do NOT commit API keys—use environment variables.
- Data privacy: redact sensitive user or project content before sending to provider in production; free model provider logs may retain content—do not use for confidential data without agreement.
- Rollback: feature flag disables external calls and falls back to local guidance; no DB schema changes required for the initial rollout.
