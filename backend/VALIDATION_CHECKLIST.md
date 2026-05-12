# Production Deployment Validation Checklist

This checklist ensures all GitLab integration features are properly deployed and validated.

## Task 11.6: Audit Logging Validation

### Verify Audit Logs Record All Operations

```bash
# Query audit logs
psql postgresql://user:password@localhost/sprintflow

-- Check for repository linking operations
SELECT action, user_id, resource_id, severity, created_at 
FROM audit_system_log 
WHERE action LIKE 'gitlab_repository_%' 
ORDER BY created_at DESC LIMIT 10;

-- Expected actions:
-- - gitlab_repository_linked
-- - gitlab_repository_unlinked
-- - gitlab_repository_metadata_updated
```

### Verify Sync Operations Are Logged

```bash
-- Check sync operation logs
SELECT job_name, status, repository_id, commit_count, errors, executed_at
FROM global_job 
WHERE job_name = 'gitlab_sync_repositories' 
ORDER BY executed_at DESC LIMIT 20;

-- Expected status values:
-- - completed (successful)
-- - completed_with_errors (partial success)
-- - failed (total failure)
-- - timeout (exceeded time limit)
```

### Validate Audit Log Details

```bash
-- Check audit log details include necessary information
SELECT id, action, user_id, resource_type, resource_id, details, severity, created_at
FROM audit_system_log 
WHERE action LIKE '%gitlab%' 
LIMIT 5;

-- Details should include:
-- {
--   "gitlab_project_id": 12345,
--   "repository_id": 1,
--   "commits_synced": 42,
--   "duration_seconds": 3.5,
--   "status": "completed"
-- }
```

### Verify No Sensitive Data in Logs

```bash
-- Check that tokens are NOT in logs
SELECT * FROM audit_system_log WHERE details LIKE '%glpat-%';
-- Should return 0 rows

SELECT * FROM audit_system_log WHERE details LIKE '%gAA%';
-- Should return 0 rows (encrypted tokens in Fernet format)
```

### Checklist

- [ ] Sync job records appear in global_job table after each sync
- [ ] Repository linking/unlinking logged to audit_system_log
- [ ] Audit logs include user_id and timestamp
- [ ] Audit logs include operation details (commit counts, errors, etc.)
- [ ] No plaintext GitLab tokens in any logs
- [ ] No API tokens in application logs (check docker-compose logs)
- [ ] Logs use hashes or IDs, not full token values
- [ ] Error details captured without exposing credentials

---

## Task 11.7: Security Review

### Token Encryption Verification

```bash
-- Verify tokens are encrypted in database
psql postgresql://user:password@localhost/sprintflow

SELECT id, gitlab_url, gitlab_access_token 
FROM gitlab_repositories LIMIT 1;

-- Token should look like:
-- gAAAAABnC8X5-JfZ...m6cV1H2Q== (Fernet encrypted)
-- NOT: glpat-xxxxxxxxxxx (plaintext)
```

### Verify Token Scope

```bash
# Test that token has only 'api' scope
curl -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
  https://gitlab.com/api/v4/personal_access_tokens/self | jq '.scopes'

# Should output: ["api"]
# Should NOT include: ["api_write", "write_repository", "sudo", etc.]
```

### Check HTTPS Configuration

```bash
# Verify all external API calls use HTTPS
grep -r "http://" app/ --include="*.py" | grep -v "localhost" | grep -v "127.0.0.1"
# Should return 0 matches for external APIs

grep -r "gitlab_url" app/config.py
# Should show: GITLAB_API_BASE_URL starts with "https://"
```

### Verify No Hardcoded Secrets

```bash
# Check for hardcoded tokens or keys
grep -r "glpat-" . --include="*.py" --include="*.env" --include="*.json"
# Should return 0 matches

grep -r "TOKEN_ENCRYPTION_KEY" . --include="*.py" --exclude-dir=venv
# Should only appear in config.py, not hardcoded values
```

### Database Security

```bash
# Verify database requires authentication
psql -h localhost -U wrong_user -d sprintflow -c "SELECT 1;"
# Should fail with authentication error (not allow access)

# Verify SSL/TLS enabled for database (in production)
grep -i "sslmode" .env
# Should show: sslmode=require (or similar)
```

### Access Control Validation

```bash
# Test that endpoints require authentication
curl http://localhost:8000/api/v1/repositories/gitlab/1
# Should return 401 Unauthorized

curl -H "Authorization: Bearer invalid-token" \
  http://localhost:8000/api/v1/repositories/gitlab/1
# Should return 401 Unauthorized

# Test that non-project-members cannot access
curl -H "Authorization: Bearer ${OTHER_USER_TOKEN}" \
  http://localhost:8000/api/v1/repositories/gitlab/1
# Should return 403 Forbidden (if user not on project)
```

### Encryption Key Security

```bash
# Verify encryption key is not in version control
git log -p -- | grep "TOKEN_ENCRYPTION_KEY" | grep -v ".env.example"
# Should return 0 matches (key not in history)

# Verify .env is in .gitignore
cat .gitignore | grep "\.env"
# Should include .env (but not .env.example)
```

### Checklist

