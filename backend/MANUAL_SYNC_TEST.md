# Manual GitLab Sync Testing Guide

**Purpose**: Validate that the GitLab commit synchronization works correctly with a real GitLab project.

## Prerequisites

Before testing, you'll need:

1. **GitLab Account** - Access to gitlab.com or self-hosted instance
2. **Test Project** - A GitLab project with at least 5 commits
3. **Project ID** - The numeric project ID
4. **API Token** - Personal access token with `api` scope
5. **SprintFlow Instance** - Running backend with database
6. **Authentication** - Valid JWT token for SprintFlow API

## Step 1: Prepare GitLab Project

### Identify Test Project

```bash
# Option A: Create new test project
https://gitlab.com/projects/new
# Create a test project (e.g., "sprintflow-test-repo")

# Option B: Use existing project with commits
# Find project ID in Settings → General
# Example URL: https://gitlab.com/username/project-name
# Project ID visible in Settings
```

### Generate API Token

```bash
# Navigate to access tokens
https://gitlab.com/profile/personal_access_tokens

# Create new token:
Token Name: sprintflow-sync-test
Expiration: 30 days
Scopes: api (read-only)

# Copy token immediately
export GITLAB_TOKEN="glpat-xxxxxxxxxx"
```

## Step 2: Prepare Test Environment

### Set Environment Variables

```bash
# GitLab credentials
export GITLAB_TOKEN="glpat-xxxxxxxxxx"
export GITLAB_PROJECT_ID=12345
export GITLAB_URL="https://gitlab.com"  # or self-hosted URL

# SprintFlow credentials
export SPRINTFLOW_TOKEN="eyJ0eXAiOiJKV1QiLC..."
export SPRINTFLOW_PROJECT_ID=1
export SPRINTFLOW_URL="http://localhost:8000"
```

### Verify Connectivity

```bash
# Test GitLab API access
curl -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
  "${GITLAB_URL}/api/v4/user"

# Expected response: Your GitLab user profile

# Test SprintFlow API access
curl "${SPRINTFLOW_URL}/api/v1/projects/${SPRINTFLOW_PROJECT_ID}" \
  -H "Authorization: Bearer ${SPRINTFLOW_TOKEN}"

# Expected response: Project details
```

## Step 3: Prepare Database

### Create Test Repository Record

```bash
# Option A: Link via API
curl -X POST \
  "${SPRINTFLOW_URL}/api/v1/repositories/gitlab/link/${SPRINTFLOW_PROJECT_ID}" \
  -H "Authorization: Bearer ${SPRINTFLOW_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "gitlab_project_id": '"${GITLAB_PROJECT_ID}"',
    "gitlab_url": "'"${GITLAB_URL}"'",
    "gitlab_token": "'"${GITLAB_TOKEN}"'"
  }'

# Response should show: "status": "linked"

# Option B: Directly in database (for testing)
psql postgresql://user:password@localhost/sprintflow

INSERT INTO gitlab_repositories (
  project_id, 
  gitlab_project_id, 
  gitlab_url, 
  gitlab_access_token
) VALUES (
  1, 
  12345, 
  'https://gitlab.com',
  (SELECT encrypt_token('glpat-xxx'))  -- Use app's encryption
);
```

## Step 4: Manual Sync Testing

### Trigger Manual Sync

```bash
# Request sync via API
curl -X POST \
  "${SPRINTFLOW_URL}/api/v1/repositories/gitlab/sync/${SPRINTFLOW_PROJECT_ID}" \
  -H "Authorization: Bearer ${SPRINTFLOW_TOKEN}"

# Expected response (200 OK):
{
  "status": "success",
  "repository_id": 1,
  "commits_synced": 42,
  "duration_seconds": 2.5,
  "message": "Sync completed successfully"
}
```

### Monitor Sync in Progress

```bash
# Watch sync job in another terminal
watch -n 1 "psql -U postgres -d sprintflow -c 'SELECT * FROM global_job WHERE job_name = \"gitlab_sync_repositories\" ORDER BY executed_at DESC LIMIT 1;'"

# Should show:
# - status: starting → in_progress → completed
# - commit_count increasing from 0 to final number
# - duration_seconds increasing until complete
```

