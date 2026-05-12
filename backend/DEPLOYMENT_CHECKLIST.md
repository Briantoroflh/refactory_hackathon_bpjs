# GitLab Integration Deployment Checklist

**Purpose**: Ensure GitLab integration is properly deployed and validated before production release.

## Pre-Deployment Validation

### Code & Dependencies
- [ ] All code changes committed to version control
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Python version >= 3.10 verified
- [ ] All imports resolve without errors

### Database Migrations
- [ ] Migration file exists: `alembic/versions/*_add_gitlab_*.py`
- [ ] Migration forward tested: `alembic upgrade head`
- [ ] Migration rollback tested: `alembic downgrade -1`
- [ ] Tables created correctly:
  - [ ] `gitlab_repositories` table exists with correct schema
  - [ ] `commits` table exists with correct schema and indexes
  - [ ] Foreign key constraints verified
  - [ ] Unique constraints verified

### Environment Configuration
- [ ] `.env` file has GitLab settings:
  - [ ] `GITLAB_API_BASE_URL` set to correct GitLab instance
  - [ ] `GITLAB_SYNC_INTERVAL_MINUTES` set (recommend 15-60 min)
  - [ ] `GITLAB_ENABLE_AUTO_SYNC` set to True/False as desired
  - [ ] `TOKEN_ENCRYPTION_KEY` set to secure value
- [ ] `.env` is NOT committed to version control
- [ ] Environment variables are documented in `.env.example`

### Security Review
- [ ] API tokens are encrypted before storage (using cryptography.Fernet)
- [ ] Token decryption only happens during API calls
- [ ] Tokens are never logged in plain text
- [ ] Error messages don't expose sensitive information
- [ ] SQL injection vulnerabilities checked
- [ ] Rate limiting configured for API endpoints

## Deployment Steps

### 1. Database Preparation
```bash
# Backup current database
pg_dump <database_url> > backup_before_gitlab.sql

# Run migrations
cd backend
python -m alembic upgrade head
```

### 2. APScheduler Verification
- [ ] APScheduler dependency installed
- [ ] Scheduler starts during app startup
- [ ] Log shows "Background job scheduler initialized with 5 jobs"
- [ ] Check that scheduler has jobs:
  - [ ] fetch_commits_from_github
  - [ ] recalculate_worker_kpi
  - [ ] send_deadline_notifications
  - [ ] archive_old_audit_logs
  - [ ] gitlab_sync_repositories

### 3. Service Validation
- [ ] FastAPI app starts without errors
- [ ] All routes registered: `openapi.json` endpoint works
- [ ] GitLab routes available:
  - [ ] POST /api/v1/repositories/gitlab/link/{project_id}
  - [ ] GET /api/v1/repositories/gitlab/{project_id}
  - [ ] DELETE /api/v1/repositories/gitlab/{project_id}
  - [ ] POST /api/v1/repositories/gitlab/sync/{project_id}
  - [ ] GET /api/v1/commits
  - [ ] GET /api/v1/dashboard/gitlab-metrics/{project_id}

### 4. GitLab API Testing
- [ ] GitLab API token generated and valid
- [ ] API token has correct scopes (api read access)
- [ ] Connection to GitLab tested:
  ```bash
  curl -H "PRIVATE-TOKEN: <token>" https://gitlab.com/api/v4/user
  ```
- [ ] Firewall rules allow outbound connections to GitLab
- [ ] Rate limits understood (usually 600 req/min)

### 5. End-to-End Testing
```bash
# 1. Link a test repository
curl -X POST http://localhost:8000/api/v1/repositories/gitlab/link/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "gitlab_project_id": <project_id>,
    "gitlab_url": "https://gitlab.com",
    "gitlab_token": "<api_token>"
  }'

# 2. Verify repository was linked
curl http://localhost:8000/api/v1/repositories/gitlab/1 \
  -H "Authorization: Bearer <token>"

# 3. Trigger manual sync
curl -X POST http://localhost:8000/api/v1/repositories/gitlab/sync/1 \
  -H "Authorization: Bearer <token>"

# 4. Check commits were synced
curl "http://localhost:8000/api/v1/commits?project_id=1" \
  -H "Authorization: Bearer <token>"

# 5. View dashboard metrics
curl http://localhost:8000/api/v1/dashboard/gitlab-metrics/1 \
  -H "Authorization: Bearer <token>"
```

- [ ] Repository linked successfully
- [ ] Commits synced without errors
- [ ] Commits visible in queries
- [ ] Dashboard metrics calculated correctly

### 6. Background Job Validation
- [ ] Check GlobalJob table for sync status:
  ```sql
  SELECT * FROM global_job WHERE job_name = 'gitlab_sync_repositories' 
  ORDER BY executed_at DESC LIMIT 5;
  ```
- [ ] Recent sync job entries exist
- [ ] Status shows "completed" or "completed_with_errors"
- [ ] No "failed" status entries

