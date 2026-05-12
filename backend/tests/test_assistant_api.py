"""API tests for AI assistant workflows, role checks, and error handling."""
import pytest
import json
from unittest.mock import AsyncMock, patch
from fastapi import status

from app.models import User, Role, UserRole
from app.services import hash_password, encode_token


@pytest.mark.asyncio
async def test_planning_workflow_success(client, test_db, test_user):
    """Test successful planning workflow request."""
    async with test_db() as db:
        # Create admin role and assign to user
        role = Role(name="admin")
        db.add(role)
        await db.commit()
        await db.refresh(role)

        user_role = UserRole(user_id=test_user.user_id, role_id=role.role_id)
        db.add(user_role)
        await db.commit()

    # Create access token
    token = encode_token({"sub": str(test_user.user_id), "type": "access"})

    with patch("app.services.assistant.run_workflow") as mock_run:
        mock_run.return_value = {
            "workflow": "planning",
            "status": "completed",
            "model": "test-model",
            "content": '{"summary": "Test summary"}',
            "structured_output": {"summary": "Test summary"},
            "source": "openrouter",
        }

        response = await client.post(
            "/ai-assistant/planning",
            json={"prompt": "Create a project plan", "context": {"project_id": 1}},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["workflow"] == "planning"
    assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_sprint_summary_workflow_success(client, test_db, test_user):
    """Test successful sprint summary workflow request."""
    async with test_db() as db:
        # Create team_lead role
        role = Role(name="team_lead")
        db.add(role)
        await db.commit()
        await db.refresh(role)

        user_role = UserRole(user_id=test_user.user_id, role_id=role.role_id)
        db.add(user_role)
        await db.commit()

    token = encode_token({"sub": str(test_user.user_id), "type": "access"})

    with patch("app.services.assistant.run_workflow") as mock_run:
        mock_run.return_value = {
            "workflow": "sprint_summary",
            "status": "completed",
            "model": "test-model",
            "content": '{"summary": "Sprint completed"}',
            "structured_output": {"summary": "Sprint completed"},
            "source": "openrouter",
        }

        response = await client.post(
            "/ai-assistant/sprint-summary",
            json={"prompt": "Summarize sprint", "context": {"sprint_id": 1}},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_workflow_missing_authentication(client):
    """Test workflow request without authentication."""
    response = await client.post(
        "/ai-assistant/planning",
        json={"prompt": "Create a project plan", "context": {}},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in response.json()["detail"]


@pytest.mark.asyncio
async def test_workflow_invalid_token(client):
    """Test workflow request with invalid token."""
    response = await client.post(
        "/ai-assistant/planning",
        json={"prompt": "Create a project plan", "context": {}},
        headers={"Authorization": "Bearer invalid_token"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_workflow_role_denied_for_engineer(client, test_db, test_user):
    """Test that engineer cannot access planning endpoint."""
    async with test_db() as db:
        # Create engineer role (not allowed for planning)
        role = Role(name="engineer")
        db.add(role)
        await db.commit()
        await db.refresh(role)

        user_role = UserRole(user_id=test_user.user_id, role_id=role.role_id)
        db.add(user_role)
        await db.commit()

    token = encode_token({"sub": str(test_user.user_id), "type": "access"})

    response = await client.post(
        "/ai-assistant/planning",
        json={"prompt": "Create a project plan", "context": {}},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "AI access denied" in response.json()["detail"]


@pytest.mark.asyncio
async def test_workflow_admin_bypasses_role_check(client, test_db, test_user):
    """Test that admin can access all workflows regardless of role restrictions."""
    async with test_db() as db:
        # Create both admin and engineer roles
        admin_role = Role(name="admin")
        engineer_role = Role(name="engineer")
        db.add(admin_role)
        db.add(engineer_role)
        await db.commit()
        await db.refresh(admin_role)
        await db.refresh(engineer_role)

        # Assign both roles to user
        for role in [admin_role, engineer_role]:
            user_role = UserRole(user_id=test_user.user_id, role_id=role.role_id)
            db.add(user_role)
        await db.commit()

    token = encode_token({"sub": str(test_user.user_id), "type": "access"})

    with patch("app.services.assistant.run_workflow") as mock_run:
        mock_run.return_value = {
            "workflow": "planning",
            "status": "completed",
            "model": "test-model",
            "content": "{}",
            "structured_output": {},
            "source": "openrouter",
        }

        response = await client.post(
            "/ai-assistant/planning",
            json={"prompt": "Create a project plan", "context": {}},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_workflow_async_mode(client, test_db, test_user):
    """Test workflow request with async_mode=true."""
    async with test_db() as db:
        role = Role(name="admin")
        db.add(role)
        await db.commit()
        await db.refresh(role)

        user_role = UserRole(user_id=test_user.user_id, role_id=role.role_id)
        db.add(user_role)
        await db.commit()

    token = encode_token({"sub": str(test_user.user_id), "type": "access"})

    response = await client.post(
        "/ai-assistant/planning",
        json={
            "prompt": "Create a project plan",
            "context": {"project_id": 1},
            "async_mode": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"


@pytest.mark.asyncio
async def test_workflow_service_error_handling(client, test_db, test_user):
    """Test handling of AI service errors."""
    async with test_db() as db:
        role = Role(name="admin")
        db.add(role)
        await db.commit()
        await db.refresh(role)

        user_role = UserRole(user_id=test_user.user_id, role_id=role.role_id)
        db.add(user_role)
        await db.commit()

    token = encode_token({"sub": str(test_user.user_id), "type": "access"})

    from app.services.assistant import AIServiceError

    with patch("app.services.assistant.run_workflow") as mock_run:
        mock_run.side_effect = AIServiceError("Service unavailable", status_code=503)

        response = await client.post(
            "/ai-assistant/planning",
            json={"prompt": "Create a project plan", "context": {}},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "Service unavailable" in response.json()["detail"]


@pytest.mark.asyncio
async def test_all_workflow_endpoints_with_valid_role(client, test_db, test_user):
    """Test all workflow endpoints are accessible with proper roles."""
    async with test_db() as db:
        # Create required roles for each workflow
        roles_data = {
            "admin": {
                "planning": True,
                "sprint_summary": True,
                "standup_recap": True,
                "task_recommendation": True,
                "workload_suggestion": True,
                "ticket_explanation": True,
                "documentation_helper": True,
                "bug_analysis": True,
                "kanban_jobdesk": True,
            },
        }

        role = Role(name="admin")
        db.add(role)
        await db.commit()
        await db.refresh(role)

        user_role = UserRole(user_id=test_user.user_id, role_id=role.role_id)
        db.add(user_role)
        await db.commit()

    token = encode_token({"sub": str(test_user.user_id), "type": "access"})

    endpoints = [
        ("/ai-assistant/planning", {"prompt": "Create plan", "context": {}}),
        ("/ai-assistant/sprint-summary", {"prompt": "Summarize sprint", "context": {}}),
        ("/ai-assistant/standup-recap", {"prompt": "Recap standup", "context": {}}),
        ("/ai-assistant/task-recommendation", {"prompt": "Recommend tasks", "context": {}}),
        ("/ai-assistant/workload-suggestion", {"prompt": "Suggest workload", "context": {}}),
        ("/ai-assistant/ticket-explanation", {"prompt": "Explain ticket", "context": {}}),
        ("/ai-assistant/documentation-helper", {"prompt": "Help document", "context": {}}),
        ("/ai-assistant/bug-analysis", {"prompt": "Analyze bug", "context": {}}),
        ("/ai-assistant/kanban-jobdesk", {"prompt": "Generate kanban", "context": {}}),
    ]

    with patch("app.services.assistant.run_workflow") as mock_run:
        mock_run.return_value = {
            "workflow": "test",
            "status": "completed",
            "model": "test-model",
            "content": "{}",
            "structured_output": {},
            "source": "openrouter",
        }

        for endpoint, payload in endpoints:
            response = await client.post(
                endpoint,
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == status.HTTP_200_OK, f"Failed for {endpoint}"


@pytest.mark.asyncio
async def test_user_without_role_assignment_denied(client, test_db, test_user):
    """Test that user without any role assignment cannot access AI endpoints."""
    # Don't assign any role to the user
    token = encode_token({"sub": str(test_user.user_id), "type": "access"})

    response = await client.post(
        "/ai-assistant/planning",
        json={"prompt": "Create a project plan", "context": {}},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "role assignment" in response.json()["detail"]


@pytest.mark.asyncio
async def test_refresh_token_rejected(client, test_db, test_user):
    """Test that refresh tokens are rejected for API access."""
    async with test_db() as db:
        role = Role(name="admin")
        db.add(role)
        await db.commit()
        await db.refresh(role)

        user_role = UserRole(user_id=test_user.user_id, role_id=role.role_id)
        db.add(user_role)
        await db.commit()

    # Create refresh token (should be rejected)
    token = encode_token({"sub": str(test_user.user_id), "type": "refresh"})

    response = await client.post(
        "/ai-assistant/planning",
        json={"prompt": "Create a project plan", "context": {}},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_team_lead_can_access_planning(client, test_db, test_user):
    """Test that team_lead can access planning workflow."""
    async with test_db() as db:
        role = Role(name="team_lead")
        db.add(role)
        await db.commit()
        await db.refresh(role)

        user_role = UserRole(user_id=test_user.user_id, role_id=role.role_id)
        db.add(user_role)
        await db.commit()

    token = encode_token({"sub": str(test_user.user_id), "type": "access"})

    with patch("app.services.assistant.run_workflow") as mock_run:
        mock_run.return_value = {
            "workflow": "planning",
            "status": "completed",
            "model": "test-model",
            "content": "{}",
            "structured_output": {},
            "source": "openrouter",
        }

        response = await client.post(
            "/ai-assistant/planning",
            json={"prompt": "Create plan", "context": {}},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_project_manager_can_access_task_recommendation(client, test_db, test_user):
    """Test that project_manager can access task_recommendation workflow."""
    async with test_db() as db:
        role = Role(name="project_manager")
        db.add(role)
        await db.commit()
        await db.refresh(role)

        user_role = UserRole(user_id=test_user.user_id, role_id=role.role_id)
        db.add(user_role)
        await db.commit()

    token = encode_token({"sub": str(test_user.user_id), "type": "access"})

    with patch("app.services.assistant.run_workflow") as mock_run:
        mock_run.return_value = {
            "workflow": "task_recommendation",
            "status": "completed",
            "model": "test-model",
            "content": "{}",
            "structured_output": {},
            "source": "openrouter",
        }

        response = await client.post(
            "/ai-assistant/task-recommendation",
            json={"prompt": "Recommend tasks", "context": {}},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_engineer_can_access_bug_analysis(client, test_db, test_user):
    """Test that engineer can access bug_analysis workflow."""
    async with test_db() as db:
        role = Role(name="engineer")
        db.add(role)
        await db.commit()
        await db.refresh(role)

        user_role = UserRole(user_id=test_user.user_id, role_id=role.role_id)
        db.add(user_role)
        await db.commit()

    token = encode_token({"sub": str(test_user.user_id), "type": "access"})

    with patch("app.services.assistant.run_workflow") as mock_run:
        mock_run.return_value = {
            "workflow": "bug_analysis",
            "status": "completed",
            "model": "test-model",
            "content": "{}",
            "structured_output": {},
            "source": "openrouter",
        }

        response = await client.post(
            "/ai-assistant/bug-analysis",
            json={"prompt": "Analyze bug", "context": {}},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_engineer_cannot_access_planning(client, test_db, test_user):
    """Test that engineer cannot access planning workflow (role-restricted)."""
    async with test_db() as db:
        role = Role(name="engineer")
        db.add(role)
        await db.commit()
        await db.refresh(role)

        user_role = UserRole(user_id=test_user.user_id, role_id=role.role_id)
        db.add(user_role)
        await db.commit()

    token = encode_token({"sub": str(test_user.user_id), "type": "access"})

    response = await client.post(
        "/ai-assistant/planning",
        json={"prompt": "Create plan", "context": {}},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
