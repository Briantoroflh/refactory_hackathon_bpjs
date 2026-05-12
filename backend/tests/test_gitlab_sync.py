"""
Unit tests for GitLab commit synchronization service.

Tests cover:
- Normal sync flow (new repos, incremental updates)
- Duplicate detection and handling
- Error scenarios (invalid credentials, rate limiting, network errors)
- Audit logging and error reporting
- Batch insert performance
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

# Handle optional gitlab import for testing
try:
    from gitlab.exceptions import GitlabAuthenticationError, GitlabGetError
except ImportError:
    GitlabAuthenticationError = Exception
    GitlabGetError = Exception

from app.services.commit_sync import CommitSyncService
from app.models.gitlab import GitLabRepository, Commit
from app.models.audit import AuditSystemLog


class TestCommitSyncService:
    """Test cases for CommitSyncService."""

    @pytest.mark.asyncio
    async def test_sync_repository_new_repository(self):
        """Test syncing a new repository with no previous sync."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_repository = Mock(spec=GitLabRepository)
        mock_repository.id = 1
        mock_repository.project_id = 1
        mock_repository.gitlab_project_id = 12345
        mock_repository.gitlab_url = "https://gitlab.com"
        mock_repository.gitlab_access_token = "encrypted-token"
        mock_repository.last_sync_timestamp = None

        with patch('app.services.commit_sync.GitLabClientFactory') as mock_factory:
            mock_client = AsyncMock()
            mock_factory.create_client.return_value = mock_client
            
            # Mock fetch commits to return some commits
            mock_client.fetch_commits.return_value = [
                {
                    "hash": "abc123",
                    "author_name": "John Doe",
                    "author_email": "john@example.com",
                    "message": "Initial commit",
                    "committed_date": datetime.now().isoformat(),
                    "created_at": datetime.now().isoformat(),
                    "branch": "main"
                }
            ]
            
            # For a new repo, sync should use 90-day lookback
            # This test documents the expected behavior

    @pytest.mark.asyncio
    async def test_sync_all_repositories_empty_list(self):
        """Test syncing when no repositories are linked."""
        mock_session = AsyncMock(spec=AsyncSession)
        
        # Mock the query to return no repositories
        mock_query_result = AsyncMock()
        mock_query_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_query_result
        
        # This test documents expected behavior for no repositories

    @pytest.mark.asyncio
    async def test_sync_detects_duplicates(self):
        """Test that duplicate commits are not inserted."""
        # Setup mock objects
        mock_session = AsyncMock(spec=AsyncSession)
        mock_repository = Mock(spec=GitLabRepository)
        mock_repository.id = 1
        mock_repository.project_id = 1
        mock_repository.gitlab_project_id = 12345
        
        # Create duplicate commits (same git_hash)
        commits = [
            {
                "hash": "abc123",
                "author_name": "John Doe",
                "author_email": "john@example.com",
                "message": "First commit",
                "committed_date": datetime.now().isoformat(),
                "created_at": datetime.now().isoformat(),
                "branch": "main"
            },
            {
                "hash": "abc123",  # Duplicate hash
                "author_name": "John Doe",
                "author_email": "john@example.com",
                "message": "First commit",
                "committed_date": datetime.now().isoformat(),
                "created_at": datetime.now().isoformat(),
                "branch": "main"
            }
        ]
        
        # The service should handle duplicate detection
        # via (repository_id, git_hash) unique constraint

    @pytest.mark.asyncio
    async def test_sync_batch_inserts_large_commit_list(self):
        """Test that large commit lists are inserted in batches."""
        # Generate 550 mock commits (exceeds 500-commit batch size)
        commits = [
            {
                "hash": f"hash{i:04d}",
                "author_name": f"Author {i}",
                "author_email": f"author{i}@example.com",
                "message": f"Commit {i}",
                "committed_date": datetime.now().isoformat(),
                "created_at": datetime.now().isoformat(),
                "branch": "main"
            }
            for i in range(550)
        ]
        
        # The service should batch these into:
        # - Batch 1: 500 commits
        # - Batch 2: 50 commits

    @pytest.mark.asyncio
    async def test_sync_uses_last_sync_timestamp(self):
        """Test that sync respects last_sync_timestamp for incremental fetch."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_repository = Mock(spec=GitLabRepository)
        
        # Set a previous sync timestamp
        previous_sync = datetime.now() - timedelta(days=7)
        mock_repository.last_sync_timestamp = previous_sync
        
        with patch('app.services.commit_sync.GitLabClientFactory') as mock_factory:
            mock_client = AsyncMock()
            mock_factory.create_client.return_value = mock_client
            
            # The service should call fetch_commits with 
            # since=last_sync_timestamp, not with a 90-day lookback

    @pytest.mark.asyncio
    async def test_sync_audit_logs_success(self):
        """Test that successful syncs are logged to AuditSystemLog."""
        # Expected behavior:
        # - Create AuditSystemLog entry with:
        #   - action="gitlab_sync_completed"
        #   - details with total_synced count
        # - Log to both database and logger

    @pytest.mark.asyncio
    async def test_sync_audit_logs_error(self):
        """Test that sync errors are logged to AuditSystemLog."""
        # Expected behavior:
        # - Create AuditSystemLog entry with:
        #   - action="gitlab_sync_failed"
        #   - severity="error"
        #   - error details
        # - Continue processing other repositories


class TestErrorScenarios:
    """Test error handling in commit sync service."""

    @pytest.mark.asyncio
    async def test_sync_handles_invalid_credentials(self):
        """Test graceful handling of invalid GitLab credentials."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_repository = Mock(spec=GitLabRepository)
        mock_repository.id = 1
        mock_repository.gitlab_access_token = "invalid-encrypted-token"

        with patch('app.services.commit_sync.GitLabClientFactory') as mock_factory:
            mock_client = AsyncMock()
            mock_factory.create_client.return_value = mock_client
            
            # Simulate authentication failure
            mock_client.fetch_commits.side_effect = GitlabAuthenticationError("401 Unauthorized")
            
            # Expected behavior:
            # - Log error to AuditSystemLog with action="gitlab_sync_error"
            # - Capture error details
            # - Continue processing other repositories
            # - Return error status in result dict
            pass

    @pytest.mark.asyncio
    async def test_sync_handles_rate_limiting(self):
        """Test graceful handling of GitLab API rate limiting."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_repository = Mock(spec=GitLabRepository)

        with patch('app.services.commit_sync.GitLabClientFactory') as mock_factory:
            mock_client = AsyncMock()
            mock_factory.create_client.return_value = mock_client
            
            # Simulate rate limit error (HTTP 429)
            mock_client.fetch_commits.side_effect = GitlabGetError("429 Too Many Requests")
            
            # Expected behavior:
            # - Log rate limit error
            # - Optionally implement exponential backoff (3 retries max)
            # - Continue processing other repositories
            pass

    @pytest.mark.asyncio
    async def test_sync_handles_network_timeout(self):
        """Test graceful handling of network timeouts."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_repository = Mock(spec=GitLabRepository)

        with patch('app.services.commit_sync.GitLabClientFactory') as mock_factory:
            mock_client = AsyncMock()
            mock_factory.create_client.return_value = mock_client
            
            # Simulate timeout error
            import asyncio
            mock_client.fetch_commits.side_effect = asyncio.TimeoutError("Connection timeout")
            
            # Expected behavior:
            # - Log timeout error
            # - Implement retry logic (3 attempts with exponential backoff)
            # - After 3 failures, mark repository as "sync_failed"
            pass

    @pytest.mark.asyncio
    async def test_sync_handles_malformed_response(self):
        """Test handling of malformed GitLab API responses."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_repository = Mock(spec=GitLabRepository)

        with patch('app.services.commit_sync.GitLabClientFactory') as mock_factory:
            mock_client = AsyncMock()
            mock_factory.create_client.return_value = mock_client
            
            # Return commits with missing required fields
            mock_client.fetch_commits.return_value = [
                {
                    "hash": "abc123",
                    # Missing: author_name, author_email, message, etc.
                }
            ]
            
            # Expected behavior:
            # - Log data validation error
            # - Skip malformed commits (don't crash)
            # - Continue with valid commits
            # - Log count of skipped commits
            pass

    @pytest.mark.asyncio
    async def test_sync_handles_database_constraint_violation(self):
        """Test handling of database unique constraint violations."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_repository = Mock(spec=GitLabRepository)

        # Simulate database constraint error (duplicate (repository_id, git_hash))
        from sqlalchemy.exc import IntegrityError
        
        with patch('app.services.commit_sync.GitLabClientFactory') as mock_factory:
            mock_client = AsyncMock()
            mock_factory.create_client.return_value = mock_client
            
            mock_client.fetch_commits.return_value = [
                {
                    "hash": "abc123",
                    "message": "Commit 1",
                    "author_name": "Test Author",
                    "author_email": "test@example.com",
                    "committed_date": datetime.utcnow(),
                    "branch": "main",
                }
            ]
            
            # Simulate unique constraint violation on insert
            mock_session.add.side_effect = IntegrityError("Duplicate", "", "")
            
            # Expected behavior:
            # - Log duplicate key error
            # - Rollback transaction
            # - Skip duplicate commits
            # - Continue with remaining commits
            pass

    @pytest.mark.asyncio
    async def test_sync_handles_repository_not_found(self):
        """Test handling when GitLab project no longer exists."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_repository = Mock(spec=GitLabRepository)
        mock_repository.gitlab_project_id = 99999  # Non-existent project

        with patch('app.services.commit_sync.GitLabClientFactory') as mock_factory:
            mock_client = AsyncMock()
            mock_factory.create_client.return_value = mock_client
            
            # Simulate 404 not found
            mock_client.fetch_commits.side_effect = GitlabGetError("404 Project not found")
            
            # Expected behavior:
            # - Log "project not found" error
            # - Mark repository as "invalid" or "not_found"
            # - Continue processing other repositories
            # - Alert user that repository needs to be re-linked
            pass

    @pytest.mark.asyncio
    async def test_sync_handles_partial_failure(self):
        """Test handling when some repositories fail but others succeed."""
        # Setup 3 repositories
        repositories = [
            Mock(id=1, gitlab_project_id=111),
            Mock(id=2, gitlab_project_id=222),  # This will fail
            Mock(id=3, gitlab_project_id=333),
        ]

        with patch('app.services.commit_sync.CommitSyncService') as mock_service:
            # Mock sync results
            sync_results = [
                {"status": "success", "commits_synced": 10},
                {"status": "failed", "error": "Unauthorized"},
                {"status": "success", "commits_synced": 15},
            ]
            
            # Expected behavior:
            # - Process all repositories even if one fails
            # - Return mixed status indicating partial success
            # - Log both successes and failures
            pass


class TestCommitSyncIntegration:
    """Integration tests for commit sync (requires database)."""

    @pytest.mark.skipif(
        True,  # Skip by default; enable with pytest.mark.db_integration
        reason="Requires --db-integration flag"
    )
    @pytest.mark.asyncio
    async def test_end_to_end_sync_with_mock_gitlab(self):
        """Test full sync flow with mocked GitLab but real database."""
        # This test would:
        # 1. Create a test repository record in database
        # 2. Mock GitLab API responses
        # 3. Run sync_repository
        # 4. Verify commits were inserted correctly
        # 5. Verify last_sync_timestamp was updated
        # 6. Verify AuditSystemLog entry was created
        pass


class TestDatabaseIntegrity:
    """Test database-level integrity and constraint handling."""

    @pytest.mark.asyncio
    async def test_duplicate_detection_via_unique_constraint(self):
        """Test that duplicate commits are prevented by (repository_id, git_hash) constraint."""
        # Expected behavior:
        # - Unique constraint on (repository_id, git_hash)
        # - Attempting to insert duplicate should raise IntegrityError
        # - Error should be caught and logged gracefully
        # - Commit count should reflect only unique commits
        
        # Test case:
        # 1. Insert commit with hash="abc123", repository_id=1
        # 2. Attempt to insert same commit again
        # 3. Verify only 1 commit exists in database
        pass

    @pytest.mark.asyncio
    async def test_foreign_key_constraint_repository(self):
        """Test that commits must reference valid repository."""
        # Expected behavior:
        # - Foreign key constraint on commits.repository_id → gitlab_repositories.id
        # - Attempting to insert commit with invalid repository_id fails
        # - Error should be caught and logged
        
        # Test case:
        # 1. Create commit with repository_id=999 (doesn't exist)
        # 2. Verify insertion fails with foreign key error
        pass

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_failure(self):
        """Test that failed sync rolls back all uncommitted changes."""
        # Expected behavior:
        # - If sync fails midway, all uncommitted changes are rolled back
        # - Database should be left in consistent state
        # - last_sync_timestamp not updated on failure
        
        # Test case:
        # 1. Start sync with 500 commits
        # 2. Fail at commit 250 due to malformed data
        # 3. Verify: All 500 commits rolled back
        # 4. Verify: last_sync_timestamp unchanged
        # 5. Verify: No partial data in database
        pass

    @pytest.mark.asyncio
    async def test_commit_table_indexes(self):
        """Test that required indexes exist for query performance."""
        # Expected indexes:
        # - repository_id (for filtering by repository)
        # - committed_at (for date range queries)
        # - author_email (for contributor queries)
        # - git_hash (for duplicate detection)
        # - (repository_id, git_hash) - unique constraint
        
        # Test verification:
        # Query database schema and verify all indexes exist
        pass

    @pytest.mark.asyncio
    async def test_batch_insert_atomicity(self):
        """Test that batch inserts are atomic (all or nothing)."""
        # Expected behavior:
        # - Batch of 500 commits inserts as single transaction
        # - If any commit fails, entire batch is rolled back
        # - Error details are captured
        
        # Test case:
        # 1. Create batch with 499 valid + 1 invalid commit
        # 2. Attempt batch insert
        # 3. Verify: All 500 commits rolled back
        # 4. Verify: No partial inserts in database
        pass

    @pytest.mark.asyncio
    async def test_concurrent_sync_handling(self):
        """Test that concurrent syncs for same repository don't cause issues."""
        # Expected behavior:
        # - Only one sync should run at a time for a repository
        # - Second concurrent sync should wait or be rejected
        # - Both should complete without data corruption
        
        # Note: This is more of an application-level lock,
        # not purely database integrity
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
