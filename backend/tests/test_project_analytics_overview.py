"""Tests for the live project analytics overview endpoint."""

from datetime import datetime, timedelta

import pytest

from app.models import Category, Division, Project, ProjectTask, ProjectTeam, ProjectTeamMember, ProjectWorkspace, Team, User, Worker, WorkerKPI
from app.routes.dependencies import require_auth
from app.services import hash_password


@pytest.mark.asyncio
async def test_project_analytics_overview_returns_live_metrics(test_app, test_db):
    async with test_db() as db:
        user = User(
            email="analytics@example.com",
            password_hash=hash_password("Test@1234"),
            full_name="Analytics User",
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
            full_name="Sarah J.",
            email="sarah@example.com",
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

        workspace = ProjectWorkspace(
            name="Main Workspace",
            description="Main workspace",
            is_active=True,
        )
        db.add(workspace)
        await db.flush()

        project = Project(
            workspace_id=workspace.workspace_id,
            name="Team Analytics Project",
            description="Live analytics project",
            status="active",
            created_by=user.user_id,
            start_date="2023-09-01",
            end_date="2023-09-15",
        )
        db.add(project)
        await db.flush()

        team = ProjectTeam(
            project_id=project.project_id,
            team_id=team_record.team_id,
            role="lead",
        )
        db.add(team)
        await db.flush()

        db.add(ProjectTeamMember(
            project_team_id=team.project_team_id,
            worker_id=worker.worker_id,
            role="engineer",
            allocation_percentage=100,
        ))

        db.add(WorkerKPI(
            worker_id=worker.worker_id,
            project_id=project.project_id,
            score=95,
            is_manual_override=False,
            metrics={},
        ))

        now = datetime.utcnow()
        db.add_all(
            [
                ProjectTask(
                    project_id=project.project_id,
                    title="Current sprint task",
                    description="Recent completed work",
                    status="completed",
                    priority="medium",
                    story_points=8,
                    assigned_to=worker.worker_id,
                    created_by=user.user_id,
                    updated_at=now - timedelta(days=1),
                ),
                ProjectTask(
                    project_id=project.project_id,
                    title="Previous sprint task",
                    description="Earlier completed work",
                    status="completed",
                    priority="medium",
                    story_points=5,
                    assigned_to=worker.worker_id,
                    created_by=user.user_id,
                    updated_at=now - timedelta(days=40),
                ),
            ]
        )
        await db.commit()

    app = test_app
    app.dependency_overrides[require_auth] = lambda: user

    from httpx import ASGITransport, AsyncClient

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as client:
        response = await client.get(f"/projects/{project.project_id}/analytics-overview")

    assert response.status_code == 200
    payload = response.json()["data"]

    assert payload["teamVelocity"]["current"] == 8
    assert payload["teamVelocity"]["previous"] == 5
    assert len(payload["engineers"]) == 1
    assert payload["engineers"][0]["name"] == "Sarah J."
    assert payload["engineers"][0]["status"] == "optimal"
    assert len(payload["insights"]) == 2
