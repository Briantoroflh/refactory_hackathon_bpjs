## Context

SprintFlow requires a production-ready backend that supports multi-tenant team management, real-time analytics, and external integrations (Git platforms, AI services). The system must handle:
- Concurrent task updates from multiple team members
- Real-time productivity metrics and KPI calculations
- Audit logging for compliance and troubleshooting
- Commit synchronization from GitHub/GitLab
- Background processing for AI recommendations and analytics

Currently, there is no database schema, API layer, or authentication system. The frontend (Next.js) is ready to consume APIs but has no backend to connect to.

## Goals / Non-Goals

**Goals:**
- Establish complete PostgreSQL schema with 20+ tables covering all entities (users, projects, tasks, teams, KPIs, audits)
- Implement async FastAPI endpoints with proper request/response validation via Pydantic
- Create SQLAlchemy ORM models with relationships and constraints
- Set up JWT-based authentication with role-based access control (RBAC)
- Establish Alembic migration system for schema versioning
- Implement audit logging for all sensitive operations (user creation, permission changes, KPI updates)
- Create database connection pooling and async context management
- Support concurrent task updates with transaction isolation (READ_COMMITTED or SERIALIZABLE)

**Non-Goals:**
- Git platform integration implementation (only schema support)
- AI service integration (only API endpoints for data; actual AI logic deferred)
- Real-time WebSocket support (REST polling sufficient for MVP)
- Advanced caching strategies beyond connection pooling
- Third-party identity provider integration (local user auth only)
- Multi-database support (PostgreSQL only)

## Decisions

### Decision 1: Async-First FastAPI Architecture
**Choice:** Use FastAPI with async/await and asyncpg for all database operations
**Rationale:** 
- Handles concurrent requests efficiently without threading overhead
- Aligns with Python async ecosystem standards
- Better resource utilization for I/O-bound operations (database, external APIs)
- Matches project tech stack commitment

**Alternatives considered:**
- Django + Django ORM: Heavier framework, less suitable for async patterns
- Flask with threading: Explicit thread management adds complexity

---

### Decision 2: Centralized Alembic Migrations
**Choice:** Use Alembic for all schema changes with auto-generated and manually-reviewed migrations
**Rationale:**
- Version control for database schema
- Reproducible deployments across environments
- Automatic rollback capability
- Clear audit trail of schema evolution

**Alternatives considered:**
- Manual SQL scripts: No rollback capability, error-prone
- ORM auto-migrations: Risk of silent data loss during downgrades

---

### Decision 3: Role-Based Access Control (RBAC) with Permission Tables
**Choice:** Implement three-level permission model: Roles → Permissions → Resources
**Rationale:**
- Flexible permission assignments (users → roles → permissions)
- Supports org-wide and project-level role assignments
- Scalable to future permission requirements
- Clear audit trail of role assignments

**Alternatives considered:**
- Attribute-based access control (ABAC): Overkill for current requirements
- Direct user-resource permissions: No role reusability, maintenance burden

---

### Decision 4: Optimistic Locking for Concurrent Task Updates
**Choice:** Use version columns (integer) with optimistic locking instead of row locks
**Rationale:**
- Avoids database lock contention for highly-updated tasks
- Allows more concurrent readers/writers
- Reduces deadlock risk
- Client retries on conflict (suitable for async workloads)

**Alternatives considered:**
- Pessimistic locking (SELECT ... FOR UPDATE): Serializes access, high contention
- SERIALIZABLE isolation: Very slow for typical workloads

---

### Decision 5: Separate Audit Tables Over Triggers
**Choice:** Explicit insert into audit tables from application code, not database triggers
**Rationale:**
- Application-level control (log only what matters)
- No silent database modifications
- Easier to test and debug
- Captures user context (who made the change, why)

**Alternatives considered:**
- Database triggers: Hidden logic, harder to trace, performance overhead

---

### Decision 6: Async Connection Pooling with Prepared Statements
**Choice:** Use asyncpg connection pool with prepared statements for frequently-run queries
**Rationale:**
- Reuses prepared statement plans (faster repeated queries)
- Reduces parsing overhead
- Safer SQL injection prevention
- Better performance under load

