## 1. Configuration & Security

- [x] 1.1 Add backend configuration keys for OpenRouter (base URL, model, timeout, retries, feature flag).
- [x] 1.2 Ensure `OPENROUTER_API_KEY` is loaded from env and not committed. Document rotation guidance.
- [x] 1.3 Add startup validation that fails when `OPENROUTER_ENABLED=true` but API key missing.

## 2. Service & Gateway

- [x] 2.1 Implement `app/services/assistant.py` to build messages, call OpenRouter `/chat/completions`, handle timeout and retries.
- [x] 2.2 Add response normalization to prefer JSON output when possible and include `usage` metadata.
- [x] 2.3 Add fallback/local guidance path when feature flag is disabled.

## 3. Controllers & Routes

- [x] 3.1 Add `app/controllers/assistant.py` with orchestration and audit logging hooks.
- [x] 3.2 Add `app/routes/assistant.py` with per-workflow endpoints and JWT/role dependency.
- [x] 3.3 Wire the assistant router into `app/main.py` behind config and startup validation.

## 4. Tests & Observability

- [x] 4.1 Add unit tests for gateway retry/timeout behavior and normalization.
- [ ] 4.2 Add API tests for workflow endpoints, role checks, and error handling.
- [ ] 4.3 Add telemetry hooks (latency, errors) and a basic health metric for AI endpoints.

## 5. Rollout

- [ ] 5.1 Deploy to staging with `OPENROUTER_ENABLED=false`, run smoke tests.
- [ ] 5.2 Enable `OPENROUTER_ENABLED=true` in staging, validate outputs and costs.
- [ ] 5.3 Document rollback and key-rotation steps in runbook.
