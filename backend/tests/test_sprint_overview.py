"""Tests for the live sprint overview endpoint."""

from datetime import datetime, timedelta

import pytest

from app.models import Category, Division, Project, ProjectTask, ProjectTeam, ProjectTeamMember, ProjectWorkspace, Team, User, Worker
from app.routes.dependencies import require_auth
from app.services import hash_password


@pytest.mark.asyncio
async def test_sprint_overview_returns_live_sprint_data(test_app, test_db):
    async with test_db() as db:
        user = User(
            email="sprint@example.com",
            password_hash=hash_password("Test@1234"),
            full_name="Sprint User",
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

        team = Team(
            name="Core Team",
            category_id=category.category_id,
            description="Core team",
            status="active",
            capacity_hours=160,
        )
        db.add(team)
        await db.flush()

        workspace = ProjectWorkspace(name="Main Workspace", description="Main workspace", is_active=True)
        db.add(workspace)
        await db.flush()

        project = Project(
            workspace_id=workspace.workspace_id,
            name="Project 3",
            description="Sprint project",
            status="active",
            created_by=user.user_id,
            start_date="2026-05-01",
            end_date="2026-05-31",
            updated_at=datetime.utcnow(),
        )
        db.add(project)
        await db.flush()

        project_team = ProjectTeam(project_id=project.project_id, team_id=team.team_id, role="lead")
        db.add(project_team)
        await db.flush()

        db.add(ProjectTeamMember(project_team_id=project_team.project_team_id, worker_id=worker.worker_id, role="engineer", allocation_percentage=100))

        db.add_all(
            [
                ProjectTask(
                    project_id=project.project_id,
                    title="Completed task",
                    description="Done",
                    status="completed",
                    priority="medium",
                    story_points=5,
                    created_by=user.user_id,
                    updated_at=datetime.utcnow(),
                ),
                ProjectTask(
                    project_id=project.project_id,
                    title="Open blocker",
                    description="Needs attention",
                    status="in_progress",
                    priority="high",
                    story_points=3,
                    created_by=user.user_id,
                    updated_at=datetime.utcnow(),
                ),
            ]
        )
        await db.commit()

    app = test_app
    app.dependency_overrides[require_auth] = lambda: user

    from httpx import ASGITransport, AsyncClient

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as client:
        response = await client.get(f"/projects/{project.project_id}/sprint-overview")

    assert response.status_code == 200
    payload = response.json()["data"]

    assert payload["sprint"]["name"] == "Project 3 Active Sprint"
    assert payload["sprint"]["storyPointGoal"] == 8
    assert payload["stats"][0]["value"] == "8"
    assert payload["stats"][1]["value"] == "5"
    assert payload["stats"][2]["value"] == "3"
    assert payload["members"][0]["avatar"] == "AL"
    assert payload["tasks"][0]["id"].isdigit()
    assert len(payload["velocity"]) == 4
    assert payload["insights"]["status"] in {"on_track", "at_risk"}
