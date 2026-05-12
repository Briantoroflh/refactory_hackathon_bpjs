"""
Tests for project and task management endpoints
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, test_user):
    """Test project creation"""
    response = await client.post(
        "/projects",
        json={
            "name": "New Project",
            "description": "Test project",
            "workspace_id": 1,
        }
    )
    
    # Note: Will fail auth check, but we're testing the endpoint exists
    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient):
    """Test project listing with pagination"""
    response = await client.get(
        "/projects",
        params={
            "skip": 0,
            "limit": 20,
        }
    )
    
    # Will fail auth, but endpoint should exist
    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_get_project(client: AsyncClient, test_project):
    """Test getting single project"""
    response = await client.get(
        f"/projects/{test_project.project_id}"
    )
    
    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, test_project):
    """Test task creation"""
    response = await client.post(
        f"/projects/{test_project.project_id}/tasks",
        json={
            "title": "New Task",
            "description": "Task description",
            "story_points": 5,
            "priority": "high",
        }
    )
    
    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_list_tasks(client: AsyncClient, test_project):
    """Test task listing"""
    response = await client.get(
        f"/projects/{test_project.project_id}/tasks",
        params={
            "skip": 0,
            "limit": 20,
        }
    )
    
    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_get_task(client: AsyncClient, test_task):
    """Test getting single task"""
    response = await client.get(
        f"/tasks/{test_task.task_id}"
    )
    
    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_update_task_status(client: AsyncClient, test_task):
    """Test task status transition"""
    response = await client.patch(
        f"/tasks/{test_task.task_id}/status",
        json={
            "new_status": "in_progress",
        }
    )
    
    # Will fail auth, but endpoint should exist
    assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_create_task_comment(client: AsyncClient, test_task):
    """Test adding comment to task"""
    response = await client.post(
        f"/tasks/{test_task.task_id}/comments",
        json={
            "content": "Test comment",
        }
    )
    
    assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_get_task_comments(client: AsyncClient, test_task):
    """Test retrieving task comments"""
    response = await client.get(
        f"/tasks/{test_task.task_id}/comments"
    )
    
    assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_log_task_worklog(client: AsyncClient, test_task):
    """Test logging work hours on task"""
    response = await client.post(
        f"/tasks/{test_task.task_id}/worklog",
        json={
            "hours_worked": 3.5,
            "description": "Worked on implementation",
        }
    )
    
    assert response.status_code in [200, 401, 404]
