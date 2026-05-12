# SprintFlow Backend API Documentation

## Overview

SprintFlow Backend is a comprehensive FastAPI-based team management and project tracking system. It provides REST APIs for managing projects, tasks, teams, workers, and KPIs with built-in authentication, audit logging, and background job processing.

## Features

- **Authentication & Authorization**: JWT-based authentication with role-based access control (RBAC)
- **Project Management**: Create, update, and track projects with team assignments
- **Task Management**: Comprehensive task lifecycle management with status transitions, comments, and work logs
- **Team Organization**: Team creation, membership management, divisions, and categories
- **Worker Performance**: KPI tracking and manual score adjustments with audit trail
- **Commit Tracking**: GitHub/GitLab integration for commit tracking with worker attribution
- **Audit Logging**: Comprehensive audit trail for all system actions
- **Background Jobs**: Scheduled jobs for commit sync, KPI recalculation, notifications, and log archival

## Technology Stack

- **Framework**: FastAPI 0.100.0+
- **Database**: PostgreSQL with SQLAlchemy ORM 2.0+
- **Async**: asyncio with asyncpg driver
- **Authentication**: JWT tokens (python-jose)
- **Password Security**: bcrypt hashing via passlib
- **Job Scheduler**: APScheduler
- **Validation**: Pydantic v2
- **API Docs**: OpenAPI/Swagger (auto-generated)

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── config.py            # Configuration management
│   ├── databases/           # Database connection & session management
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── base.py          # Base model and mixins
│   │   ├── auth.py          # User, Role, Permission models
│   │   ├── organization.py  # Division, Category, Worker models
│   │   ├── team.py          # Team, TeamMember models
│   │   ├── project.py       # Project, ProjectTask models
│   │   ├── kpi.py           # WorkerKPI models
│   │   ├── audit.py         # Audit logging models
│   │   └── __init__.py      # Model exports
│   ├── routes/              # API endpoint definitions
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── users.py         # User management
│   │   ├── projects.py      # Project CRUD
│   │   ├── tasks.py         # Task management
│   │   ├── roles.py         # Role management
│   │   ├── teams.py         # Team organization
│   │   ├── workers.py       # Worker & KPI management
│   │   ├── commits.py       # Commit tracking
│   │   ├── audit.py         # Audit log endpoints
│   │   └── __init__.py
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── schemas.py       # Pydantic request/response models
│   │   ├── auth.py          # Authentication utilities
│   │   ├── audit.py         # Audit logging utilities
│   │   └── scheduler.py     # Background job scheduler
│   └── scripts/
│       ├── seed_db.py       # Database seeding script
│       └── __init__.py
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_auth.py         # Auth tests
│   ├── test_projects_tasks.py  # Project/Task tests
│   └── test_audit_kpi.py    # Audit/KPI tests
├── alembic/                 # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   ├── versions/
│   └── alembic.ini
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation & Setup

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Git

### 1. Clone Repository

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/sprintflow_db
SECRET_KEY=your-secret-key-here-min-32-chars
DEBUG=False
API_TITLE=SprintFlow
API_VERSION=1.0.0
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 5. Initialize Database

```bash
# Generate migrations
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### 6. Seed Database with Initial Data

```bash
python -m app.scripts.seed_db
```

### 7. Run Application

```bash
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

### Authentication

- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user

### Users & Permissions

- `GET /users/{user_id}` - Get user profile
- `PUT /users/{user_id}` - Update user
- `POST /users/{user_id}/roles` - Assign role
- `DELETE /users/{user_id}/roles/{role_id}` - Remove role
- `GET /users/{user_id}/roles` - List user roles

### Roles & Permissions

- `GET /roles` - List roles
- `POST /roles` - Create role
- `POST /roles/{role_id}/permissions` - Assign permission to role
- `DELETE /roles/{role_id}/permissions/{permission_id}` - Remove permission

### Projects

- `POST /projects` - Create project
- `GET /projects` - List projects (paginated)
- `GET /projects/{project_id}` - Get project
- `PUT /projects/{project_id}` - Update project
- `PATCH /projects/{project_id}/status` - Change status
- `POST /projects/{project_id}/repository` - Link Git repository
- `GET /projects/{project_id}/team` - Get team assignments

### Tasks

- `POST /projects/{project_id}/tasks` - Create task
- `GET /projects/{project_id}/tasks` - List tasks
- `GET /tasks/{task_id}` - Get task
- `PUT /tasks/{task_id}` - Update task
- `PATCH /tasks/{task_id}/status` - Change status
- `PATCH /tasks/{task_id}/assignee` - Reassign task
- `POST /tasks/{task_id}/comments` - Add comment
- `GET /tasks/{task_id}/comments` - List comments
- `POST /tasks/{task_id}/worklog` - Log work hours
- `GET /tasks/{task_id}/history` - View change history

### Teams & Organization