## Step 5: Verify Commits Were Synced

### Check Commits in Database

```bash
# Count total commits
psql postgresql://user:password@localhost/sprintflow

SELECT COUNT(*) as total_commits FROM commits WHERE repository_id = 1;

# Get sample commits
SELECT git_hash, message, author_name, author_email, committed_at 
FROM commits 
WHERE repository_id = 1 
ORDER BY committed_at DESC 
LIMIT 5;

# Expected output: Multiple commits with proper data
```

### Compare with GitLab API

```bash
# Get commit count from GitLab
GITLAB_COMMIT_COUNT=$(curl -s \
  -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
  "${GITLAB_URL}/api/v4/projects/${GITLAB_PROJECT_ID}/repository/commits?statistics=true" \
  | grep -o '"count":[0-9]*' | grep -o '[0-9]*' | head -1)

echo "GitLab commits: ${GITLAB_COMMIT_COUNT}"

# Get count from SprintFlow
SPRINTFLOW_COMMIT_COUNT=$(psql -U postgres -d sprintflow -t -c "SELECT COUNT(*) FROM commits WHERE repository_id = 1;")

echo "SprintFlow commits: ${SPRINTFLOW_COMMIT_COUNT}"

# They should match (or SprintFlow may have fewer if limited by date range)
```

### Verify Commit Data Accuracy

```bash
# Get a commit from GitLab API
COMMIT_HASH="abc123def456"  # Replace with real hash from above

GITLAB_COMMIT=$(curl -s \
  -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
  "${GITLAB_URL}/api/v4/projects/${GITLAB_PROJECT_ID}/repository/commits/${COMMIT_HASH}")

echo "GitLab commit:"
echo "$GITLAB_COMMIT" | jq '{id, message, author_name, author_email, committed_date}'

# Get same commit from SprintFlow
SPRINTFLOW_COMMIT=$(psql -U postgres -d sprintflow -t -c "
SELECT git_hash, message, author_name, author_email, committed_at 
FROM commits 
WHERE git_hash = '${COMMIT_HASH}';")

echo "SprintFlow commit:"
echo "$SPRINTFLOW_COMMIT"

# Data should match
```

## Step 6: Test Data Persistence

### Verify Timestamps

```bash
-- Check that sync timestamp was recorded
SELECT last_sync_timestamp FROM gitlab_repositories WHERE id = 1;

-- Should show a recent timestamp

-- Verify commit timestamps match GitLab
SELECT MIN(committed_at), MAX(committed_at) FROM commits WHERE repository_id = 1;

-- Should align with actual commit dates from GitLab
```

### Test Incremental Sync

```bash
# Add a new commit to GitLab project
# (Either via web UI or git push)

# Wait a moment, then trigger sync again
curl -X POST \
  "${SPRINTFLOW_URL}/api/v1/repositories/gitlab/sync/${SPRINTFLOW_PROJECT_ID}" \
  -H "Authorization: Bearer ${SPRINTFLOW_TOKEN}"

# Check that only new commits were fetched
# (Should be much faster than first sync, fewer commits)

# Verify no duplicates
psql postgresql://user:password@localhost/sprintflow

SELECT git_hash, COUNT(*) as count 
FROM commits 
WHERE repository_id = 1 
GROUP BY git_hash 
HAVING COUNT(*) > 1;

# Should return 0 rows (no duplicates)
```

## Step 7: Test Error Handling

### Test Invalid Credentials