- [ ] All GitLab tokens encrypted in database (Fernet format)
- [ ] Tokens never logged in plaintext
- [ ] API calls use HTTPS (not HTTP)
- [ ] Database connections authenticated and secured
- [ ] No hardcoded secrets in code
- [ ] Access control enforced (auth required, RBAC)
- [ ] Encryption key unique per environment
- [ ] Encryption key stored in vault/secure config
- [ ] Token scope limited to 'api' read-only
- [ ] SSL/TLS enabled for database in production
- [ ] Error messages don't expose tokens or internal details
- [ ] Audit logging captures all auth attempts

---

## Task 11.8: Performance Review

### Database Query Optimization

```bash
-- Verify indexes exist for common queries
psql postgresql://user:password@localhost/sprintflow

-- List all indexes on commits table
\d commits
-- Should show indexes on: repository_id, committed_at, author_email

-- Explain query plans for common operations
EXPLAIN ANALYZE 
SELECT * FROM commits 
WHERE repository_id = 1 
ORDER BY committed_at DESC 
LIMIT 100;
-- Should show "Index Scan" not "Seq Scan"

EXPLAIN ANALYZE 
SELECT author_email, COUNT(*) as count 
FROM commits 
WHERE repository_id = 1 AND committed_at > NOW() - INTERVAL '30 days'
GROUP BY author_email 
ORDER BY count DESC;
-- Should use indexes efficiently
```

### Response Time Analysis

```bash
# Run load test (see load_test.py)
python scripts/load_test.py ${SPRINTFLOW_TOKEN} http://localhost:8000 1

# Expected results:
# - Dashboard metrics endpoint: < 500ms (p95)
# - Commit query endpoint: < 1000ms (p95)
# - Health endpoint: < 200ms (p95)
# - Success rate: > 99%
```

### Database Connection Pooling

```bash
# Check connection pool configuration
grep -i "pool" app/config.py

# Should show appropriate pool sizes:
# - pool_size: 20 (minimum connections to keep)
# - max_overflow: 40 (additional connections allowed)
# - pool_timeout: 30 (seconds to wait for available connection)
```

### Memory Usage

```bash
# Monitor memory during typical operations
docker-compose exec api ps aux | grep uvicorn
# Check RSS column for baseline memory

# Run sync with 1000+ commits
# Monitor memory doesn't exceed 2GB for typical operations
```

### Batch Insert Performance

```bash
# Verify batch insertion is efficient
-- Check commit insert timestamps
SELECT COUNT(*) as count, 
       MIN(created_at) as oldest,
       MAX(created_at) as newest
FROM commits 
WHERE created_at > NOW() - INTERVAL '10 minutes';

-- If 500 commits were synced, verify they have similar timestamps
-- (indicating batch insert) not spread over minutes
```

### Query Performance Benchmarks

```bash
-- Measure query performance
-- Commit frequency calculation
EXPLAIN ANALYZE 
SELECT COUNT(*) as total, 
       COUNT(*)::float / 30 as per_day
FROM commits 
WHERE repository_id = 1 
  AND committed_at > NOW() - INTERVAL '30 days';
-- Should complete in < 100ms

-- Top contributors
EXPLAIN ANALYZE 
SELECT author_email, author_name, COUNT(*) as count 
FROM commits 
WHERE repository_id = 1 
  AND committed_at > NOW() - INTERVAL '30 days'
GROUP BY author_email, author_name 
ORDER BY count DESC 
LIMIT 10;
-- Should complete in < 200ms

-- Velocity calculation (complex aggregation)
EXPLAIN ANALYZE 
SELECT 
  COUNT(*) as current_commits,
  (SELECT COUNT(*) FROM commits 
   WHERE repository_id = 1 
   AND committed_at BETWEEN NOW() - INTERVAL '60 days' AND NOW() - INTERVAL '30 days')
  as previous_commits;
-- Should complete in < 300ms
```

### Concurrent Load Performance

```bash
# Run multiple concurrent requests
for i in {1..10}; do
  curl -s "http://localhost:8000/api/v1/dashboard/gitlab-metrics/1?days=30" \
    -H "Authorization: Bearer ${TOKEN}" &
done
wait

# All requests should complete with < 1s response time
# Server should handle without connection errors
```

### Checklist

- [ ] Database indexes created on: repository_id, committed_at, author_email, git_hash
- [ ] Query plans show Index Scans, not Seq Scans
- [ ] Commit frequency query: < 100ms
- [ ] Top contributors query: < 200ms
- [ ] Health status query: < 100ms
- [ ] Batch inserts complete commits in < 5 seconds per 500 commits
- [ ] Dashboard metrics endpoint: p95 < 500ms
- [ ] Commit query endpoint: p95 < 1000ms
- [ ] Connection pooling configured appropriately
- [ ] Memory usage stable under load (< 2GB)
- [ ] No N+1 query problems
- [ ] Pagination works correctly for large result sets
- [ ] Query results properly cached where applicable

---

## Sign-Off

- [ ] All audit logging validated
- [ ] All security checks passed
- [ ] All performance benchmarks met
- [ ] Ready for production deployment

**Validated By**: ___________________  
**Date**: ___________________  
**Sign-Off**: ___________________  

---

For detailed validation procedures, see:
- [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)
- [E2E_TESTING.md](./E2E_TESTING.md)
- [TESTING.md](./TESTING.md)