- `POST /teams` - Create team
- `GET /teams` - List teams
- `GET /teams/{team_id}` - Get team
- `PUT /teams/{team_id}` - Update team
- `POST /teams/{team_id}/members` - Add member
- `DELETE /teams/{team_id}/members/{member_id}` - Remove member
- `POST /divisions` - Create division
- `GET /divisions` - List divisions
- `POST /categories` - Create category
- `GET /categories` - List categories

### Workers & KPI

- `POST /workers` - Create worker
- `GET /workers/{worker_id}` - Get worker
- `PUT /workers/{worker_id}` - Update worker
- `POST /workers/{worker_id}/kpi/{project_id}` - Record KPI score
- `GET /workers/{worker_id}/kpi-scores` - View scores
- `PUT /workers/{worker_id}/kpi/{project_id}` - Manual KPI adjustment
- `GET /workers/{worker_id}/kpi-summary` - KPI summary

### Commits

- `POST /projects/{project_id}/commits` - Store commit
- `GET /projects/{project_id}/commits` - List commits
- `GET /commits?message_search={query}` - Search commits
- `POST /commits/{commit_id}/attribution` - Correct attribution
- `GET /projects/{project_id}/commit-stats` - Commit statistics

### Audit Logs

- `GET /audit-logs` - List audit logs (admin)
- `GET /audit-logs/user/{user_id}` - Filter by user
- `GET /audit-logs/action/{action}` - Filter by action
- `GET /audit-logs/resource/{resource_id}` - Filter by resource
- `GET /audit-logs/system` - System audit logs

## Authentication

All endpoints (except `/auth/register` and `/auth/login`) require JWT token in `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Token Lifecycle

- **Access Token**: 15 minutes expiry
- **Refresh Token**: 7 days expiry
- **Refresh Endpoint**: `POST /auth/refresh` with refresh token body

## Error Handling

API returns standard HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict (duplicate resource)
- `500` - Server Error

Error responses include detail message:

```json
{
  "detail": "User not found"
}
```

## Testing

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test File

```bash
pytest tests/test_auth.py
```

### Run with Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

### Test Files

- `tests/conftest.py` - Shared fixtures
- `tests/test_auth.py` - Authentication tests
- `tests/test_projects_tasks.py` - Project/task tests
- `tests/test_audit_kpi.py` - Audit/KPI tests

## Database Migrations

### Create New Migration

```bash
alembic revision --autogenerate -m "Migration description"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

### View Migration History

```bash
alembic current
alembic history
```

## Background Jobs

Jobs run on schedule via APScheduler:

1. **Commit Sync** (every 6 hours) - Fetch commits from GitHub/GitLab
2. **KPI Recalculation** (daily 2 AM) - Recalculate worker performance scores
3. **Deadline Notifications** (daily 8 AM) - Alert for approaching deadlines
4. **Audit Log Archival** (weekly Sunday 3 AM) - Archive old logs

View job status in `GlobalJob` table.

## Performance Optimization

### Connection Pooling

Configured in `app/databases/__init__.py`:
- Pool size: 10
- Max overflow: 20
- Pool timeout: 30 seconds
- Pool recycle: 3600 seconds

### Query Optimization

- Pagination limits: max 100 records
- Indexed columns: user.email, project_id, task_id, worker_id
- Composite indices for common queries

### Caching

- JWT tokens cached in memory (15 min)
- Password hashes use bcrypt with cost factor 12

## Security

### Password Policy

- Minimum 8 characters
- Must contain uppercase, lowercase, numbers (recommended)
- Hashed with bcrypt cost factor 12

### RBAC (Role-Based Access Control)

Three levels:
1. User → Role (many-to-many)
2. Role → Permission (many-to-many)
3. Permission checks on endpoints

### Audit Trail

All modifications logged to:
- `UserLog` - User actions
- `AuditSystemLog` - Sensitive operations
- `CommitChangeLogs` - Commit modifications

### Headers

- CORS: Allow all origins (configure for production)
- Trusted Hosts: localhost, 127.0.0.1 (configure for production)

## Troubleshooting

### Database Connection Issues

Check:
- PostgreSQL is running
- DATABASE_URL is correct
- Network connectivity

```bash
psql postgresql://user:password@localhost:5432/sprintflow_db -c "SELECT 1"
```

### Migration Errors

```bash
# Check current migration state
alembic current

# Downgrade and retry
alembic downgrade -1
alembic upgrade head
```

### Authentication Issues

- Token expired? Use refresh endpoint
- Invalid token? Re-login
- Wrong credentials? Check password policy

### Performance Issues

- Check database query logs
- Monitor connection pool status
- Review pagination limits

## Deployment

See `DEPLOYMENT.md` for production deployment guide.

## Contributing

1. Create feature branch: `git checkout -b feature/name`
2. Make changes and commit: `git commit -am "Description"`
3. Push branch: `git push origin feature/name`
4. Create Pull Request with description

## License

Proprietary - All rights reserved
