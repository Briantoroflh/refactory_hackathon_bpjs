# End-to-End Testing Guide for GitLab Integration

**Purpose**: Validate that the complete GitLab integration workflow works with a real GitLab project.

## Prerequisites

Before running E2E tests, you'll need:

1. **GitLab Account** - Access to a GitLab instance (gitlab.com or self-hosted)
2. **Test Project** - A GitLab project you can link (preferably a test project)
3. **API Token** - GitLab personal access token with `api` scope
4. **Project ID** - The numeric ID of your test GitLab project
5. **SprintFlow Project ID** - The numeric ID of a project in SprintFlow
6. **Valid JWT Token** - Access token for SprintFlow API

## Step 1: Generate Required Tokens

### Generate GitLab API Token

```bash
# 1. Navigate to GitLab account settings
https://gitlab.com/profile/personal_access_tokens

# 2. Click "Add new token"
Token Name: sprintflow-e2e-test
Expiration Date: 30 days from now
Scopes: api (read-only)

# 3. Copy the token immediately
export GITLAB_TOKEN="glpat-xxxxxxxxxxx"

# 4. Save Project ID
export GITLAB_PROJECT_ID=12345  # Replace with your project ID
```

### Get SprintFlow Access Token

```bash
# 1. Login to SprintFlow
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-password"
  }'

# 2. Copy the access_token from response
export SPRINTFLOW_TOKEN="eyJ0eXAiOiJKV1QiLC..."

# 3. Note your SprintFlow project ID
export SPRINTFLOW_PROJECT_ID=1
```

## Step 2: Link Repository to Project

### Test Repository Linking Endpoint

```bash
# Link the GitLab repository
curl -X POST \
  "http://localhost:8000/api/v1/repositories/gitlab/link/${SPRINTFLOW_PROJECT_ID}" \
  -H "Authorization: Bearer ${SPRINTFLOW_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "gitlab_project_id": '"${GITLAB_PROJECT_ID}"',
    "gitlab_url": "https://gitlab.com",
    "gitlab_token": "'"${GITLAB_TOKEN}"'"
  }'

# Expected Response (201 Created):
# {
#   "id": 1,
#   "project_id": 1,
#   "gitlab_project_id": 12345,
#   "gitlab_url": "https://gitlab.com",
#   "last_sync_timestamp": null,
#   "created_at": "2026-05-12T10:30:00Z",
#   "status": "linked"
# }
```

### Verify Linking in Database

```bash
# Connect to PostgreSQL
psql postgresql://user:password@localhost/sprintflow

# Check linked repository
SELECT id, project_id, gitlab_project_id, status, created_at
FROM gitlab_repositories
WHERE project_id = 1;
```

**Expected**: Should show 1 row with status "linked"

## Step 3: Manually Trigger Sync

### Trigger Manual Sync

```bash
# Request manual sync
curl -X POST \
  "http://localhost:8000/api/v1/repositories/gitlab/sync/${SPRINTFLOW_PROJECT_ID}" \
  -H "Authorization: Bearer ${SPRINTFLOW_TOKEN}"

# Expected Response (200 OK):
# {
#   "status": "success",
#   "repository_id": 1,
#   "commits_synced": 42,
#   "duration_seconds": 3.5,
#   "message": "Sync completed successfully"
# }
```

### Monitor Sync Progress

```bash
# Check GlobalJob table for sync records
psql postgresql://user:password@localhost/sprintflow

SELECT id, job_name, status, commit_count, executed_at, duration_seconds
FROM global_job
WHERE job_name = 'gitlab_sync_repositories'
ORDER BY executed_at DESC
LIMIT 5;
```

**Expected**: Should show recent sync with:
- status: "completed"
- commit_count: > 0
- duration_seconds: < 30 (for typical repos)

## Step 4: Verify Commits Were Synced

### Check Commits in Database

```bash
# Query commits in database
psql postgresql://user:password@localhost/sprintflow

SELECT COUNT(*) as total_commits,
       MIN(committed_at) as oldest_commit,
       MAX(committed_at) as newest_commit
FROM commits
WHERE repository_id = 1;
```

**Expected**: Should show commits from GitLab project

### Query Commits via API

```bash
# Get commits with filtering
curl "http://localhost:8000/api/v1/commits?project_id=${SPRINTFLOW_PROJECT_ID}&days=30" \
  -H "Authorization: Bearer ${SPRINTFLOW_TOKEN}" | jq .

# Expected Response:
# {
#   "total": 42,
#   "items": [
#     {
#       "id": 1,
#       "repository_id": 1,
#       "git_hash": "abc123def456",
#       "message": "Commit message",
#       "author_name": "John Doe",
#       "author_email": "john@example.com",
#       "committed_at": "2026-05-12T09:30:00Z",
#       "branch": "main"
#     },
#     ...
#   ]
# }
```

