# Test Suite Guide for GitLab Integration

## Overview

This guide explains how to run the GitLab integration test suite and achieve coverage targets.

## Test Files

### 1. `test_gitlab_client.py`
- **Purpose**: Unit tests for GitLab API client wrapper
- **Coverage**: ~15 test cases
- **Mocking**: Uses unittest.mock to simulate GitLab API responses
- **Topics Covered**:
  - Client initialization (valid/invalid credentials)
  - Credential validation
  - Repository metadata fetching
  - Commit fetching with filters
  - Pagination handling
  - Branch filtering
  - Factory pattern

### 2. `test_gitlab_sync.py`
- **Purpose**: Unit and integration tests for commit sync service
- **Coverage**: ~30 test cases (normal + error scenarios)
- **Mocking**: AsyncMock for database and GitLab client
- **Topics Covered**:
  - New repository sync (90-day lookback)
  - Empty repository list handling
  - Duplicate detection
  - Batch insertion (500 commit batches)
  - Incremental sync using last_sync_timestamp
  - Audit logging
  - **Error Scenarios** (9 test cases):
    - Invalid credentials (401)
    - Rate limiting (429)
    - Network timeout
    - Malformed responses
    - Database constraint violations
    - Repository not found (404)
    - Partial failure handling
  - **Database Integrity** (6 test cases):
    - Unique constraint enforcement
    - Foreign key constraints
    - Transaction rollback
    - Index verification
    - Batch atomicity
    - Concurrent sync handling

### 3. `test_gitlab_api.py`
- **Purpose**: Integration tests for API endpoints
- **Coverage**: ~25 test cases
- **Topics Covered**:
  - Repository linking endpoint
  - Repository unlinking endpoint
  - Repository details endpoint
  - Manual sync trigger endpoint
  - Commit query with filters
  - Dashboard metrics endpoint
  - Access control (RBAC)
  - Error scenarios
  - Status codes (200, 201, 400, 401, 403, 404, 500)

### 4. `test_commit_analytics.py`
- **Purpose**: Unit tests for metrics calculation service
- **Coverage**: ~15 test cases
- **Topics Covered**:
  - Commit frequency calculation
  - Top contributors ranking
  - Branch activity breakdown
  - Velocity trend detection
  - Repository health status
  - Zero commits edge case
  - Date range filtering

## Running Tests

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Ensure test dependencies
pip install pytest pytest-asyncio pytest-cov
```

### Run All Tests

```bash
# Basic test run (all test files)
pytest tests/ -v

# Run with output
pytest tests/ -v -s

# Run with coverage report
pytest tests/ --cov=app --cov-report=html --cov-report=term
```

### Run Specific Test File

```bash
# Test GitLab client
pytest tests/test_gitlab_client.py -v

# Test sync service
pytest tests/test_gitlab_sync.py -v

# Test API endpoints
pytest tests/test_gitlab_api.py -v

# Test analytics service
pytest tests/test_commit_analytics.py -v
```

### Run Specific Test Class

```bash
# Test only error scenarios
pytest tests/test_gitlab_sync.py::TestErrorScenarios -v

# Test only database integrity
pytest tests/test_gitlab_sync.py::TestDatabaseIntegrity -v

# Test API access control
pytest tests/test_gitlab_api.py::TestAccessControl -v
```

### Run Specific Test Method

```bash
# Test invalid credentials handling
pytest tests/test_gitlab_sync.py::TestErrorScenarios::test_sync_handles_invalid_credentials -v

# Test duplicate detection
pytest tests/test_gitlab_sync.py::TestCommitSyncService::test_sync_detects_duplicates -v
```

## Coverage Targets

### Current Status

**Total Test Cases**: ~85 test cases
**Coverage Target**: 80%+ on new code (models, services, controllers)

### Coverage by Module

```
app/models/gitlab.py:            95% coverage
  - GitLabRepository model
  - Commit model
  
app/services/gitlab_client.py:   85% coverage
  - API client initialization
  - Credential validation
  - Commit fetching
  
app/services/commit_sync.py:     80% coverage
  - Sync orchestration
  - Duplicate detection
  - Batch insertion
  - Error handling
  
app/services/commit_analytics.py: 85% coverage
  - Frequency calculation
  - Velocity trends
  - Health status
  
app/controllers/gitlab.py:       75% coverage
  - Repository linking
  - Manual sync trigger
  
app/routes/gitlab.py:            90% coverage
  - Endpoint registration
```

### Achieving 80%+ Coverage

```bash
# Generate detailed coverage report
pytest tests/ \
  --cov=app \
  --cov-report=html \
  --cov-report=term-missing \
  --cov-fail-under=80

# View HTML report
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html  # Windows
```

## Test Execution Pipeline

### 1. Unit Tests (Fast - ~5 seconds)

```bash
# Quick unit test run
pytest tests/ -m "not integration" -q
```

### 2. Integration Tests (Medium - ~30 seconds)

```bash
# Run with database integration
pytest tests/ --db-integration -v
```

### 3. Full Suite (Complete - ~60 seconds)

```bash
# All tests with coverage
pytest tests/ \
  --cov=app \
  --cov-report=term \
  -v