**Alternatives considered:**
- Unmanaged connections: Connection exhaustion under load
- No prepared statements: Higher CPU overhead on database

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **Alembic migration conflicts** in concurrent development | Slow CI/CD, merge conflicts | Establish migration naming convention; one developer applies migrations to shared dev DB |
| **N+1 query problems** in nested relationships (projects → tasks → comments) | High database load, slow API responses | Use SQLAlchemy eager loading (joinedload) in all complex queries; add query logging for detection |
| **Race condition** on KPI calculations during concurrent task updates | Incorrect scores, missed updates | Use transaction isolation (READ_COMMITTED minimum); implement idempotent KPI recalculation |
| **Audit log explosion** if all field updates logged | Large audit tables, slow queries | Log only significant changes (status, assignment, deadline); batch audit inserts |
| **Slow migrations** on large existing tables (millions of rows) | Production deployment downtime | Plan migrations in advance; use online schema change tools if needed; deploy during low-traffic windows |
| **Connection pool exhaustion** under traffic spike | Requests timeout, cascading failures | Set max pool connections conservatively; implement circuit breaker for database unavailability |
| **JWT token replay** if token stolen | Security breach | Token expiration (15 min), refresh token rotation (7 days), HTTPS-only transmission |

## Migration Plan

### Phase 1: Database Schema Deployment
```
1. Create PostgreSQL database with UTF-8 encoding
2. Initialize Alembic in backend/ folder
3. Create initial schema migration (all tables with constraints)
4. Apply migration: alembic upgrade head
5. Verify all tables created via psql or GUI tool
6. Create indexes for foreign keys and frequently-queried columns
```

### Phase 2: Application Layer
```
1. Create SQLAlchemy models matching database schema
2. Configure async engine with asyncpg and connection pooling
3. Implement Pydantic request/response schemas
4. Create FastAPI app with dependency injection for DB session
5. Implement JWT authentication endpoints (register, login, refresh)
6. Create CRUD endpoints for core entities (users, projects, tasks)
```

### Phase 3: Integration & Testing
```
1. Seed database with default roles and permissions
2. Create pytest fixtures for test database
3. Write integration tests for critical flows
4. Test concurrent task updates (race condition detection)
5. Verify Alembic rollback works
```

### Rollback Strategy
- **Code rollback:** Git revert to previous commit
- **Schema rollback:** `alembic downgrade -1` or `alembic downgrade <specific-revision>`
- **Data restoration:** PostgreSQL WAL backups or point-in-time recovery (infrastructure responsibility)

## Async Patterns & Background Processing

### Connection Management
```python
# FastAPI dependency: get_db() yields async session for each request
# Session auto-commits on success, auto-rollbacks on exception
async def get_db():
    async with async_session() as session:
        yield session
```

### Concurrent Task Update Pattern
```
1. Client sends task update (e.g., change status)
2. API fetches task with current version number
3. API attempts update with WHERE version = current_version
4. If update fails (version mismatch), return 409 Conflict
5. Client retries with fresh version number
```

### Commit Sync (Future Background Job)
```
1. Scheduled job queries all active projects with GitHub repos
2. Fetch commits since last sync timestamp
3. Insert new commits into project_commit_tracking table
4. Trigger KPI recalculation for affected workers
5. Log sync result in audit trail
```

## Error Handling & Retry Logic

### Database Connection Failures
- Retry with exponential backoff (1s, 2s, 4s, 8s max)
- Circuit breaker after 5 consecutive failures
- Return 503 Service Unavailable if DB unavailable

### Validation Errors
- Return 422 Unprocessable Entity with detailed field errors (Pydantic automatic)
- Log validation failures for pattern detection

### Authorization Failures
- Return 403 Forbidden for permission denied
- Log all authorization failures for security audit

### External Service Calls (Git APIs, AI services)
- Retry up to 3 times with exponential backoff
- Timeout after 10 seconds per request
- Fail gracefully if external service unavailable (don't block core operations)

## Open Questions

1. Should audit logs be queryable by end-users or admin-only?
2. What is the retention policy for audit logs? (30 days, 1 year, indefinite?)
3. Should KPI calculations run synchronously (on save) or asynchronously (background job)?
4. What's the expected concurrency level? (10 users, 100, 1000+?)
5. Do we need read replicas for analytics queries, or single PostgreSQL instance sufficient?
