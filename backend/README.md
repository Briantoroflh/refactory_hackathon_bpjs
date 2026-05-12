# SprintFlow Backend

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13%2B-336791)

SprintFlow is a comprehensive project management and AI-powered workflow platform. The backend provides REST APIs for project management, team collaboration, task tracking, and **real-time GitLab integration** for commit analysis and team metrics.

## 🚀 Features

### Core Features
- **Project Management**: Create, organize, and track projects with team collaboration
- **Sprint Management**: Plan sprints, track velocity, and manage capacity
- **Task Tracking**: Detailed task management with dependencies, estimates, and assignments
- **Team Management**: Team organization, role-based access control (RBAC)
- **User Management**: User profiles, authentication, and authorization
- **Audit Logging**: Comprehensive audit trails for compliance and debugging
- **Role-Based Access**: Project owner, team lead, contributor, and viewer roles

### 🆕 GitLab Integration
- **Automatic Commit Sync**: Fetch commits from GitLab repositories every 15 minutes
- **Repository Linking**: Link GitLab projects to SprintFlow projects (1-to-1 mapping)
- **Commit Analytics**: View commit frequency, velocity trends, and contributor metrics
- **Team Metrics**: Identify top contributors and track development activity
- **Branch Analysis**: Monitor activity across development branches
- **Health Monitoring**: Repository health status based on recent activity
- **Secure Token Storage**: GitLab API tokens encrypted at rest using Fernet
- **Audit Trail**: All GitLab operations logged for security and compliance

### AI-Powered Features
- **OpenRouter Integration**: AI assistant for workflow recommendations and planning
- **Intelligent Planning**: Get AI-powered project planning suggestions
- **Team Analytics**: AI-driven insights on team productivity and velocity
- **Fallback Mode**: Built-in fallback responses when AI service is unavailable

## 🏗️ Architecture

```
Backend API (FastAPI)
├── Routes (HTTP endpoints)
├── Controllers (Business logic)
├── Services (Data processing & external APIs)
├── Models (Database schema - SQLAlchemy ORM)
├── Schemas (Request/response validation - Pydantic)
└── Database (PostgreSQL with Alembic migrations)

Background Jobs (APScheduler)
├── GitLab Commit Synchronization (every 15 min)
├── KPI Recalculation
├── Deadline Notifications
├── GitHub Commit Sync
└── Audit Log Cleanup

External Integrations
├── GitLab API (python-gitlab)
├── GitHub API (PyGithub)
└── OpenRouter AI (LLM API)
```

## 📋 Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Web Framework | FastAPI | 0.100.0+ |
| ORM | SQLAlchemy | 2.0+ |
| Database | PostgreSQL | 13+ |
| Async Runtime | asyncpg | Latest |
| Job Scheduler | APScheduler | 3.11.2+ |
| GitLab Client | python-gitlab | 3.0+ |
| Encryption | cryptography | 48.0.0+ |
| AI Integration | OpenRouter API | Latest |
| Testing | pytest | Latest |
| Documentation | OpenAPI/Swagger | Auto-generated |

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 13+
- Docker & Docker Compose (recommended)

### Installation

**Option 1: Docker (Recommended)**
```bash
docker-compose up --build
```

**Option 2: Local Development**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
python -m alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

### Configuration

Create `.env` file in the backend directory (copy from `.env.example`):

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/sprintflow

# JWT
SECRET_KEY=your-secret-key-here

# OpenRouter (AI Integration)
OPENROUTER_ENABLED=false  # Start disabled for testing
OPENROUTER_API_KEY=sk_xxxx
OPENROUTER_MODEL=nvidia/nemotron-3-super-120b-a12b:free

# GitLab Integration
GITLAB_API_BASE_URL=https://gitlab.com
GITLAB_SYNC_INTERVAL_MINUTES=15
GITLAB_ENABLE_AUTO_SYNC=True
TOKEN_ENCRYPTION_KEY=<generated-key>

