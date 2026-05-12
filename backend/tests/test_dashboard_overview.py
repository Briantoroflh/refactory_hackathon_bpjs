"""
Tests for the live dashboard overview endpoint.
"""

import pytest
from datetime import datetime

from app.controllers.auth import get_current_user
from app.models import Category, Division, Project, ProjectTask, ProjectWorkspace, Team, User
from app.services import hash_password


@pytest.mark.asyncio
async def test_dashboard_overview_returns_live_counts(test_app, test_db):
    async with test_db() as db:
        user = User(
            email="dashboard@example.com",
            password_hash=hash_password("Test@1234"),
            full_name="Dashboard User",
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

        workspace = ProjectWorkspace(name="Main Workspace", description="Primary workspace", is_active=True)
        db.add(workspace)
        await db.flush()

        project_active = Project(
            workspace_id=workspace.workspace_id,
            name="Active Project",
            description="Active project",
            status="active",
            created_by=user.user_id,
        )
        project_planning = Project(
            workspace_id=workspace.workspace_id,
            name="Planning Project",
            description="Planning project",
            status="planning",
            created_by=user.user_id,
        )
        db.add_all([project_active, project_planning])
        await db.flush()

        team = Team(
            name="Core Team",
            category_id=category.category_id,
            description="Core delivery team",
            status="active",
            capacity_hours=160,
        )
        db.add(team)
        await db.flush()

        db.add_all(
            [
                ProjectTask(
                    project_id=project_active.project_id,
                    title="Done task",
                    description="Finished task",
                    status="completed",
                    priority="medium",
                    created_by=user.user_id,
                    assigned_to=None,
                ),
                ProjectTask(
                    project_id=project_active.project_id,
                    title="Blocking task",
                    description="Needs attention",
                    status="in_progress",
                    priority="high",
                    created_by=user.user_id,
                    assigned_to=None,
                    updated_at=datetime.utcnow(),
                ),
                ProjectTask(
                    project_id=project_planning.project_id,
                    title="Backlog task",
                    description="Still waiting",
                    status="backlog",
                    priority="low",
                    created_by=user.user_id,
                    assigned_to=None,
                ),
            ]
        )
        await db.commit()

    app = test_app
    app.dependency_overrides[get_current_user] = lambda: user

    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as client:
        response = await client.get("/api/v1/dashboard/overview")

    assert response.status_code == 200
    payload = response.json()["data"]

    assert payload["profile"]["name"] == "Dashboard User"
    assert payload["profile"]["projects"] == 2
    assert payload["profile"]["team"] == 1

    stats = {item["title"]: item for item in payload["stats"]}
    assert stats["Projects"]["value"] == "2"
    assert stats["Completion Rate"]["value"] == "33%"
    assert stats["Open Blockers"]["value"] == "1"
    assert len(payload["sprint"]["bars"]) == 5
