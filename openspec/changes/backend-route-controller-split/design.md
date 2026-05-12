## Context

The backend currently concentrates endpoint behavior in route modules. This makes the files larger, harder to test in isolation, and more expensive to maintain as endpoint complexity grows. The refactor applies across multiple route modules, so a clear controller boundary is useful before implementation starts.

## Goals / Non-Goals

**Goals:**
- Move business logic out of route modules into controllers.
- Keep routing files thin and consistent.
- Preserve existing external API behavior.
- Make controller logic easier to unit test and reuse.
- Keep the refactor incremental enough to avoid a large-bang rewrite.

**Non-Goals:**
- Redesign endpoint URLs or API response contracts.
- Change database schema or migrate stored data.
- Rewrite unrelated service or model logic.
- Introduce a new framework or external dependency.

## Decisions

- Introduce an `app/controllers` layer for endpoint-specific orchestration.
  - Rationale: it separates HTTP transport concerns from domain logic without changing the existing FastAPI stack.
  - Alternatives considered: keeping logic in routes or moving everything into services. Keeping logic in routes preserves the current complexity; moving straight to services can blur endpoint orchestration and business use cases.
- Refactor route modules incrementally, module by module.
  - Rationale: smaller changes reduce regression risk and let tests validate each slice.
  - Alternatives considered: a full rewrite of all routes at once. Rejected because it increases risk and makes validation harder.
- Preserve existing request/response contracts while changing internal call flow.
  - Rationale: frontend consumers should not need to change just because the backend structure changed.
  - Alternatives considered: simultaneous API redesign. Rejected because the goal is maintainability, not a contract change.

## Risks / Trade-offs

- [Risk] Some route modules may have hidden coupling to models or services → Mitigation: introduce controllers alongside current code, migrate one module at a time, and add tests around the moved behavior.
- [Risk] Refactor may accidentally change endpoint behavior → Mitigation: keep route paths and response shapes unchanged and validate with existing endpoint tests.
- [Risk] More files may increase navigation overhead initially → Mitigation: use a consistent controller naming convention that mirrors route modules.

## Migration Plan

1. Create controller modules for the first set of route domains.
2. Move endpoint business logic from route handlers into the corresponding controllers.
3. Update route handlers to call controllers and keep HTTP-specific concerns only.
4. Run backend tests after each refactored module.
5. Roll back by restoring the original route logic if a module introduces regressions.

**Data Migration Strategy:**
- No database data migration is required; this is a code-structure refactor only.

**Rollback Plan:**
- Revert controller extraction for any module that fails validation, keeping the previous route logic in place until the issue is resolved.

## Open Questions

- Which route modules should be migrated first to reduce the highest maintenance risk?
- Should controller modules mirror route module names exactly, or should they be grouped by domain?
- Are there any endpoints with special streaming or file-response behavior that should remain in route handlers?