# GitHub Integration (optional)
GITHUB_API_KEY=ghp_xxxx
```

#### Generate Encryption Key for GitLab Integration
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the output to `TOKEN_ENCRYPTION_KEY` in `.env`.

## 📚 API Documentation

### Interactive API Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main API Endpoints

#### Projects
```
POST   /api/v1/projects                 # Create project
GET    /api/v1/projects                 # List projects
GET    /api/v1/projects/{id}            # Get project details
PUT    /api/v1/projects/{id}            # Update project
DELETE /api/v1/projects/{id}            # Delete project
```

#### GitLab Integration
```
POST   /api/v1/repositories/gitlab/link/{project_id}     # Link repository
GET    /api/v1/repositories/gitlab/{project_id}          # Get linked repository
DELETE /api/v1/repositories/gitlab/{project_id}          # Unlink repository
POST   /api/v1/repositories/gitlab/sync/{project_id}     # Trigger manual sync
GET    /api/v1/commits                                   # List commits
GET    /api/v1/dashboard/gitlab-metrics/{project_id}     # Get metrics
```

#### Sprints
```
POST   /api/v1/sprints                  # Create sprint
GET    /api/v1/sprints                  # List sprints
GET    /api/v1/sprints/{id}             # Get sprint details
PUT    /api/v1/sprints/{id}             # Update sprint
DELETE /api/v1/sprints/{id}             # Delete sprint
```

#### Tasks
```
POST   /api/v1/tasks                    # Create task
GET    /api/v1/tasks                    # List tasks
GET    /api/v1/tasks/{id}               # Get task details
PUT    /api/v1/tasks/{id}               # Update task
DELETE /api/v1/tasks/{id}               # Delete task
```

#### Teams
```
POST   /api/v1/teams                    # Create team
GET    /api/v1/teams                    # List teams
GET    /api/v1/teams/{id}               # Get team details
PUT    /api/v1/teams/{id}               # Update team
DELETE /api/v1/teams/{id}               # Delete team
```

#### Authentication
```
POST   /auth/register                   # Register new user
POST   /auth/login                      # Login (get JWT token)
POST   /auth/refresh                    # Refresh JWT token
POST   /auth/logout                     # Logout
```

#### AI Assistant
```
POST   /ai-assistant/planning           # Get planning suggestions
POST   /ai-assistant/sprint-summary     # Get sprint summary
POST   /ai-assistant/health             # Get AI service health
```

For full API documentation, see [API_DOCUMENTATION.md](./API_DOCUMENTATION.md).

## 🔗 GitLab Integration Guide

### Features
- **Automatic Sync**: Background job fetches commits every 15 minutes
- **Commit Tracking**: View all commits with filtering and search
- **Team Metrics**: Top contributors, commit frequency, velocity trends
- **Repository Health**: Monitor activity and identify stale repositories
- **Secure Tokens**: GitLab API tokens encrypted using Fernet
- **Audit Logging**: All operations logged for compliance

### Quick Setup
1. Create GitLab API token at https://gitlab.com/profile/personal_access_tokens
2. Link repository via API: `POST /api/v1/repositories/gitlab/link/{project_id}`
3. View commits: `GET /api/v1/commits?project_id={id}`
4. See metrics: `GET /api/v1/dashboard/gitlab-metrics/{project_id}`

For detailed setup instructions, see [GITLAB_INTEGRATION.md](./GITLAB_INTEGRATION.md).

### Security Features
- ✅ Token encryption at rest (Fernet)
- ✅ Tokens decrypted only when needed
- ✅ Audit trail for all operations
- ✅ Role-based access control
- ✅ HTTPS in production
- ✅ Secure token generation

## 📊 Database Schema

### Core Tables
- **projects**: Project metadata and configuration
- **teams**: Team organization and membership
- **users**: User profiles and authentication
- **tasks**: Task items with estimates and assignments
- **sprints**: Sprint planning and tracking
- **roles**: Role definitions and permissions

### GitLab Integration Tables
- **gitlab_repositories**: Linked GitLab repositories
- **commits**: Synced commit data (100,000+ entries possible)
- **global_job**: Background job execution logs
- **audit_system_log**: Comprehensive audit trail

### Database Migrations
All database changes are managed through Alembic migrations:

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View current version
alembic current
```

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_gitlab_sync.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

### Test Categories
- **Unit Tests**: Service layer logic, utilities, calculations
- **Integration Tests**: API endpoints, database operations
- **E2E Tests**: Complete user workflows

### Test Files (GitLab Integration)
- `test_gitlab_client.py`: GitLab API client tests
- `test_gitlab_sync.py`: Commit sync logic tests
- `test_gitlab_api.py`: API endpoint tests
- `test_commit_analytics.py`: Metrics calculation tests

## 🔄 Background Jobs

### APScheduler Jobs
The application initializes 5 background jobs:

1. **gitlab_sync_repositories** (every 15 min)
   - Fetches new commits from linked GitLab repositories
   - Detects duplicates and updates metrics
   - Logs all operations to GlobalJob table

2. **fetch_commits_from_github** (every 30 min)
   - Similar to GitLab, for GitHub repositories

3. **recalculate_worker_kpi** (daily at 2 AM)
   - Recalculates team KPIs and metrics
   - Updates performance indicators

4. **send_deadline_notifications** (hourly)
   - Sends notifications for upcoming deadlines
   - Triggers task escalation

5. **archive_old_audit_logs** (weekly)
   - Archives audit logs older than 1 year
   - Maintains database performance

### Monitoring Job Health
```bash
# Check job execution logs
SELECT * FROM global_job 
WHERE job_name = 'gitlab_sync_repositories' 
ORDER BY executed_at DESC LIMIT 10;

# Check for failures
SELECT * FROM global_job 
WHERE status = 'failed' 
AND executed_at > NOW() - INTERVAL '24 hours';
```

