"""Tests for the live projects overview endpoint."""

from datetime import datetime, timedelta

import pytest

from app.models import Category, Division, Project, ProjectTask, ProjectTeam, ProjectTeamMember, ProjectWorkspace, Team, User, Worker
from app.models.gitlab import Commit, GitLabRepository
from app.routes.dependencies import require_auth
from app.services import hash_password


@pytest.mark.asyncio
async def test_projects_overview_returns_live_project_data(test_app, test_db):
    async with test_db() as db:
        user = User(
            email="projects@example.com",
            password_hash=hash_password("Test@1234"),
            full_name="Projects User",
            is_active=True,
        )
        db.add(user)
        await db.flush()

        division = Division(name="Engineering", description="Engineering")
        db.add(division)
        await db.flush()

        category = Category(name="Platform", division_id=division.division_id)
        db.add(category)
        await db.flush()

        worker = Worker(
            division_id=division.division_id,
            full_name="Ayu Lestari",
            email="ayu@example.com",
            employment_status="active",
        )
        db.add(worker)
        await db.flush()

        team_record = Team(
            name="Core Team",
            category_id=category.category_id,
            description="Core team",
            status="active",
            capacity_hours=160,
        )
        db.add(team_record)
        await db.flush()

        workspace = ProjectWorkspace(name="Main Workspace", description="Main workspace", is_active=True)
        db.add(workspace)
        await db.flush()

        project = Project(
            workspace_id=workspace.workspace_id,
            name="frontend-dashboard-v2",
            description="Frontend workspace",
            status="active",
            created_by=user.user_id,
            repository_url="https://gitlab.com/acme/frontend-dashboard-v2",
            repository_type="gitlab",
            updated_at=datetime.utcnow(),
        )
        db.add(project)
        await db.flush()

        team = ProjectTeam(project_id=project.project_id, team_id=team_record.team_id, role="lead")
        db.add(team)
        await db.flush()

        db.add(ProjectTeamMember(project_team_id=team.project_team_id, worker_id=worker.worker_id, role="engineer", allocation_percentage=100))

        repository = GitLabRepository(
            project_id=project.project_id,
            gitlab_project_id=42,
            gitlab_url="https://gitlab.com",
            gitlab_access_token="encrypted-token",
            last_sync_timestamp=datetime.utcnow(),
        )
        db.add(repository)
        await db.flush()

        db.add_all(
            [
                ProjectTask(
                    project_id=project.project_id,
                    title="Completed task",
                    description="Done",
                    status="completed",
                    priority="medium",
                    created_by=user.user_id,
                ),
                ProjectTask(
                    project_id=project.project_id,
                    title="Open blocker",
                    description="Needs attention",
                    status="in_progress",
                    priority="high",
                    created_by=user.user_id,
                ),
            ]
        )

        now = datetime.utcnow()
        db.add_all(
            [
                Commit(
                    repository_id=repository.id,
                    git_hash="a" * 40,
                    author_name="Ayu Lestari",
                    author_email="ayu@example.com",
                    message="feat: recent commit 1",
                    committed_at=now - timedelta(days=1),
                    branch="main",
                ),
                Commit(
                    repository_id=repository.id,
                    git_hash="b" * 40,
                    author_name="Ayu Lestari",
                    author_email="ayu@example.com",
                    message="feat: recent commit 2",
                    committed_at=now - timedelta(days=2),
                    branch="main",
                ),
                Commit(
                    repository_id=repository.id,
                    git_hash="c" * 40,
                    author_name="Ayu Lestari",
                    author_email="ayu@example.com",
                    message="feat: previous commit",
                    committed_at=now - timedelta(days=10),
                    branch="main",
                ),
            ]
        )
        await db.commit()

    app = test_app
    app.dependency_overrides[require_auth] = lambda: user

    from httpx import ASGITransport, AsyncClient

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as client:
        response = await client.get("/projects/overview")

    assert response.status_code == 200
    payload = response.json()["data"]

    assert len(payload["projects"]) == 1
    project_payload = payload["projects"][0]
    assert project_payload["name"] == "frontend-dashboard-v2"
    assert project_payload["status"] == "critical"
    assert project_payload["progress"] == 50
    assert project_payload["commitVelocity"] == 2
    assert project_payload["healthDelta"] == 100
    assert project_payload["members"][0]["avatar"] == "AL"

    assert len(payload["repositories"]) == 1
    assert payload["repositories"][0]["status"] == "syncing"