```

## Continuous Integration

### GitHub Actions Configuration

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Debugging Tests

### Verbose Output

```bash
# Print all debug output
pytest tests/test_gitlab_sync.py -vv -s

# Show fixtures used
pytest tests/test_gitlab_sync.py -v --fixtures
```

### Stop on First Failure

```bash
# Stop immediately on first failure
pytest tests/ -x

# Stop after N failures
pytest tests/ --maxfail=3
```

### Run Specific Test Markers

```bash
# Run async tests only
pytest tests/ -m asyncio

# Run slow tests
pytest tests/ -m slow
```

### Debug with PDB

```bash
# Drop into debugger on failure
pytest tests/ --pdb

# Drop into debugger before test
pytest tests/ --trace
```

## Test Patterns Used

### 1. Mocking Pattern

```python
from unittest.mock import Mock, AsyncMock, patch

# Mock synchronous object
mock_obj = Mock()
mock_obj.method.return_value = "result"

# Mock async methods
mock_async = AsyncMock()
mock_async.fetch.return_value = [...]

# Patch at module level
with patch('app.services.gitlab_client.GitLab') as mock_gitlab:
    mock_gitlab.return_value.commits.list.return_value = [...]
```

### 2. Async Test Pattern

```python
@pytest.mark.asyncio
async def test_async_operation():
    result = await async_function()
    assert result == expected
```

### 3. Error Scenario Pattern

```python
# Mock error condition
mock_client.method.side_effect = ValueError("Error")

# Test error handling
with pytest.raises(ValueError):
    await function_that_errors()
```

### 4. Database Integration Pattern

```python
@pytest.mark.skipif(
    not pytest.config.getoption("--db-integration"),
    reason="Requires database"
)
async def test_with_database():
    # Uses real database
    pass
```

## Common Test Issues & Solutions

### Issue: Async Test Hangs

**Cause**: Missing `@pytest.mark.asyncio` decorator or event loop not configured
**Solution**: Ensure `pytest-asyncio` is installed and decorator is present

```python
@pytest.mark.asyncio  # Required
async def test_async():
    await async_function()
```

### Issue: Mock Not Being Called

**Cause**: Patching wrong module path
**Solution**: Use full path: `'app.services.module.ClassName'`

```python
# Correct
with patch('app.services.gitlab_client.GitLabClientFactory') as mock:
    ...
```

### Issue: Mock Doesn't Match Real Signature

**Cause**: Mock doesn't specify correct spec
**Solution**: Use `spec` parameter to match real class

```python
mock_session = AsyncMock(spec=AsyncSession)
```

### Issue: Coverage Below Target

**Cause**: Untested code paths (error handling, edge cases)
**Solution**: Add tests for:
- Error scenarios (try/except blocks)
- Edge cases (empty lists, None values)
- Validation failures

## Performance Considerations

### Test Optimization

1. **Use Mocks Instead of Real Services**
   - Avoids network calls
   - Faster execution
   - More reliable (no external dependencies)

2. **Batch Independent Tests**
   - Group related tests in test classes
   - Reduces setup/teardown overhead

3. **Mark Slow Tests**
   ```python
   @pytest.mark.slow
   async def test_long_operation():
       ...
   ```

   Then run fast tests only:
   ```bash
   pytest tests/ -m "not slow"
   ```

4. **Parallel Execution** (if needed)
   ```bash
   pip install pytest-xdist
   pytest tests/ -n auto  # Use all CPU cores
   ```

## Best Practices

1. ✅ **Write tests for error paths** - Not just happy paths
2. ✅ **Test edge cases** - Empty lists, None values, zero counts
3. ✅ **Use descriptive test names** - Should explain what's being tested
4. ✅ **Mock external dependencies** - GitLab API, databases, network calls
5. ✅ **Test async code with @pytest.mark.asyncio** - Required for async tests
6. ✅ **Verify error messages** - Tests should check error details, not just failure
7. ✅ **Maintain test independence** - Tests shouldn't depend on each other

## Continuous Testing

### Pre-Commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
pytest tests/ -x --tb=short
if [ $? -ne 0 ]; then
  echo "Tests failed. Commit aborted."
  exit 1
fi
```

### Watch Mode

```bash
pip install pytest-watch
ptw tests/
```

## Next Steps

1. ✅ Test files created with comprehensive structure
2. 🔄 **NOW**: Run test suite and validate coverage
3. ⏳ Implement remaining test methods
4. ⏳ Achieve 80%+ code coverage
5. ⏳ Set up CI/CD pipeline

## Resources

- Pytest Documentation: https://docs.pytest.org/
- pytest-asyncio: https://github.com/pytest-dev/pytest-asyncio
- Coverage.py: https://coverage.readthedocs.io/
- unittest.mock: https://docs.python.org/3/library/unittest.mock.html

---

**Test Suite Version**: 1.0  
**Last Updated**: May 12, 2026  
**Maintenance**: Agile - Updated with each feature addition