**Expected**: Should contain commits from GitLab project

## Step 5: Check Dashboard Metrics

### Get Dashboard Metrics

```bash
# Get comprehensive metrics
curl "http://localhost:8000/api/v1/dashboard/gitlab-metrics/${SPRINTFLOW_PROJECT_ID}?days=30" \
  -H "Authorization: Bearer ${SPRINTFLOW_TOKEN}" | jq .

# Expected Response:
# {
#   "repository_health": {
#     "status": "healthy",
#     "last_activity": "2026-05-12T15:00:00Z"
#   },
#   "commit_frequency": {
#     "total": 42,
#     "per_day": 1.4
#   },
#   "top_contributors": [
#     {
#       "author_email": "john@example.com",
#       "author_name": "John Doe",
#       "commit_count": 25
#     },
#     {
#       "author_email": "jane@example.com",
#       "author_name": "Jane Doe",
#       "commit_count": 17
#     }
#   ],
#   "velocity": {
#     "trend": "stable",
#     "current_commits": 42,
#     "previous_commits": 40,
#     "change_percent": 5.0
#   },
#   "branch_activity": [
#     {
#       "branch": "main",
#       "commit_count": 30
#     },
#     {
#       "branch": "develop",
#       "commit_count": 12
#     }
#   ]
# }
```

**Expected**: All metrics populated with GitLab data

### Verify Individual Metrics Endpoints

```bash
# Get commit frequency only
curl "http://localhost:8000/api/v1/dashboard/gitlab-metrics/${SPRINTFLOW_PROJECT_ID}/frequency" \
  -H "Authorization: Bearer ${SPRINTFLOW_TOKEN}" | jq .

# Get velocity metrics
curl "http://localhost:8000/api/v1/dashboard/gitlab-metrics/${SPRINTFLOW_PROJECT_ID}/velocity" \
  -H "Authorization: Bearer ${SPRINTFLOW_TOKEN}" | jq .

# Get repository health
curl "http://localhost:8000/api/v1/dashboard/gitlab-metrics/${SPRINTFLOW_PROJECT_ID}/health" \
  -H "Authorization: Bearer ${SPRINTFLOW_TOKEN}" | jq .
```

## Step 6: Verify Audit Logging

### Check Audit Trail

```bash
# Query audit logs for GitLab operations
psql postgresql://user:password@localhost/sprintflow

SELECT action, user_id, severity, created_at
FROM audit_system_log
WHERE action LIKE '%gitlab%' OR action LIKE '%sync%'
ORDER BY created_at DESC
LIMIT 20;
```

**Expected**: Should show:
- `gitlab_repository_linked` - When repository was linked
- `gitlab_sync_started` - When sync began
- `gitlab_sync_completed` - When sync finished
- User information for all operations

## Troubleshooting

### Issue: "Invalid GitLab credentials"

```bash
# Verify token is correct
curl -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
  https://gitlab.com/api/v4/user

# Should return user info, not 401
```

### Issue: "Repository not found"

```bash
# Verify project ID is correct
curl -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
  "https://gitlab.com/api/v4/projects/${GITLAB_PROJECT_ID}"

# Should return project details
```

### Issue: "No commits synced"

```bash
# Check if GitLab project has commits
curl -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
  "https://gitlab.com/api/v4/projects/${GITLAB_PROJECT_ID}/repository/commits?per_page=1"

# Should return at least one commit
```

### Issue: "Metrics endpoint returns empty"

```bash
# Verify commits exist in database
psql postgresql://user:password@localhost/sprintflow

SELECT COUNT(*) FROM commits WHERE repository_id = 1;

# Should return > 0
```

## Full E2E Test Script

