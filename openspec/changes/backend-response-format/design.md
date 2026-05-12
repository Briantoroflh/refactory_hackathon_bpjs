## Context

The backend exposes multiple API modules and currently returns mixed response shapes, which forces consumers to special-case success and error handling. This change standardizes the envelope used by the API layer without changing the underlying business rules or persistence model.

## Goals / Non-Goals

**Goals:**
- Return a consistent JSON envelope with `status`, `message`, and `data`.
- Cover both success and error responses.
- Keep HTTP status codes meaningful while making the body shape predictable.
- Minimize churn by introducing reusable helpers instead of duplicating response formatting in each route.

**Non-Goals:**
- Redesign domain models or database schema.
- Change authentication or authorization rules.
- Rewrite every endpoint’s business logic.
- Introduce a new API version or external response library.

## Decisions

- Use shared response helpers and global exception handlers instead of per-endpoint ad hoc formatting.
  - Rationale: a central contract reduces duplication and keeps route handlers focused on business logic.
  - Alternatives considered: response middleware and manual formatting in every route. Middleware is harder to control for exceptions and streamed/non-JSON responses; manual formatting is too error-prone.
- Preserve existing HTTP status codes while normalizing the response body.
  - Rationale: clients and tests can still use status codes for transport-level handling, while the body stays predictable.
  - Alternatives considered: forcing all responses to 200. Rejected because it hides failures and weakens API semantics.
- Represent endpoint payloads in `data` and place human-readable text in `message`.
  - Rationale: this keeps the envelope simple and allows frontend consumers to show user-facing feedback without parsing endpoint-specific structures.

## Risks / Trade-offs

- Some endpoints may already be consumed directly by frontend code expecting the old shape → Mitigation: update the frontend callers together with the backend contract and cover representative endpoints with tests.
- Global exception handling may unintentionally mask debugging details → Mitigation: keep server logs detailed while returning safe error messages to clients.
- File download or non-JSON endpoints may need special handling → Mitigation: preserve raw responses where JSON wrapping would break behavior, and document any exceptions explicitly if they remain.

## Migration Plan

1. Introduce a shared response envelope helper and global error handlers.
2. Refactor route handlers to return wrapped responses consistently.
3. Update tests to assert `status`, `message`, and `data` on representative endpoints.
4. Run the full backend test suite and fix any routes still returning legacy shapes.
5. If needed, roll back by restoring the prior route response shapes and removing the shared wrapper helpers.

## Open Questions

- Should all error responses use `status: "error"` or should some legacy cases preserve alternate status labels?
- Are there any routes that must remain non-JSON responses and therefore should be exempt from the envelope?
- Should pagination metadata live inside `data` or as a sibling object within it?
