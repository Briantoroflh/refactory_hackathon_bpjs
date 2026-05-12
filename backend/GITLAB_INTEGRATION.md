# GitLab Integration Guide

## Overview

The SprintFlow platform integrates with GitLab to automatically sync commit information and display commit metrics on the project dashboard. This guide explains how to set up and use the GitLab integration.

## Features

- **Repository Linking**: Link GitLab repositories to SprintFlow projects (1-to-1 mapping)
- **Automatic Sync**: Background job syncs commits periodically (every 15 minutes by default)
- **Commit Tracking**: View all commits from linked repositories with filters
- **Dashboard Metrics**: See commit frequency, contributor activity, branch breakdown, and velocity trends
- **Activity Timeline**: Track commit activity over time on project dashboards

## Setup Instructions

### 1. Generate a GitLab API Token

1. Log in to your GitLab account at https://gitlab.com (or your GitLab instance)
2. Navigate to **Settings → Access Tokens**
3. Click **Add new token**
4. Fill in the form:
   - **Token name**: `sprintflow-sync` (or any descriptive name)
   - **Expiration date**: Choose an appropriate date (e.g., 1 year from now)
   - **Scopes**: Select `api` (for read access to repositories)
5. Click **Create personal access token**
6. **IMPORTANT**: Copy the token immediately. You won't be able to see it again.

### 2. Configure Environment Variables

Add these variables to your `.env` file in the backend directory:

```bash
# GitLab Configuration
GITLAB_API_BASE_URL=https://gitlab.com
GITLAB_SYNC_INTERVAL_MINUTES=15
GITLAB_ENABLE_AUTO_SYNC=True
TOKEN_ENCRYPTION_KEY=your-32-character-encryption-key-here
```

#### TOKEN_ENCRYPTION_KEY Generation

To generate a secure encryption key for storing GitLab tokens, run:

```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())
```

Paste the output as your `TOKEN_ENCRYPTION_KEY`.

### 3. Link a Repository

Once your SprintFlow instance is running, link a GitLab repository:

**Using the API:**
```bash
curl -X POST http://localhost:8000/api/v1/repositories/gitlab/link/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "gitlab_project_id": 12345,
    "gitlab_url": "https://gitlab.com",
    "gitlab_token": "glpat-VmdlsWpx4ziN1Nohd7a_FWM6MQpvOjEKdTptcGtpeQ8"
  }'
```

Replace:
- `1` with your SprintFlow project ID
- `12345` with the GitLab project ID (visible in GitLab project settings)
- `glpat-...` with your GitLab API token

**Using the UI:** (when available)
1. Navigate to project settings
2. Go to "GitLab Integration"
3. Click "Link Repository"
4. Enter the GitLab project ID and API token
5. Click "Verify & Link"

## Usage

### View Commits

**List all commits with filtering:**
```bash
curl http://localhost:8000/api/v1/commits \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Query parameters:**
- `project_id`: Filter by project ID
- `days`: Look back period (default: 30 days)
- `author_email`: Filter by commit author email
- `branch`: Filter by branch name
- `skip`: Pagination offset (default: 0)
- `limit`: Results per page (default: 100)

**Example:**
```bash
curl "http://localhost:8000/api/v1/commits?project_id=1&days=7&author_email=john@example.com" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### View Dashboard Metrics

**Get comprehensive dashboard metrics:**
```bash
curl http://localhost:8000/api/v1/dashboard/gitlab-metrics/1?days=30 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response includes:**
- Commit frequency (total commits, commits per day)
- Top contributors
- Branch activity breakdown
- Commit velocity (trend: increasing/decreasing/stable)
- Repository health status

**Query parameters:**
- `days`: Analysis period (1-365 days, default: 30)

### Manual Sync Trigger

To manually trigger a sync for a specific repository:

```bash
curl -X POST http://localhost:8000/api/v1/repositories/gitlab/sync/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Configuration Reference

### Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `GITLAB_API_BASE_URL` | URL | `https://gitlab.com` | Your GitLab instance URL (change if using self-hosted GitLab) |
| `GITLAB_SYNC_INTERVAL_MINUTES` | Integer | `15` | How often the sync job runs (in minutes) |
| `GITLAB_ENABLE_AUTO_SYNC` | Boolean | `True` | Enable/disable automatic background sync |
| `TOKEN_ENCRYPTION_KEY` | String | (empty) | **REQUIRED**: Encryption key for storing API tokens securely |

### Sync Behavior

The background sync job:
1. **Frequency**: Runs every `GITLAB_SYNC_INTERVAL_MINUTES` minutes (default: 15)
2. **Look-back Period**: Fetches commits from the last 90 days (or since last sync)
3. **Batch Size**: Inserts commits in batches of 500 for performance
4. **Duplicate Detection**: Prevents duplicate commits using git hash + repository ID
5. **Audit Logging**: All sync operations logged to audit trail

### Rate Limiting

GitLab API has rate limits:
- **Authenticated requests**: 600 requests per minute
- **Unauthenticated**: 300 requests per minute

SprintFlow respects these limits and includes exponential backoff for failed requests (up to 3 retries).

## Metrics Explained

### Commit Frequency
- **Total Commits**: Number of commits in the analysis period
- **Commits per Day**: Average commits per day

### Top Contributors
- Shows developers with most commits
- Sorted by commit count (descending)

### Branch Activity
- Lists branches by commit count
- Shows which branches are most active

### Commit Velocity
- **Current Period**: Commits in the selected time period
- **Previous Period**: Commits in the same period before
- **Trend**: Whether activity is increasing, decreasing, or stable
- **Change %**: Percentage change between periods

### Repository Health Status
- **Healthy**: Active development with multiple contributors
- **Yellow**: Some activity but fewer commits or contributors
- **Red**: Low activity or stale repository

## Troubleshooting

### Sync Job Issues

#### "Sync job not running" / "No sync entries in GlobalJob table"

**Symptoms:**
- Background sync never runs
- GlobalJob table has no entries for `gitlab_sync_repositories`
- `GITLAB_ENABLE_AUTO_SYNC=True` but sync doesn't execute

**Diagnosis:**
```bash
# 1. Check if APScheduler is initialized
docker-compose logs api | grep -i "scheduler\|jobs initialized"

# 2. Verify environment variable is set
echo $GITLAB_ENABLE_AUTO_SYNC  # Should print: True

# 3. Check if job is registered
sqlite3 jobs.db "SELECT * FROM apscheduler_jobs WHERE id = 'gitlab_sync_job';" 2>/dev/null || echo "Jobs DB not found (may use in-memory)"
```

**Solutions:**
1. **Verify GITLAB_ENABLE_AUTO_SYNC=True**
   ```bash
   # In .env
   GITLAB_ENABLE_AUTO_SYNC=True
   docker-compose up -d --no-deps backend
   ```

2. **Check APScheduler logs**
   ```bash
   docker-compose logs api | grep -A5 "APScheduler\|scheduler.*initialized"
   ```

3. **Manually trigger sync to verify endpoint works**
   ```bash
   curl -X POST http://localhost:8000/api/v1/repositories/gitlab/sync/1 \
     -H "Authorization: Bearer $TOKEN"
   
   # Should return 200 with sync result
   ```

4. **Check database for job records**
   ```sql
   -- Should have recent entries
   SELECT id, job_name, status, executed_at 
   FROM global_job 
   WHERE job_name = 'gitlab_sync_repositories' 
   ORDER BY executed_at DESC LIMIT 5;
   ```

---

#### "Sync fails with 'Connection refused'"

**Symptoms:**
- Sync job shows error in GlobalJob table
- Error message: `ConnectionRefusedError: [Errno 111] Connection refused`
- Cannot connect to GitLab API

**Diagnosis:**
```bash
# Test connectivity to GitLab
curl -I https://gitlab.com/api/v4/version

# Test with your GitLab instance
curl -I $GITLAB_API_BASE_URL/api/v4/version
```

