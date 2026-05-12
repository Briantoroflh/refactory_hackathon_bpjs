# AI Assistant Operations Runbook

## Overview

This runbook covers deployment, operations, and recovery procedures for the OpenRouter AI Assistant backend integration.

## Table of Contents

1. [Deployment](#deployment)
2. [Feature Flag Management](#feature-flag-management)
3. [API Key Rotation](#api-key-rotation)
4. [Troubleshooting](#troubleshooting)
5. [Rollback Procedures](#rollback-procedures)
6. [Monitoring](#monitoring)

---

## Deployment

### Pre-Deployment Checklist

Before deploying to any environment:

- [ ] All code changes have been tested locally
- [ ] API tests pass: `pytest tests/test_assistant_api.py`
- [ ] Telemetry tests pass: `pytest tests/test_assistant_telemetry.py`
- [ ] Service tests pass: `pytest tests/test_assistant_service.py`
- [ ] No hardcoded secrets in configuration
- [ ] Feature flag `OPENROUTER_ENABLED=false` for initial deployment

### Environment Variables

Add these to your `.env` or container configuration:

```bash
# OpenRouter Configuration
OPENROUTER_ENABLED=false  # Start disabled for staging validation
OPENROUTER_API_KEY=sk_xxxx  # Never commit - load from secure vault
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=nvidia/nemotron-3-super-120b-a12b:free
OPENROUTER_TIMEOUT_SECONDS=60
OPENROUTER_MAX_RETRIES=3
OPENROUTER_RETRY_BACKOFF_SECONDS=2
OPENROUTER_SITE_URL=https://sprintflow.io
OPENROUTER_SITE_NAME=SprintFlow
```

### Staging Deployment - Phase 1: Disabled Mode

**Objective:** Validate infrastructure, endpoints, and basic functionality without calling external AI provider.

1. **Deploy with `OPENROUTER_ENABLED=false`**
   ```bash
   # Set in environment
   export OPENROUTER_ENABLED=false
   
   # Deploy application
   docker-compose up -d
   ```

2. **Verify Application Health**
   ```bash
   curl -X GET http://staging-api:8000/ai-assistant/health
   
   # Expected response:
   # {
   #   "status": "healthy",
   #   "total_requests": 0,
   #   "successful_requests": 0,
   #   "failed_requests": 0,
   #   "success_rate_percent": 0.0,
   #   ...
   # }
   ```

3. **Run Smoke Tests**
   
   Create auth token for test user:
   ```bash
   curl -X POST http://staging-api:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@sprintflow.io", "password": "AdminPassword123"}'
   
   # Save the access_token from response
   export TOKEN=<access_token>
   ```

   Test workflow endpoints (fallback mode):
   ```bash
   # Test planning endpoint
   curl -X POST http://staging-api:8000/ai-assistant/planning \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "Create a project plan for an e-commerce website",
       "context": {"project_id": 1}
     }'
   
   # Test sprint summary endpoint
   curl -X POST http://staging-api:8000/ai-assistant/sprint-summary \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "Summarize the sprint",
       "context": {"sprint_id": 1}
     }'
   
   # Verify response includes "source": "fallback"
   ```

4. **Verify Role-Based Access Control**
   ```bash
   # Create non-admin user and verify access denied
   # (Tests should show 403 for invalid roles)
   ```

5. **Check Logs**
   ```bash
   docker-compose logs -f api | grep -i "openrouter\|fallback"
   
   # Should see: "OpenRouter disabled; using fallback for workflow=..."
   ```

### Staging Deployment - Phase 2: Enabled Mode

**Objective:** Enable OpenRouter calls and validate output quality, token usage, and cost.

**Prerequisites:**
- Phase 1 smoke tests passed
- Valid `OPENROUTER_API_KEY` obtained from account
- Team agrees on cost budget

1. **Update Environment Variable**
   ```bash
   export OPENROUTER_ENABLED=true
   export OPENROUTER_API_KEY=sk_xxxx  # from secure vault
   
   # Rolling restart (zero downtime):
   docker-compose up -d --no-deps --build api
   ```

2. **Verify Startup Validation**
   ```bash
   docker-compose logs api | grep -i "validation\|error"
   
   # Should NOT see missing key errors
   ```

3. **Test with Real AI Provider**
   ```bash
   export TOKEN=<access_token>
   
   curl -X POST http://staging-api:8000/ai-assistant/planning \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "Create a detailed project plan for building a payment processing system",
       "context": {
         "project_id": 1,
         "timeline": "6 months",
         "team_size": 8,
         "budget": "$500k"
       }
     }'
   
   # Verify response includes "source": "openrouter" and structured JSON output
   ```

4. **Monitor Metrics and Costs**
   
   Check health endpoint for metrics:
   ```bash
   curl -X GET http://staging-api:8000/ai-assistant/health | jq .
   
   # Review:
   # - avg_latency_ms (should be < 10000ms)
   # - error_counts (should be 0 or low)
   # - success_rate_percent (should be > 95%)
   ```

   Check OpenRouter dashboard for:
   - Token usage
   - Cost accrual
   - Error rates
   - Response times

5. **Run Extended Test Suite**
   ```bash
   # Test all workflows
   pytest tests/test_assistant_api.py -v
   pytest tests/test_assistant_telemetry.py -v
   
   # Test with different workload patterns
   # - High concurrency
   # - Large context payloads
   # - Various role types
   ```

6. **Validate Output Quality**
   - Review generated content for accuracy
   - Verify JSON schema compliance
   - Check that structured outputs match expectations
   - Test error handling (timeout, rate limits)

7. **Cost Validation**
   - Run for 24+ hours of staging traffic
   - Verify costs align with quotas
   - Document average cost per workflow type
   - Adjust model or prompt length if needed

---

## Feature Flag Management

### Disabling OpenRouter (Fallback Mode)

If issues arise, immediately disable OpenRouter:

```bash
# Option 1: Environment variable
export OPENROUTER_ENABLED=false
docker-compose up -d --no-deps --build api

# Option 2: Update config and redeploy
# Edit app/config.py: OPENROUTER_ENABLED = False
docker-compose restart api

# Verify fallback is active
curl -X GET http://staging-api:8000/ai-assistant/health | jq .

# Existing requests continue with fallback responses
# New requests return pre-generated guidance
```

### Re-enabling OpenRouter

```bash
export OPENROUTER_ENABLED=true
export OPENROUTER_API_KEY=sk_xxxx
docker-compose up -d --no-deps --build api

# Health check
curl -X GET http://staging-api:8000/ai-assistant/health | jq .
```

---

## API Key Rotation

### Scheduled Rotation (Monthly Recommended)

#### Step 1: Generate New Key

1. Login to OpenRouter account at https://openrouter.ai/account/api_keys
2. Click "Create new key"
3. Name: `sprintflow-staging-YYYY-MM-DD` (include date)
4. Copy key immediately
5. Save in secure vault (AWS Secrets Manager, Vault, etc.)

#### Step 2: Validate New Key

Before rotating out old key:

```bash
# Test new key in staging
export OPENROUTER_API_KEY=sk_new_xxxx
docker-compose up -d --no-deps --build api

# Run smoke tests
curl -X POST http://staging-api:8000/ai-assistant/planning \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test planning", "context": {}}'

# Verify success rate
curl -X GET http://staging-api:8000/ai-assistant/health | jq '.success_rate_percent'

# Should show success_rate_percent >= 95
```

#### Step 3: Rotate in Production (if applicable)

```bash
# Update production secret in vault
# Trigger rolling restart (zero downtime):
export OPENROUTER_API_KEY=sk_new_xxxx
docker-compose up -d --no-deps --build api

# Monitor metrics for 10 minutes
watch -n 5 'curl -s http://staging-api:8000/ai-assistant/health | jq .'
```

#### Step 4: Revoke Old Key

1. Return to https://openrouter.ai/account/api_keys
2. Find old key by name/date
3. Click "Delete"
4. Confirm deletion
5. Document in change log: "Rotated OpenRouter API key - old key revoked YYYY-MM-DD HH:MM UTC"

### Emergency Key Rotation (Suspected Compromise)

If key is compromised:

1. **Immediately disable external calls:**
   ```bash
   export OPENROUTER_ENABLED=false
   docker-compose up -d --no-deps --build api
   ```

2. **Revoke compromised key:**
   - Login to OpenRouter immediately
   - Delete the compromised key
   - Check usage logs for unauthorized calls

3. **Generate new key:**
   - Create new key (see Scheduled Rotation steps)

4. **Deploy with new key:**
   ```bash
   export OPENROUTER_ENABLED=true
   export OPENROUTER_API_KEY=sk_new_xxxx
   docker-compose up -d --no-deps --build api
   ```

5. **Monitor closely:**
   ```bash
   # Watch for anomalies
   docker-compose logs -f api | grep -i error
   curl -X GET http://staging-api:8000/ai-assistant/health | jq .
   ```

---

## Troubleshooting

### Issue: High Error Rate (> 5%)

**Symptoms:**
- Health endpoint shows `success_rate_percent < 95`
- Users report workflow failures
- Error logs show repeated failures

**Resolution:**

1. **Check OpenRouter Status**
   ```bash
   curl -X GET https://openrouter.ai/api/v1/auth/me \
     -H "Authorization: Bearer $OPENROUTER_API_KEY"
   
   # If 401: Key expired or invalid - see API Key Rotation
   # If 429: Rate limited - increase retry backoff
   # If 5xx: OpenRouter outage - enable fallback mode
   ```

2. **Check Error Types**
   ```bash
   curl -X GET http://staging-api:8000/ai-assistant/health | jq '.error_counts'
   
   # Common errors:
   # TimeoutError: Increase OPENROUTER_TIMEOUT_SECONDS
   # RateLimitError: Reduce concurrency or upgrade plan
   # AIServiceError: Check API key and network connectivity
   ```

3. **Enable Fallback**
   ```bash
   export OPENROUTER_ENABLED=false
   docker-compose up -d --no-deps --build api
   ```

4. **Escalate if Needed**
   - Contact OpenRouter support: https://openrouter.ai/support
   - Check status page: https://status.openrouter.ai

### Issue: Slow Response Times (Latency > 10s)

**Symptoms:**
- Health endpoint shows high `latency_ms.avg`
- Users report slow UI responses
- Timeouts on large prompts

**Resolution:**

1. **Increase Timeout**
   ```bash
   # Current: OPENROUTER_TIMEOUT_SECONDS=60
   # Try: OPENROUTER_TIMEOUT_SECONDS=120
   export OPENROUTER_TIMEOUT_SECONDS=120
   docker-compose up -d --no-deps --build api
   ```

2. **Reduce Prompt Complexity**
   - Review context size in prompts
   - Consider breaking large workflows into smaller steps

3. **Switch Model (if available)**
   ```bash
   # Current: nvidia/nemotron-3-super-120b-a12b:free
   # Try faster model: gpt-3.5-turbo (faster, less capable)
   export OPENROUTER_MODEL=openai/gpt-3.5-turbo
   docker-compose up -d --no-deps --build api
   ```

### Issue: Unauthorized Errors (401)

**Symptoms:**
- API returns 401 on workflow requests
- Even after providing valid JWT token
- Error: "Not authenticated" or "Invalid access token"

**Resolution:**

1. **Verify Token is not Refresh Token**
   - Refresh tokens only work for `/auth/refresh`
   - Must use access token for AI endpoints

2. **Check Token Expiration**
   ```bash
   # Get new access token
   curl -X POST http://staging-api:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "password"}'
   ```

3. **Verify JWT Secret**
   - Ensure `SECRET_KEY` environment variable is set
   - If changed, all existing tokens become invalid

---

## Rollback Procedures

### Fast Rollback (Disabled Feature Flag)

**Timing:** < 30 seconds
**Data Impact:** None (read-only operation)

```bash
# Step 1: Disable OpenRouter
export OPENROUTER_ENABLED=false

# Step 2: Redeploy
docker-compose up -d --no-deps --build api

# Step 3: Verify
curl -X GET http://staging-api:8000/ai-assistant/health | jq .
# Should show success_rate_percent = 100 with fallback responses

# Step 4: Monitor for 5 minutes
docker-compose logs -f api | grep -i "fallback\|error"
```

### Full Rollback (Revert Deployment)

**Timing:** 2-5 minutes
**Data Impact:** None (database unchanged)

```bash
# Step 1: Get previous version commit hash
git log --oneline -n 5

# Step 2: Checkout previous version
git checkout <previous-commit-hash>

# Step 3: Stop current deployment
docker-compose down

# Step 4: Rebuild and restart
docker-compose build
docker-compose up -d

# Step 5: Verify
curl -X GET http://staging-api:8000/health

# Step 6: Monitor logs
docker-compose logs -f api

# Step 7: Run smoke tests
# (See Staging Deployment section)
```

### Partial Rollback (Re-enable Fallback Only)

If only the OpenRouter integration needs to be rolled back:

```bash
# Keep current code, disable feature flag
export OPENROUTER_ENABLED=false
docker-compose up -d --no-deps --build api

# This allows reverting just the AI provider without full deployment rollback
```

---

## Monitoring

### Health Check Endpoint

**Endpoint:** `GET /ai-assistant/health`
**Authentication:** None required
**Interval:** Monitor every 60 seconds

```bash
# Example monitoring query
curl -X GET http://staging-api:8000/ai-assistant/health | jq '
{
  status: .status,
  total_requests: .total_requests,
  success_rate: .success_rate_percent,
  avg_latency: .latency_ms.avg,
  errors: .error_counts
}'
```

### Key Metrics to Monitor

| Metric | Threshold | Action |
|--------|-----------|--------|
| `success_rate_percent` | < 95% | Investigate errors |
| `latency_ms.avg` | > 10000 | Increase timeout, reduce load |
| `total_requests` | 0 for 5+ min | Check if service is receiving traffic |
| `error_counts[*]` | > 10 per hour | Check logs, escalate if persistent |

### Alerting Rules

**Critical Alerts:**
- Success rate < 80% for 10 minutes
- All requests failing for 5 minutes
- API key validation errors (401/403)

**Warning Alerts:**
- Success rate < 95% for 30 minutes
- Average latency > 15 seconds
- Specific error type count > 20 per hour

### Logs to Review

```bash
# Errors
docker-compose logs api | grep -i "error\|exception\|failed"

# OpenRouter calls
docker-compose logs api | grep -i "openrouter"

# Telemetry
docker-compose logs api | grep -i "telemetry\|recorded"

# Fallback usage
docker-compose logs api | grep -i "fallback"
```

---

## Maintenance Windows

### Scheduled Maintenance

Announce 24 hours in advance:
- API key rotation (30 min window)
- Model or configuration changes (30 min window)
- Major version updates (1-2 hour window)

During maintenance:
1. Set `OPENROUTER_ENABLED=false`
2. Make changes
3. Validate with smoke tests
4. Re-enable if appropriate
5. Post notice with completion time

### Security Patches

For security-related issues:
1. Immediately set `OPENROUTER_ENABLED=false`
2. Deploy patch in next available window
3. Test thoroughly before re-enabling
4. Update security logs with incident details

---

## Contact & Escalation

- **OpenRouter Support:** https://openrouter.ai/support
- **SprintFlow Team:** dev-team@sprintflow.io
- **On-Call Engineer:** See oncall schedule
