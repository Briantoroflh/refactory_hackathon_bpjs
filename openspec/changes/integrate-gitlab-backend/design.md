## Context

The platform has foundational models for projects, teams, and users with a FastAPI backend and PostgreSQL database. Currently, commit tracking exists but is limited. GitLab integration requires:

1. **GitLab API Authentication**: Secure API key storage and token management
2. **Data Mapping**: Link platform projects to GitLab repositories
3. **Continuous Sync**: Background jobs to periodically fetch commits
4. **Analytics Pipeline**: Store and query commit data for dashboard insights
5. **Async Architecture**: Non-blocking operations for external API calls

The existing tech stack supports these requirements: FastAPI (async), SQLAlchemy (ORM), Alembic (migrations), and background task scheduling capabilities.

## Goals / Non-Goals

**Goals:**
- Enable automatic repository creation and linking when a project is created
- Continuously synchronize commits from GitLab repositories into the platform database
- Provide commit activity metrics on the dashboard (commit frequency, contributor trends, branch activity)
- Track repository health indicators and development pace
- Maintain audit logs for all GitLab API operations
- Support secure credential storage for GitLab API keys
- Enable easy rollback without data loss

**Non-Goals:**
- Pull request tracking (commits only)
- Issue management or milestone tracking
- Code review metrics
- Custom GitLab webhook handling (polling-based sync instead)
- Multi-repository per project support (1-to-1 mapping only)

## Decisions

### 1. **Background Job Scheduler for Commit Sync**
**Decision:** Use APScheduler (or similar) for periodic commit synchronization instead of webhooks.

**Rationale:**
- Webhooks require public endpoints and more complex deployment
- Polling provides better control, retry logic, and consistency across deployments
- Easier to test and debug than event-driven architectures
- Less operational overhead for credential rotation

**Alternatives considered:**
- Webhooks: More real-time but harder to secure and test
- Celery + Redis: Overkill for periodic tasks; adds operational complexity

### 2. **GitLab API Client Library**
**Decision:** Use `python-gitlab` library for GitLab API interactions.

**Rationale:**
- Well-maintained, covers all needed endpoints (repositories, commits)
- Type hints and error handling built-in
- Simplifies pagination and retry logic
- Reduces custom HTTP code

**Alternatives considered:**
- Direct `httpx`/`requests` calls: More control but more code and error handling
- GraphQL API: More complex for this use case; REST sufficient

### 3. **Data Model for Repository and Commit Tracking**
**Decision:** Create two new SQLAlchemy models:
- `GitLabRepository`: Stores mapping between platform projects and GitLab repos
  - Fields: `project_id`, `gitlab_project_id`, `gitlab_url`, `gitlab_access_token` (encrypted), `last_sync_timestamp`
- `Commit`: Stores commit metadata
  - Fields: `id`, `repository_id`, `git_hash`, `author`, `message`, `committed_at`, `branch`, `created_at`

**Rationale:**
- Cleanly separates GitLab-specific metadata from project data
- Allows multiple data sources in future (GitHub, Bitbucket)
- Commit queries fast with indexed timestamps and repository IDs
- Enables audit trail of sync operations

**Alternatives considered:**
- Store commits in existing Project model: Violates SRP; harder to manage multiple git sources
- Store encrypted tokens in Project: Mixes concerns; worse security

### 4. **Commit Sync Strategy**
**Decision:** Use incremental sync with `last_sync_timestamp` checkpoint.

**Rationale:**
- Avoids re-fetching all historical commits on each sync
- GitLab API supports filtering by date (`since` parameter)
- Scales well as repository grows
- Minimal bandwidth and database overhead

**Alternatives considered:**
- Full sync on each run: O(n) complexity, wasteful
- Webhook-driven: More events to handle, deployment complexity

### 5. **Error Handling and Retry Logic**
**Decision:** Implement exponential backoff for API failures; log all sync operations to audit table.

**Rationale:**
- GitLab API may temporarily rate-limit or be unavailable
- Audit logs satisfy compliance and debugging needs
- Non-blocking: Sync failures don't crash the app

**Mechanism:**
- Max 3 retries with exponential backoff (1s, 2s, 4s)
- Log to `AuditLog` table with status (success/failure) and error details
- Alert on repeated failures (future enhancement)

### 6. **API Endpoints Structure**
**Decision:** New routes in `/api/v1/repositories/` and `/api/v1/commits/`.

**Routes:**
- `POST /api/v1/repositories/gitlab/link` - Link GitLab repo to project
- `POST /api/v1/repositories/gitlab/sync` - Trigger manual sync
- `GET /api/v1/repositories/{project_id}/gitlab` - Get repository metadata
- `GET /api/v1/commits?project_id=X&days=30` - Query commits with filters (date, author)

**Rationale:**
- Follows REST conventions
- Clear resource hierarchy
- Extensible for other Git platforms

### 7. **Background Job Scheduling**
**Decision:** Initialize APScheduler job on app startup; sync all repositories every 15 minutes.

**Rationale:**
- 15-minute interval balances real-time-ness with API rate limits
- Configurable via environment variable
- Lightweight and requires no external services

**Flow:**
```
App Startup → APScheduler initialized
            → Load all GitLabRepository records
            → Schedule job: sync_all_repositories() every 15 min
            → Sync runs asynchronously without blocking FastAPI
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| **API Rate Limiting** | Cache last_sync_timestamp; implement backoff; monitor API quota usage |
| **Large Repositories** | Pagination in GitLab API calls; batch inserts to database (e.g., 500 commits per batch) |
| **Token Leakage** | Encrypt tokens at rest in DB; use environment variables for initial setup; rotate tokens regularly |
| **Sync Failures** | Audit log all operations; alert on repeated failures; support manual re-sync endpoint |
| **Data Consistency** | Use database transactions for each sync batch; validate commit hashes |
| **First Sync Duration** | For large repos with 10k+ commits, initial sync may take minutes; trigger async and show progress in UI |

## Migration Plan

**Deployment Steps:**
1. Create Alembic migration for new tables: `GitLabRepository`, `Commit`, `RepositoryAuditLog`
2. Deploy updated backend with new models, services, and routes
3. Add environment variables: `GITLAB_API_BASE_URL`, `GITLAB_SYNC_INTERVAL_MINUTES`
4. Configure APScheduler on app startup (no database migration required—config is in code)
5. Optionally: Seed initial repositories via API for existing projects

**Rollback Plan:**
1. Disable APScheduler job via feature flag (set `GITLAB_SYNC_INTERVAL_MINUTES=0`)
2. Leave database tables intact (no data loss)
3. If needed, revert code via git; Alembic downgrade removes tables

**Data Migration:**
- No data migration needed; GitLab integration is purely additive
- Existing projects remain unchanged until explicitly linked to GitLab

## Open Questions

1. **Rate Limiting Strategy**: Should we implement per-repository or global rate limiting? (Recommend per-repository to parallelze syncs)
2. **Token Rotation**: How often should GitLab API tokens be rotated? (Recommend quarterly or on suspected compromise)
3. **Historical Data**: Should we fetch all commits on first link, or only from N days back? (Recommend 90-day lookback to balance completeness and performance)
4. **Dashboard Aggregation**: Should commit stats be pre-computed (materialized views) or computed on-demand? (Recommend pre-compute in sync job for dashboard responsiveness)