**Solutions:**
1. **Verify GITLAB_API_BASE_URL is correct**
   ```bash
   # Should be like: https://gitlab.com or https://gitlab.yourcompany.com
   echo $GITLAB_API_BASE_URL
   ```

2. **Check network/firewall allows outbound HTTPS**
   ```bash
   # From the API container
   docker-compose exec api curl -I https://gitlab.com/api/v4/version
   ```

3. **Check DNS resolution**
   ```bash
   docker-compose exec api nslookup gitlab.com
   ```

---

#### "Invalid GitLab credentials" / "401 Unauthorized"

**Symptoms:**
- Sync fails with 401 error
- Error in GlobalJob: `Unauthorized` or `Invalid credentials`
- Token verification fails

**Diagnosis:**
```bash
# Test token validity against GitLab
curl -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  https://gitlab.com/api/v4/user

# Check token has api scope
curl -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  https://gitlab.com/api/v4/personal_access_tokens/self
```

**Solutions:**
1. **Verify token is correct**
   ```bash
   # Copy token from GitLab and test
   GITLAB_TOKEN="glpat-abc123xyz"
   curl -H "PRIVATE-TOKEN: $GITLAB_TOKEN" https://gitlab.com/api/v4/user
   ```

2. **Check token hasn't expired**
   - Go to GitLab Settings → Access Tokens
   - Verify token expiration date is in the future
   - If expired, create new token

3. **Verify token has `api` scope**
   - In GitLab, go to Settings → Access Tokens
   - Find your token, verify `api` checkbox is checked
   - Create new token with proper scope if needed

4. **Check GITLAB_API_BASE_URL matches token's GitLab instance**
   - Token from gitlab.com requires GITLAB_API_BASE_URL=https://gitlab.com
   - Token from self-hosted requires matching URL

---

#### "Repository not found" / "404 Not Found"

**Symptoms:**
- Sync fails when trying to fetch repository
- Error: `404 Not Found` or `Project not found`
- Repository details endpoint returns 404

**Diagnosis:**
```bash
# Test if GitLab project exists and is accessible
curl -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  https://gitlab.com/api/v4/projects/YOUR_PROJECT_ID

# Test with correct GitLab instance
curl -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  $GITLAB_API_BASE_URL/api/v4/projects/YOUR_PROJECT_ID
```

**Solutions:**
1. **Verify GitLab project ID is correct**
   - Go to GitLab project → Settings
   - Copy the exact Project ID (integer, e.g., 12345)
   - Verify it matches the one in SprintFlow

2. **Check token has access to project**
   - Token must have access to the specific project
   - If project is private, token must be from user with access
   - Test: `curl -H "PRIVATE-TOKEN: $TOKEN" https://gitlab.com/api/v4/projects/ID`

3. **Verify project is not archived**
   - Archived projects cannot be accessed via API
   - Go to GitLab project → Settings → General
   - Unarchive if needed

---

### Commit Sync Issues

#### "No commits synced" / "Commits table remains empty"

**Symptoms:**
- Repository successfully linked
- Sync job appears to complete (GlobalJob status = "completed")
- But no commits appear in database
- Dashboard metrics show "No data available"

**Diagnosis:**
```bash
# Check if GitLab repository has commits
curl -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_API_BASE_URL/api/v4/projects/PROJECT_ID/repository/commits?per_page=1"

# Check if commits were inserted into database
sqlite3 sprintflow.db "SELECT COUNT(*) FROM commits WHERE repository_id = REPO_ID;"

# Check sync job details
sqlite3 sprintflow.db "SELECT * FROM global_job WHERE job_name = 'gitlab_sync_repositories' ORDER BY executed_at DESC LIMIT 1;" | grep -o "result.*"
```

**Solutions:**
1. **Verify repository is linked correctly**
   ```bash
   # Check linked repository exists
   curl http://localhost:8000/api/v1/repositories/gitlab/1 \
     -H "Authorization: Bearer $TOKEN"
   
   # Should return repository details with status
   ```

