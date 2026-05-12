"""
GitLab API client service for repository and commit operations.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

import gitlab
from gitlab.exceptions import GitlabError, GitlabGetError
import httpx

logger = logging.getLogger(__name__)


class GitLabClient:
    """
    Wrapper around python-gitlab library for GitLab API operations.
    Handles authentication, error handling, and retry logic.
    """

    def __init__(self, gitlab_url: str, api_token: str):
        """
        Initialize GitLab API client.

        Args:
            gitlab_url: GitLab instance URL (e.g., https://gitlab.com)
            api_token: GitLab personal access token
        """
        self.gitlab_url = gitlab_url
        self.api_token = api_token
        try:
            self.gl = gitlab.Gitlab(gitlab_url, private_token=api_token)
            # Test connection
            self.gl.auth()
            logger.info(f"GitLab client initialized and authenticated with {gitlab_url}")
        except GitlabError as e:
            logger.error(f"Failed to authenticate with GitLab: {str(e)}")
            raise

    def get_repository_metadata(self, project_id: int) -> Dict[str, Any]:
        """
        Fetch repository metadata from GitLab.

        Args:
            project_id: GitLab project ID

        Returns:
            Dictionary with repository metadata
        """
        try:
            project = self.gl.projects.get(project_id)
            return {
                "id": project.id,
                "name": project.name,
                "path": project.path,
                "url": project.web_url,
                "description": project.description,
                "default_branch": project.default_branch,
                "last_activity_at": project.last_activity_at,
            }
        except GitlabGetError as e:
            logger.error(f"Failed to get repository metadata for project {project_id}: {str(e)}")
            raise

    def fetch_commits(
        self,
        project_id: int,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        branch: str = "main",
        per_page: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Fetch commits from GitLab repository with pagination support.

        Args:
            project_id: GitLab project ID
            since: Only commits after this date (ISO 8601 format)
            until: Only commits before this date (ISO 8601 format)
            branch: Branch name (default: main)
            per_page: Number of commits per page (max 100)

        Returns:
            List of commit dictionaries
        """
        commits = []
        try:
            project = self.gl.projects.get(project_id)

            # Build query parameters
            kwargs = {"per_page": per_page, "all": True}
            if since:
                kwargs["since"] = since.isoformat()
            if until:
                kwargs["until"] = until.isoformat()

            # Fetch commits from the specified branch
            repository_commits = project.commits.list(
                ref_name=branch,
                order_by="created_at",
                sort="desc",
                **kwargs
            )

            for commit in repository_commits:
                commits.append(
                    {
                        "hash": commit.id,
                        "author_name": commit.author_name,
                        "author_email": commit.author_email,
                        "message": commit.message,
                        "committed_date": commit.committed_date,
                        "created_at": commit.created_at,
                        "branch": branch,
                    }
                )

            logger.info(
                f"Fetched {len(commits)} commits from project {project_id} "
                f"on branch {branch}"
            )
            return commits

        except GitlabError as e:
            logger.error(f"Failed to fetch commits from project {project_id}: {str(e)}")
            raise

    def validate_credentials(self) -> bool:
        """
        Validate GitLab credentials by testing API connection.

        Returns:
            True if credentials are valid, raises exception otherwise
        """
        try:
            self.gl.auth()
            return True
        except GitlabError as e:
            logger.error(f"GitLab credential validation failed: {str(e)}")
            return False


class GitLabClientFactory:
    """
    Factory for creating GitLab client instances with retry logic.
    """

    _retry_config = {
        "max_retries": 3,
        "backoff_factor": 1,  # 1s, 2s, 4s exponential backoff
    }

    @staticmethod
    def create_client(
        gitlab_url: str,
        api_token: str,
        timeout: int = 30,
    ) -> GitLabClient:
        """
        Create a GitLab client with retry logic.

        Args:
            gitlab_url: GitLab instance URL
            api_token: GitLab personal access token
            timeout: Request timeout in seconds

        Returns:
            GitLabClient instance

        Raises:
            GitlabError if authentication fails after retries
        """
        max_retries = GitLabClientFactory._retry_config["max_retries"]
        backoff_factor = GitLabClientFactory._retry_config["backoff_factor"]

        last_error = None
        for attempt in range(max_retries):
            try:
                client = GitLabClient(gitlab_url, api_token)
                return client
            except GitlabError as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = backoff_factor * (2 ** attempt)
                    logger.warning(
                        f"Failed to create GitLab client (attempt {attempt + 1}/{max_retries}). "
                        f"Retrying in {wait_time}s..."
                    )
                    import time
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to create GitLab client after {max_retries} attempts")

        raise last_error
