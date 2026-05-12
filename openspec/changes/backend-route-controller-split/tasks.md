## 1. Controller Layer Setup

- [x] 1.1 Create the `app/controllers` package and module structure for route domains.
- [x] 1.2 Define controller naming and import conventions that mirror the existing route modules.
- [x] 1.3 Add any shared helper utilities needed for controller orchestration.

## 2. Route Extraction

- [x] 2.1 Move auth business logic from `app/routes/auth.py` into a controller module.
- [x] 2.2 Move user, project, task, team, worker, audit, and KPI logic into controller modules.
- [x] 2.3 Update route handlers to delegate to controllers while keeping URLs and request/response contracts unchanged.

## 3. Verification

- [x] 3.1 Add or update tests for controller functions and route delegation.
- [x] 3.2 Run the backend test suite to confirm the refactor does not change external API behavior.
- [x] 3.3 Verify the OpenSpec change is ready for implementation.