2. **Manually trigger sync and check result**
   ```bash
   curl -X POST http://localhost:8000/api/v1/repositories/gitlab/sync/1 \
     -H "Authorization: Bearer $TOKEN"
   
   # Response should show commit count and status
   ```

3. **Check GlobalJob table for error details**
   ```sql
   SELECT result, errors, commit_count FROM global_job 
   WHERE job_name = 'gitlab_sync_repositories' 
   AND repository_id = 1 
   ORDER BY executed_at DESC LIMIT 1;
   ```

4. **Verify repository actually has commits**
   - Check GitLab project for branches/tags
   - If brand new repository, create a test commit
   - Retry sync after adding commits

---

#### "Sync is very slow" / "Sync times out"

**Symptoms:**
- Sync takes > 5 minutes
- Sync job status shows "timeout" or "failed"
- Database CPU usage is high during sync

**Diagnosis:**
```bash
# Check sync job duration
sqlite3 sprintflow.db "SELECT executed_at, duration_seconds, commit_count FROM global_job WHERE job_name = 'gitlab_sync_repositories' ORDER BY executed_at DESC LIMIT 10;"

# Check database indexes
sqlite3 sprintflow.db ".indices commits"
# Should show indexes on: repository_id, committed_at, git_hash

# Check if large commit history
curl -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_API_BASE_URL/api/v4/projects/PROJECT_ID/repository/commits?pagination=keyset&per_page=1&order=topo" \
  | grep total_commits
```

**Solutions:**
1. **Increase timeout**
   ```bash
   # In backend app/config.py or environment
   GITLAB_TIMEOUT_SECONDS=120  # Default is 60
   docker-compose up -d --no-deps backend
   ```

2. **Optimize database queries**
   ```sql
   -- Ensure indexes exist
   CREATE INDEX IF NOT EXISTS idx_commits_repository_id ON commits(repository_id);
   CREATE INDEX IF NOT EXISTS idx_commits_committed_at ON commits(committed_at);
   CREATE INDEX IF NOT EXISTS idx_commits_git_hash ON commits(git_hash);
   ```

3. **Reduce sync frequency if first sync is large**
   ```bash
   # Run sync manually for large repos during off-hours
   GITLAB_SYNC_INTERVAL_MINUTES=60  # Instead of 15
   # Or disable auto-sync and use manual triggers
   GITLAB_ENABLE_AUTO_SYNC=False
   ```

4. **Check database performance**
   ```bash
   # Monitor database connections during sync
   docker-compose exec db psql -c "SELECT count(*) FROM pg_stat_activity;"
   ```

---

### Data Issues

#### "Duplicate commits appearing" / "Commits synced multiple times"

**Symptoms:**
- Dashboard shows incorrect commit counts (too high)
- Same commit appears multiple times in commits table
- Commit frequency metrics are inflated

**Diagnosis:**
```bash
# Find duplicate commits
sqlite3 sprintflow.db "
SELECT git_hash, COUNT(*) as count 
FROM commits 
WHERE repository_id = REPO_ID 
GROUP BY git_hash 
HAVING count > 1 
LIMIT 10;
"
```

**Solutions:**
1. **Database has unique constraint, duplicates shouldn't occur**
   - Unique constraint on `(repository_id, git_hash)`
   - If duplicates exist, database schema may be corrupted

2. **Check migration was applied correctly**
   ```bash
   docker-compose exec api alembic current
   # Should show latest migration version
   ```

3. **If duplicates exist, clean up**
   ```sql
   -- Remove duplicates, keep only the oldest
   DELETE FROM commits 
   WHERE id NOT IN (
     SELECT MIN(id) FROM commits 
     GROUP BY repository_id, git_hash
   );
   ```

---

#### "Metrics show 0 commits" / "Dashboard shows 'No data'"

**Symptoms:**
- Commits in database but dashboard endpoint returns empty metrics
- Commit frequency shows 0 commits
- All metric values are null/0