## 📈 Performance Optimization

### Database Indexes
All frequently queried columns are indexed:
- `commits.repository_id`
- `commits.committed_at`
- `commits.author_email`
- `tasks.project_id`
- `tasks.assigned_to`
- `sprints.project_id`

### Query Optimization
- Async SQLAlchemy for non-blocking database operations
- Connection pooling with configurable pool size
- Batch inserts for large commit imports (500 at a time)
- Query result caching where appropriate

### Caching Strategy
- In-memory cache for frequently accessed data
- Dashboard metrics cached for 5 minutes (configurable)
- Consider Redis for distributed caching in production

### Performance Targets
- API response times: < 500ms (p95)
- Dashboard metrics: < 2 seconds
- Commit sync: < 30 seconds for typical repositories
- GitLab API calls: < 5 seconds (including network)

## 🐛 Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check DATABASE_URL in .env
# Verify PostgreSQL is running
docker-compose logs db

# Test connection
psql postgresql://user:password@localhost/sprintflow
```

**GitLab Sync Not Running**
```bash
# Check if APScheduler initialized
docker-compose logs api | grep -i scheduler

# Check GITLAB_ENABLE_AUTO_SYNC=True
echo $GITLAB_ENABLE_AUTO_SYNC

# Manually trigger sync
curl -X POST http://localhost:8000/api/v1/repositories/gitlab/sync/1 \
  -H "Authorization: Bearer $TOKEN"
```

**Invalid GitLab Token**
```bash
# Verify token is correct
curl -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  https://gitlab.com/api/v4/user

# Check token expiration and scopes
# Regenerate if needed
```

**API Returns 401 Unauthorized**
```bash
# Check JWT secret is consistent
# Get new access token: POST /auth/login
# Use access token (not refresh token) in header
```

For more troubleshooting, see:
- [GITLAB_INTEGRATION.md](./GITLAB_INTEGRATION.md) - GitLab-specific issues
- [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) - Deployment problems
- [AI_ASSISTANT_RUNBOOK.md](./AI_ASSISTANT_RUNBOOK.md) - AI integration issues

## 📝 Documentation

- **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)** - Complete REST API reference
- **[GITLAB_INTEGRATION.md](./GITLAB_INTEGRATION.md)** - GitLab setup and usage
- **[DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)** - Deployment guide
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Docker deployment instructions
- **[AI_ASSISTANT_RUNBOOK.md](./AI_ASSISTANT_RUNBOOK.md)** - AI assistant operations
- **[IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md)** - Feature implementation progress

## 🔐 Security

### Authentication
- JWT tokens for API authentication
- Refresh token rotation
- Secure password hashing (bcrypt)
- Session management

### Data Protection
- API tokens encrypted using Fernet (AES-128)
- Secure transmission via HTTPS (in production)
- Database encryption at rest
- Audit logging for compliance

### Access Control
- Role-based access control (RBAC)
- Project-level permissions
- API rate limiting
- Request validation with Pydantic

## 📦 Deployment

### Docker Deployment
```bash
# Build image
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Environment-Specific Configuration
```bash
# Development
cp .env.example .env
# Edit .env with development values

# Staging
export ENVIRONMENT=staging
# Use staging-specific values

# Production
export ENVIRONMENT=production
# Use secure vault for secrets
```

For complete deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md).

## 🤝 Contributing

### Code Style
- Follow PEP 8 for Python code
- Use type hints for all functions
- Write docstrings for all public methods
- Keep functions focused and testable

### Before Submitting PR
1. Run tests: `pytest tests/ -v`
2. Check code style: `flake8 app/`
3. Run type checker: `mypy app/`
4. Update documentation if needed
5. Add tests for new features

## 📞 Support

For issues and questions:
1. Check [GITLAB_INTEGRATION.md](./GITLAB_INTEGRATION.md) troubleshooting section
2. Review [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) for deployment issues
3. Check application logs: `docker-compose logs api`
4. Open an issue on the project repository

## 📄 License

[License information to be added]

## 🎯 Roadmap

### Completed ✅
- Core project management
- Team collaboration
- Sprint planning and tracking
- Task management with dependencies
- User authentication and RBAC
- GitLab integration with commit sync
- AI-powered workflow assistant
- Comprehensive audit logging
- Docker deployment
- API documentation

### In Progress 🔄
- Frontend dashboard redesign
- Advanced analytics and KPI tracking
- Webhook integrations
- Real-time notifications (WebSocket)

### Planned 📅
- Mobile app
- Jira integration
- Slack integration
- Microsoft Teams integration
- Custom workflow automation
- Advanced reporting and exports

---

**Version**: 1.0.0  
**Last Updated**: May 12, 2026  
**Status**: Production Ready ✅

For more information, visit https://sprintflow.io or contact dev-team@sprintflow.io