```bash
# Unlink and relink with invalid token
curl -X POST \
  "${SPRINTFLOW_URL}/api/v1/repositories/gitlab/link/${SPRINTFLOW_PROJECT_ID}" \
  -H "Authorization: Bearer ${SPRINTFLOW_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "gitlab_project_id": '"${GITLAB_PROJECT_ID}"',
    "gitlab_url": "'"${GITLAB_URL}"'",
    "gitlab_token": "glpat-invalid-token-123"
  }'

# Trigger sync
curl -X POST \
  "${SPRINTFLOW_URL}/api/v1/repositories/gitlab/sync/${SPRINTFLOW_PROJECT_ID}" \
  -H "Authorization: Bearer ${SPRINTFLOW_TOKEN}"

# Should fail with "Invalid credentials" error

# Check GlobalJob table
psql postgresql://user:password@localhost/sprintflow
SELECT * FROM global_job WHERE job_name = 'gitlab_sync_repositories' 
ORDER BY executed_at DESC LIMIT 1;

# Status should be "failed" or "completed_with_errors"
# Errors field should describe the authentication failure
```

### Test Invalid Project ID

```bash
# Link non-existent project
curl -X POST \
  "${SPRINTFLOW_URL}/api/v1/repositories/gitlab/link/${SPRINTFLOW_PROJECT_ID}" \
  -H "Authorization: Bearer ${SPRINTFLOW_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "gitlab_project_id": 999999,
    "gitlab_url": "'"${GITLAB_URL}"'",
    "gitlab_token": "'"${GITLAB_TOKEN}"'"
  }'

# Trigger sync
curl -X POST \
  "${SPRINTFLOW_URL}/api/v1/repositories/gitlab/sync/${SPRINTFLOW_PROJECT_ID}" \
  -H "Authorization: Bearer ${SPRINTFLOW_TOKEN}"

# Should fail with "Project not found" (404)
```

## Step 8: Verify Audit Logging

### Check Audit Trail

```bash
# Query all GitLab operations
psql postgresql://user:password@localhost/sprintflow

SELECT action, user_id, resource_id, details, created_at 
FROM audit_system_log 
WHERE action LIKE '%gitlab%' 
ORDER BY created_at DESC LIMIT 10;

# Expected actions:
# - gitlab_repository_linked
# - gitlab_sync_started
# - gitlab_sync_completed
```

### Verify Sync Job Logged

```bash
-- Check GlobalJob entries
SELECT id, job_name, status, repository_id, commit_count, errors, executed_at 
FROM global_job 
WHERE job_name = 'gitlab_sync_repositories' 
ORDER BY executed_at DESC LIMIT 10;

-- Each sync should create an entry with:
-- - status: completed or failed
-- - commit_count: number of new commits synced
-- - duration_seconds: how long sync took
-- - errors: if status is failed
```

## Complete Manual Test Script