**Diagnosis:**
```bash
# Verify commits exist
sqlite3 sprintflow.db "SELECT COUNT(*) FROM commits WHERE repository_id = 1;"

# Test metrics endpoint directly
curl http://localhost:8000/api/v1/dashboard/gitlab-metrics/1?days=30 \
  -H "Authorization: Bearer $TOKEN" | jq .
```

**Solutions:**
1. **Check commit date ranges**
   ```sql
   -- Commits may be outside the date range
   SELECT MIN(committed_at), MAX(committed_at) 
   FROM commits 
   WHERE repository_id = 1;
   ```

2. **Extend date range in query**
   ```bash
   # Try 90 days instead of 30
   curl "http://localhost:8000/api/v1/dashboard/gitlab-metrics/1?days=90" \
     -H "Authorization: Bearer $TOKEN"
   ```

3. **Verify repository is properly linked**
   ```bash
   curl http://localhost:8000/api/v1/repositories/gitlab/1 \
     -H "Authorization: Bearer $TOKEN"
   ```

---

### API / Integration Issues

#### "Token decryption fails" / "Encryption key error"

**Symptoms:**
- Sync fails when trying to decrypt token
- Error: `InvalidToken` or `Invalid encryption key`
- Cannot link new repositories

**Diagnosis:**
```bash
# Verify encryption key is set
echo $TOKEN_ENCRYPTION_KEY
# Should output a 88-character base64 string

# Test encryption/decryption manually
python -c "
from cryptography.fernet import Fernet
key = b'$TOKEN_ENCRYPTION_KEY'  # Must be bytes
f = Fernet(key)
encrypted = f.encrypt(b'test')
decrypted = f.decrypt(encrypted)
print(f'Success: {decrypted}')
"
```

**Solutions:**
1. **Regenerate and set encryption key**
   ```bash
   # Generate new key
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   
   # Update environment
   TOKEN_ENCRYPTION_KEY=<new_key>
   docker-compose up -d --no-deps backend
   ```

2. **If key changed, old tokens become invalid**
   - Need to re-link repositories with new key
   - Or migrate token encryption (advanced)

---

#### "Rate limit exceeded" / "429 Too Many Requests"

**Symptoms:**
- Sync fails with "Rate limit exceeded"
- GitLab API returns 429 status code
- Error message mentions rate limiting

**Diagnosis:**
```bash
# Check GitLab rate limit headers
curl -I -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  https://gitlab.com/api/v4/user | grep -i "x-ratelimit"
```

**Solutions:**
1. **Wait for rate limit to reset**
   - GitLab allows 600 req/min for authenticated users
   - Rate limit resets every minute

2. **Reduce sync frequency**
   ```bash
   # Instead of every 15 minutes
   GITLAB_SYNC_INTERVAL_MINUTES=60
   ```

3. **Implement caching** (optional)
   - Cache commits for shorter period
   - Reduces API calls significantly

4. **Use higher-tier GitLab account** (if available)
   - Premium accounts may have higher limits

---

### General Debugging

#### Enable verbose logging

```bash
# Set log level to DEBUG for detailed output
LOG_LEVEL=DEBUG
docker-compose up -d --no-deps backend

# View logs
docker-compose logs -f api | grep -i gitlab
```

#### Check all sync jobs

```sql
SELECT 
  id,
  job_name,
  repository_id,
  status,
  executed_at,
  duration_seconds,
  commit_count,
  errors
FROM global_job 
WHERE job_name LIKE '%gitlab%'
ORDER BY executed_at DESC 
LIMIT 20;
```

#### Verify linked repositories

```bash
# Get all linked repositories
curl http://localhost:8000/api/v1/repositories/gitlab \
  -H "Authorization: Bearer $TOKEN" | jq .
```

#### Get sync status for specific repository

```bash
curl http://localhost:8000/api/v1/repositories/gitlab/1 \
  -H "Authorization: Bearer $TOKEN" | jq .
```

#### Contact support

If you've tried these steps and still experiencing issues:
1. Collect logs: `docker-compose logs api > api.log`
2. Collect database dump: `sqlite3 sprintflow.db ".dump" > dump.sql`
3. Contact SprintFlow support with logs attached