```bash
#!/bin/bash
# E2E_TEST.sh - Complete end-to-end test

set -e

echo "Starting E2E Test..."
echo "===================="
echo ""

# Step 1: Link repository
echo "Step 1: Linking GitLab repository..."
LINK_RESPONSE=$(curl -s -X POST \
  "http://localhost:8000/api/v1/repositories/gitlab/${SPRINTFLOW_PROJECT_ID}" \
  -H "Authorization: Bearer ${SPRINTFLOW_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "gitlab_project_id": '"${GITLAB_PROJECT_ID}"',
    "gitlab_url": "https://gitlab.com",
    "gitlab_token": "'"${GITLAB_TOKEN}"'"
  }')

if echo "$LINK_RESPONSE" | grep -q '"status":"linked"'; then
  echo "✓ Repository linked successfully"
else
  echo "✗ Failed to link repository"
  echo "$LINK_RESPONSE"
  exit 1
fi
echo ""

# Step 2: Trigger manual sync
echo "Step 2: Triggering manual sync..."
SYNC_RESPONSE=$(curl -s -X POST \
  "http://localhost:8000/api/v1/repositories/gitlab/sync/${SPRINTFLOW_PROJECT_ID}" \
  -H "Authorization: Bearer ${SPRINTFLOW_TOKEN}")

if echo "$SYNC_RESPONSE" | grep -q '"status":"success"'; then
  COMMITS=$(echo "$SYNC_RESPONSE" | grep -o '"commits_synced":[0-9]*' | grep -o '[0-9]*')
  echo "✓ Sync completed - $COMMITS commits synced"
else
  echo "✗ Sync failed"
  echo "$SYNC_RESPONSE"
  exit 1
fi
echo ""

# Step 3: Query commits via API
echo "Step 3: Querying commits via API..."
COMMITS_RESPONSE=$(curl -s "http://localhost:8000/api/v1/commits?project_id=${SPRINTFLOW_PROJECT_ID}&days=30" \
  -H "Authorization: Bearer ${SPRINTFLOW_TOKEN}")

if echo "$COMMITS_RESPONSE" | grep -q '"total"'; then
  TOTAL=$(echo "$COMMITS_RESPONSE" | grep -o '"total":[0-9]*' | grep -o '[0-9]*')
  echo "✓ Commits query successful - $TOTAL total commits"
else
  echo "✗ Commits query failed"
  echo "$COMMITS_RESPONSE"
  exit 1
fi
echo ""

# Step 4: Get dashboard metrics
echo "Step 4: Getting dashboard metrics..."
METRICS_RESPONSE=$(curl -s "http://localhost:8000/api/v1/dashboard/gitlab-metrics/${SPRINTFLOW_PROJECT_ID}?days=30" \
  -H "Authorization: Bearer ${SPRINTFLOW_TOKEN}")

if echo "$METRICS_RESPONSE" | grep -q '"repository_health"'; then
  echo "✓ Dashboard metrics retrieved successfully"
  echo "$METRICS_RESPONSE" | jq '.repository_health, .commit_frequency'
else
  echo "✗ Dashboard metrics retrieval failed"
  echo "$METRICS_RESPONSE"
  exit 1
fi
echo ""

echo "===================="
echo "✓ All E2E tests passed!"
```

## Running the Test Script

```bash
# Make executable
chmod +x E2E_TEST.sh

# Run the test
export GITLAB_TOKEN="glpat-xxxxx"
export GITLAB_PROJECT_ID=12345
export SPRINTFLOW_PROJECT_ID=1
export SPRINTFLOW_TOKEN="eyJ0eXAi..."

./E2E_TEST.sh
```

## Expected Results

✅ **Success Criteria**:
- Repository successfully linked
- Manual sync completes with commits synced > 0
- Commits queryable via API
- Dashboard metrics returned with data
- Audit logs record all operations
- All endpoints return appropriate status codes
- Response times < 2 seconds per endpoint

❌ **Failure Criteria**:
- Any endpoint returns error status (5xx)
- No commits synced despite GitLab project having commits
- Metrics endpoint returns empty/null values
- Audit logs missing expected entries
- Response times > 5 seconds

## Security Validation

After E2E testing, verify security:

```bash
# 1. Verify tokens are not in logs
docker-compose logs api | grep -i "glpat-" && echo "ERROR: Token in logs!" || echo "✓ No tokens in logs"

# 2. Verify tokens are encrypted in database
psql postgresql://user:password@localhost/sprintflow
SELECT gitlab_access_token FROM gitlab_repositories WHERE id = 1;
# Should show encrypted value starting with gAA... (Fernet format)

# 3. Verify error messages don't expose tokens
curl -X POST "http://localhost:8000/api/v1/repositories/gitlab/link/1" \
  -H "Authorization: Bearer ${SPRINTFLOW_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"gitlab_project_id": 99999, "gitlab_url": "https://gitlab.com", "gitlab_token": "bad-token"}'
# Error message should NOT contain the token
```

---

**Completion Criteria**: All E2E tests pass and security validation succeeds

**Expected Time**: 10-15 minutes for full test cycle

**Recommended**: Run this test before deploying to production