### 7. Audit Logging Validation
- [ ] Check AuditSystemLog table:
  ```sql
  SELECT * FROM audit_system_log 
  WHERE action LIKE '%gitlab%' 
  ORDER BY created_at DESC LIMIT 10;
  ```
- [ ] Repository link action logged
- [ ] Repository unlink action logged
- [ ] Sync actions logged
- [ ] User information captured

### 8. Performance Testing
- [ ] Dashboard metrics endpoint responds < 500ms
- [ ] Commit list endpoint with 1000+ commits < 1s
- [ ] Database queries use indexes:
  ```sql
  EXPLAIN ANALYZE 
  SELECT * FROM commits 
  WHERE repository_id = 1 
  ORDER BY committed_at DESC;
  ```
- [ ] Query plans use index scans, not seq scans

## Post-Deployment Monitoring

### Health Checks (First 24 Hours)
- [ ] Monitor application logs for errors
- [ ] Check sync job executes every N minutes
- [ ] Verify no sync failures in GlobalJob table
- [ ] Monitor database connections are stable
- [ ] Watch for GitLab API rate limit issues

### Long-Term Monitoring
- [ ] Set up alerts for:
  - [ ] Sync job failures (check GlobalJob.status)
  - [ ] Database connection pool exhaustion
  - [ ] Slow queries (> 1 second)
  - [ ] High error rates on API endpoints
  - [ ] GitLab API authentication failures

### Metrics to Track
- [ ] Average sync time per repository
- [ ] Total commits synced per day
- [ ] Number of repositories linked
- [ ] API response times (p50, p95, p99)
- [ ] Database query times by endpoint

## Rollback Plan

If issues arise during deployment:

### 1. Stop the application
```bash
pkill -f "uvicorn"
```

### 2. Rollback database
```bash
# Rollback one migration
cd backend
python -m alembic downgrade -1

# Or restore from backup
psql <database_url> < backup_before_gitlab.sql
```

### 3. Revert code
```bash
git revert <commit_hash>
git push
```

### 4. Restart application
```bash
# After code revert
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Docker Deployment

If using Docker:

### 1. Update docker-compose.yml
```yaml
services:
  backend:
    environment:
      GITLAB_API_BASE_URL: ${GITLAB_API_BASE_URL}
      GITLAB_SYNC_INTERVAL_MINUTES: ${GITLAB_SYNC_INTERVAL_MINUTES}
      GITLAB_ENABLE_AUTO_SYNC: ${GITLAB_ENABLE_AUTO_SYNC}
      TOKEN_ENCRYPTION_KEY: ${TOKEN_ENCRYPTION_KEY}
```

### 2. Update .env for Docker
```bash
GITLAB_API_BASE_URL=https://gitlab.com
GITLAB_SYNC_INTERVAL_MINUTES=15
GITLAB_ENABLE_AUTO_SYNC=True
TOKEN_ENCRYPTION_KEY=<secure-key>
```

### 3. Deploy
```bash
docker-compose down
docker-compose up -d

# Verify
docker-compose logs backend | grep "scheduler initialized"
```

## Known Issues & Troubleshooting

### Issue: "UndefinedColumnError: column id referenced in foreign key constraint does not exist"
**Solution**: Migration foreign key was referencing `projects.id` but should be `projects.project_id`. Fixed in migration file.

### Issue: APScheduler job not running
**Solutions**:
- Verify `GITLAB_ENABLE_AUTO_SYNC=True`
- Check logs for "Background job scheduler initialized"
- Verify no errors in scheduler initialization
- Ensure AsyncIOScheduler is properly initialized

### Issue: "Invalid GitLab credentials"
**Solutions**:
- Verify token is correct and not expired
- Verify token has `api` scope
- Check GITLAB_API_BASE_URL is correct
- Verify firewall allows outbound connections to GitLab

### Issue: Commits not syncing
**Solutions**:
- Run manual sync: `POST /api/v1/repositories/gitlab/sync/{project_id}`
- Check GlobalJob table for errors
- Verify repository is properly linked
- Check GitLab project ID is correct
- Verify API token has access to the project

### Issue: Encryption key errors
**Solutions**:
- Generate new key: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- Update TOKEN_ENCRYPTION_KEY in .env
- Re-encrypt existing tokens or clear and re-link repositories

## Sign-Off Checklist

- [ ] All tests passing
- [ ] Code review completed
- [ ] Security review completed
- [ ] Performance testing passed
- [ ] Documentation updated
- [ ] Team trained on new features
- [ ] Monitoring configured
- [ ] Rollback plan documented and tested
- [ ] Deployment scheduled for low-traffic window

**Deployed By**: _________________  
**Date**: _________________  
**Verified By**: _________________  
**Date**: _________________

---

For detailed setup instructions, see [GITLAB_INTEGRATION.md](./GITLAB_INTEGRATION.md)