## Security Considerations

### Token Storage & Encryption

GitLab API tokens are sensitive credentials that grant access to your repository data. SprintFlow implements multiple security layers:

#### Encryption Implementation

**In-Database Storage:**
- All GitLab API tokens are encrypted using `cryptography.Fernet` (symmetric encryption)
- Encryption uses AES-128-CBC with timestamp and HMAC authentication
- Tokens are encrypted immediately before database insertion
- Encryption key is separate from application code (environment variable)

**Encryption Process:**
```python
# Token is encrypted in the controller before storage
from app.services.token_encryption import get_encryption_helper

encrypted_token = get_encryption_helper().encrypt(gitlab_token)
# Store encrypted_token in database, NOT the plaintext token
```

**Decryption Process:**
```python
# Token is decrypted only when needed for GitLab API calls
decrypted_token = get_encryption_helper().decrypt(encrypted_token)
# Use decrypted_token for API calls, immediately discard from memory after use
```

#### Encryption Key Management

**Key Generation:**
```bash
# Generate a secure 32-byte base64-encoded key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Example output (DO NOT use this, generate your own):
# z1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6=
```

**Key Storage Best Practices:**
1. **Never commit to version control** - Store in `.env` or secure vault only
2. **Unique per environment** - Use different keys for development, staging, production
3. **Secure vault integration** - Store in AWS Secrets Manager, HashiCorp Vault, or similar
4. **Key rotation** - Regenerate keys periodically (every 1-2 years)
5. **Access control** - Restrict who can read the encryption key
6. **Backup security** - Keep backup keys in secure location, encrypted at rest

**Key Rotation Procedure:**
```bash
# 1. Generate new key
NEW_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
echo "New key: $NEW_KEY"

# 2. Temporarily support both keys (if using key versioning)
OLD_KEY=$TOKEN_ENCRYPTION_KEY
export TOKEN_ENCRYPTION_KEY=$NEW_KEY

# 3. Database migration: re-encrypt all tokens with new key
# (Implementation: Alembic migration or Python script in app)
# This ensures all old tokens are decrypted with OLD_KEY and re-encrypted with NEW_KEY

# 4. Verify encryption works
curl -X POST http://localhost:8000/api/v1/repositories/gitlab/link/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"gitlab_project_id": 12345, "gitlab_url": "...", "gitlab_token": "..."}'

# 5. Discard old key
unset OLD_KEY
```

### Token Access & Usage

**Scope Requirements:**
- SprintFlow only needs `api` scope (read-only access to repositories)
- Scopes like `write_repository`, `api_write`, or `sudo` are NOT required
- Never use personal GitLab account tokens - create a dedicated API token

**Minimal Privilege Example:**
```bash
# Create token with minimal scope in GitLab
Settings → Access Tokens
├─ Token Name: sprintflow-sync
├─ Scopes: ✓ api (read-only)
├─ Scopes: ✗ api_write (not needed)
├─ Scopes: ✗ read_user (not needed)
├─ Scopes: ✗ write_repository (not needed)
└─ Expiration: 1 year from now
```

### Access Control

**API-Level Protection:**
- All GitLab endpoints require valid JWT authentication
- Users must have project access to view linked repository details
- Repository linking requires project admin role
- Audit logging tracks all link/unlink operations

**Token Visibility:**
- Encrypted tokens never appear in API responses
- API endpoints return only `linked: true/false`, never the token itself
- Logs use token hashes, not full token values
- Database queries for tokens require direct SQL (not through UI/API)

**Best Practices:**
1. Use a service account token, not personal account token
2. Restrict token to minimum required scopes (`api` read-only)
3. Set token expiration (1 year recommended)
4. Monitor audit logs for suspicious repository linking
5. Revoke tokens immediately if compromised
6. Regenerate encryption key if token security is breached

### Logging & Audit Trail

