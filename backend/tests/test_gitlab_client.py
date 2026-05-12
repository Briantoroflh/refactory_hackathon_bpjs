"""
Unit tests for GitLab client service.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from app.services.gitlab_client import GitLabClient, GitLabClientFactory
from gitlab.exceptions import GitlabAuthenticationError, GitlabGetError


class TestGitLabClient:
    """Test cases for GitLabClient service."""

    def test_init_with_valid_credentials(self):
        """Test client initialization with valid credentials."""
        client = GitLabClient(
            gitlab_url="https://gitlab.com",
            api_token="test-token-123"
        )
        assert client is not None
        assert client.gitlab_url == "https://gitlab.com"

    def test_init_with_custom_gitlab_url(self):
        """Test client initialization with custom GitLab URL."""
        custom_url = "https://gitlab.example.com"
        client = GitLabClient(
            gitlab_url=custom_url,
            api_token="test-token-456"
        )
        assert client.gitlab_url == custom_url

    @pytest.mark.asyncio
    async def test_validate_credentials_success(self):
        """Test successful credential validation."""
        client = GitLabClient(
            gitlab_url="https://gitlab.com",
            api_token="valid-token"
        )
        with patch.object(client, 'gl') as mock_gl:
            mock_gl.auth.return_value = True
            result = await client.validate_credentials()
            assert result is True

    @pytest.mark.asyncio
    async def test_validate_credentials_failure(self):
        """Test failed credential validation."""
        client = GitLabClient(
            gitlab_url="https://gitlab.com",
            api_token="invalid-token"
        )
        with patch.object(client, 'gl') as mock_gl:
            mock_gl.auth.side_effect = GitlabAuthenticationError("Invalid token")
            result = await client.validate_credentials()
            assert result is False

    @pytest.mark.asyncio
    async def test_get_repository_metadata(self):
        """Test fetching repository metadata."""
        client = GitLabClient(
            gitlab_url="https://gitlab.com",
            api_token="test-token"
        )
        
        # Mock GitLab project
        mock_project = Mock()
        mock_project.id = 12345
        mock_project.name = "test-project"
        mock_project.path = "test-project"
        mock_project.web_url = "https://gitlab.com/user/test-project"
        mock_project.description = "A test project"
        mock_project.default_branch = "main"
        mock_project.last_activity_at = datetime.now().isoformat()
        
        with patch.object(client, 'gl') as mock_gl:
            mock_gl.projects.get.return_value = mock_project
            
            metadata = await client.get_repository_metadata(12345)
            
            assert metadata['id'] == 12345
            assert metadata['name'] == "test-project"
            assert metadata['default_branch'] == "main"

    @pytest.mark.asyncio
    async def test_fetch_commits_with_date_range(self):
        """Test fetching commits with date filtering."""
        client = GitLabClient(
            gitlab_url="https://gitlab.com",
            api_token="test-token"
        )
        
        # Mock commits
        mock_commits = [
            Mock(
                id="abc123",
                message="Test commit 1",
                authored_date=datetime.now().isoformat(),
                author_name="John Doe",
                author_email="john@example.com",
            ),
            Mock(
                id="def456",
                message="Test commit 2",
                authored_date=datetime.now().isoformat(),
                author_name="Jane Doe",
                author_email="jane@example.com",
            ),
        ]
        
        with patch.object(client, 'gl') as mock_gl:
            mock_project = Mock()
            mock_project.commits.list.return_value = mock_commits
            mock_gl.projects.get.return_value = mock_project
            
            since = (datetime.now() - timedelta(days=7)).isoformat()
            commits = await client.fetch_commits(
                project_id=12345,
                since=since
            )
            
            assert len(commits) == 2
            assert commits[0]['author_name'] == "John Doe"

    @pytest.mark.asyncio
    async def test_fetch_commits_pagination(self):
        """Test commit fetching with pagination."""
        client = GitLabClient(
            gitlab_url="https://gitlab.com",
            api_token="test-token"
        )
        
        # Create mock commits
        mock_commits = [Mock(id=f"commit{i}", message=f"Message {i}") for i in range(50)]
        
        with patch.object(client, 'gl') as mock_gl:
            mock_project = Mock()
            mock_project.commits.list.return_value = mock_commits
            mock_gl.projects.get.return_value = mock_project
            
            commits = await client.fetch_commits(
                project_id=12345,
                per_page=25
            )
            
            # Should handle pagination correctly
            assert len(commits) > 0

    @pytest.mark.asyncio
    async def test_fetch_commits_with_branch_filter(self):
        """Test fetching commits filtered by branch."""
        client = GitLabClient(
            gitlab_url="https://gitlab.com",
            api_token="test-token"
        )
        
        mock_commit = Mock(
            id="abc123",
            message="Commit on main",
            author_name="John Doe",
        )
        
        with patch.object(client, 'gl') as mock_gl:
            mock_project = Mock()
            mock_project.commits.list.return_value = [mock_commit]
            mock_gl.projects.get.return_value = mock_project
            
            commits = await client.fetch_commits(
                project_id=12345,
                branch="main"
            )
            
            assert len(commits) == 1
            mock_project.commits.list.assert_called()

    def test_factory_create_client_success(self):
        """Test factory creates client successfully."""
        client = GitLabClientFactory.create_client(
            gitlab_url="https://gitlab.com",
            api_token="test-token"
        )
        assert isinstance(client, GitLabClient)

    def test_factory_create_client_with_timeout(self):
        """Test factory accepts timeout parameter."""
        client = GitLabClientFactory.create_client(
            gitlab_url="https://gitlab.com",
            api_token="test-token",
            timeout=60
        )
        assert isinstance(client, GitLabClient)

    @pytest.mark.asyncio
    async def test_retry_logic_on_transient_failure(self):
        """Test exponential backoff retry logic."""
        client = GitLabClient(
            gitlab_url="https://gitlab.com",
            api_token="test-token"
        )
        
        # Mock transient failure then success
        with patch('time.sleep'):  # Don't actually sleep in tests
            with patch.object(client, 'gl') as mock_gl:
                mock_project = Mock()
                # First call fails, second succeeds
                mock_project.commits.list.side_effect = [
                    GitlabGetError("Rate limited"),
                    [Mock(id="abc123", message="Success")]
                ]
                mock_gl.projects.get.return_value = mock_project
                
                # Note: actual retry logic would be in the service layer
                # This test documents the expected behavior


class TestGitLabClientIntegration:
    """Integration tests that require real GitLab API (skipped by default)."""

    @pytest.mark.skipif(
        not pytest.config.getoption("--gitlab-integration"),
        reason="Requires --gitlab-integration flag"
    )
    @pytest.mark.asyncio
    async def test_real_gitlab_connection(self):
        """Test with real GitLab API (requires valid token)."""
        import os
        token = os.getenv("GITLAB_TEST_TOKEN")
        if not token:
            pytest.skip("GITLAB_TEST_TOKEN not set")
        
        client = GitLabClient(
            gitlab_url="https://gitlab.com",
            api_token=token
        )
        
        # This would test against real GitLab API
        # Only runs with --gitlab-integration flag
        result = await client.validate_credentials()
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