```bash
#!/bin/bash
# MANUAL_SYNC_TEST.sh

set -e

echo "=================================================="
echo "GitLab Sync Manual Testing"
echo "=================================================="
echo ""

# Verify environment variables
if [ -z "$GITLAB_TOKEN" ] || [ -z "$SPRINTFLOW_TOKEN" ]; then
  echo "ERROR: Missing required environment variables"
  echo "Required: GITLAB_TOKEN, GITLAB_PROJECT_ID, SPRINTFLOW_TOKEN, SPRINTFLOW_PROJECT_ID"
  exit 1
fi

echo "Configuration:"
echo "  GitLab URL: ${GITLAB_URL:-https://gitlab.com}"
echo "  GitLab Project ID: $GITLAB_PROJECT_ID"
echo "  SprintFlow Project ID: $SPRINTFLOW_PROJECT_ID"
echo ""

# Step 1: Link repository
echo "Step 1: Linking repository..."
LINK_RESPONSE=$(curl -s -X POST \
  "${SPRINTFLOW_URL}/api/v1/repositories/gitlab/link/${SPRINTFLOW_PROJECT_ID}" \
  -H "Authorization: Bearer ${SPRINTFLOW_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "gitlab_project_id": '"${GITLAB_PROJECT_ID}"',
    "gitlab_url": "'"${GITLAB_URL:-https://gitlab.com}"'",
    "gitlab_token": "'"${GITLAB_TOKEN}"'"
  }')

if echo "$LINK_RESPONSE" | grep -q '"status"'; then
  echo "✓ Repository linked"
else
  echo "✗ Failed to link repository"
  echo "$LINK_RESPONSE"
  exit 1
fi
echo ""

# Step 2: Trigger sync
echo "Step 2: Triggering sync..."
SYNC_START=$(date +%s)

SYNC_RESPONSE=$(curl -s -X POST \
  "${SPRINTFLOW_URL}/api/v1/repositories/gitlab/sync/${SPRINTFLOW_PROJECT_ID}" \
  -H "Authorization: Bearer ${SPRINTFLOW_TOKEN}")

if echo "$SYNC_RESPONSE" | grep -q '"status":"success"'; then
  COMMITS=$(echo "$SYNC_RESPONSE" | grep -o '"commits_synced":[0-9]*' | grep -o '[0-9]*')
  DURATION=$(echo "$SYNC_RESPONSE" | grep -o '"duration_seconds":[0-9.]*' | grep -o '[0-9.]*')
  echo "✓ Sync completed"
  echo "  Commits synced: $COMMITS"
  echo "  Duration: ${DURATION}s"
else
  echo "✗ Sync failed"
  echo "$SYNC_RESPONSE"
  exit 1
fi
echo ""

# Step 3: Verify commits
echo "Step 3: Verifying commits in database..."
DB_COUNT=$(psql -U postgres -d sprintflow -t -c "SELECT COUNT(*) FROM commits WHERE repository_id = 1;")
echo "✓ Commits in database: $DB_COUNT"
echo ""

# Step 4: Check audit logs
echo "Step 4: Checking audit logs..."
AUDIT_LOGS=$(psql -U postgres -d sprintflow -t -c "SELECT COUNT(*) FROM global_job WHERE job_name = 'gitlab_sync_repositories';")
echo "✓ Sync jobs recorded: $AUDIT_LOGS"
echo ""

echo "=================================================="
echo "✓ Manual sync test completed successfully!"
echo "=================================================="
```

## Troubleshooting

### Sync Returns "Invalid Credentials"

```bash
# Test token validity
curl -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
  "${GITLAB_URL}/api/v4/user"

# If 401: Token invalid or expired, regenerate

# If 403: Token valid but no access to project
# - Verify user has access to project in GitLab
# - Check project visibility (public/private)
```

### No Commits Synced

```bash
# Verify project has commits
curl -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
  "${GITLAB_URL}/api/v4/projects/${GITLAB_PROJECT_ID}/repository/commits?per_page=1"

# If empty: Project has no commits yet
# - Create test commits with:
#   git clone <project-url>
#   echo "test" > test.txt
#   git add test.txt
#   git commit -m "Test commit"
#   git push

# If commits exist: Check sync job errors
psql -c "SELECT errors FROM global_job WHERE job_name = 'gitlab_sync_repositories' ORDER BY executed_at DESC LIMIT 1;"
```

### Sync Takes Too Long

```bash
# Check database performance
psql -c "EXPLAIN ANALYZE SELECT COUNT(*) FROM commits WHERE repository_id = 1;"

# For large repositories (10,000+ commits):
# - First sync may take 30+ seconds
# - Subsequent syncs should be faster (incremental)

# If repeatedly slow:
# - Check database indexes exist
# - Monitor disk I/O during sync
# - Consider staging environment with smaller dataset
```

## Success Criteria

✅ **Sync Test Passed When:**
- Repository successfully links
- Manual sync completes without errors
- Commits visible in database matching GitLab count
- Commit data (hash, message, author, timestamp) matches GitLab
- Incremental sync detects no duplicates
- Audit logs record all operations
- Response times are reasonable (< 30s for typical repos)

❌ **Sync Test Failed When:**
- Any step returns error or timeout
- Commit count doesn't match GitLab
- Duplicate commits detected
- Audit logs missing entries
- Response times exceed 60 seconds

---

**Estimated Time**: 15-20 minutes for complete test cycle

**Required for**: Production deployment validation

**Recommended**: Run this test with at least 2 different GitLab projects