**What IS Logged:**
- Repository linking/unlinking (user, timestamp, project ID)
- Sync job results (start time, end time, commits synced, errors)
- API authentication events (success and failures)
- Token validation attempts

**What is NOT Logged:**
- Plaintext GitLab API tokens
- Encrypted token values
- GitLab user credentials
- Sensitive API responses

**Audit Log Location:**
```sql
-- View all GitLab operations in audit trail
SELECT * FROM audit_system_log 
WHERE action LIKE '%gitlab%' 
ORDER BY created_at DESC;

-- View sync job status
SELECT * FROM global_job 
WHERE job_name = 'gitlab_sync_repositories' 
ORDER BY executed_at DESC LIMIT 10;
```

### Production Deployment Security Checklist

- [ ] `TOKEN_ENCRYPTION_KEY` is set from secure vault (not hardcoded)
- [ ] Encryption key is unique per environment (dev, staging, prod)
- [ ] `.env` file is in `.gitignore` (never committed)
- [ ] All GitLab tokens use `api` scope only
- [ ] Token expiration is set (1 year maximum)
- [ ] HTTPS/TLS is enabled for all API calls
- [ ] Database backup encryption is enabled
- [ ] Audit logs are monitored and retained
- [ ] Key rotation plan is documented
- [ ] Incident response plan covers token compromise

### Common Security Mistakes to Avoid

❌ **DON'T** - Store plaintext tokens in database
✅ **DO** - Encrypt tokens before storage

❌ **DON'T** - Log API tokens in any form
✅ **DO** - Log token validation results and sync status

❌ **DON'T** - Use personal GitLab account tokens
✅ **DO** - Create dedicated service account tokens

❌ **DON'T** - Commit .env files to git
✅ **DO** - Use .env.example template in git, actual .env in vault

❌ **DON'T** - Reuse encryption keys across environments
✅ **DO** - Generate unique keys for dev, staging, production

❌ **DON'T** - Share tokens via email or chat
✅ **DO** - Use secure vault for token distribution

## Advanced Configuration

### Custom Sync Interval
To run sync every 30 minutes instead of 15:
```bash
GITLAB_SYNC_INTERVAL_MINUTES=30
```

### Disable Auto Sync
To disable automatic syncing and only use manual triggers:
```bash
GITLAB_ENABLE_AUTO_SYNC=False
```

### Self-Hosted GitLab
If using a self-hosted GitLab instance:
```bash
GITLAB_API_BASE_URL=https://gitlab.yourcompany.com
```

## API Endpoints

### Repository Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/repositories/gitlab/link/{project_id}` | POST | Link a GitLab repository to a project |
| `/api/v1/repositories/gitlab/{project_id}` | GET | Get linked repository details |
| `/api/v1/repositories/gitlab/{project_id}` | DELETE | Unlink a repository |
| `/api/v1/repositories/gitlab/sync/{project_id}` | POST | Trigger manual sync |

### Commit Queries

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/commits` | GET | List commits with filters |
| `/api/v1/projects/{project_id}/commit-stats` | GET | Get commit statistics |

### Dashboard Metrics

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/dashboard/gitlab-metrics/{project_id}` | GET | Get comprehensive dashboard metrics |
| `/api/v1/dashboard/gitlab-metrics/{project_id}/frequency` | GET | Get commit frequency metrics |
| `/api/v1/dashboard/gitlab-metrics/{project_id}/velocity` | GET | Get commit velocity metrics |
| `/api/v1/dashboard/gitlab-metrics/{project_id}/health` | GET | Get repository health status |

## Support & Troubleshooting

For issues with GitLab integration:

1. Check logs in `GlobalJob` table for sync status
2. Review `AuditSystemLog` for operation details
3. Verify database is accessible and has proper indexes
4. Check APScheduler logs for job execution details
5. Review GitLab API docs: https://docs.gitlab.com/api/

## Updates & Changelog

### Version 1.0.0
- Initial GitLab integration
- Repository linking and automatic sync
- Commit tracking and analytics
- Dashboard metrics display
- Token encryption for secure storage
- Background job scheduling with APScheduler
