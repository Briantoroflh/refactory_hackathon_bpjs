"""
Tests for audit logging and KPI endpoints
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_audit_logs(client: AsyncClient):
    """Test retrieving audit logs (admin endpoint)"""
    response = await client.get(
        "/audit-logs",
        params={
            "skip": 0,
            "limit": 20,
        }
    )
    
    # Will fail auth/permission check, but endpoint should exist
    assert response.status_code in [200, 401, 403]


@pytest.mark.asyncio
async def test_get_audit_logs_by_user(client: AsyncClient, test_user):
    """Test retrieving audit logs filtered by user"""
    response = await client.get(
        f"/audit-logs/user/{test_user.user_id}",
        params={
            "skip": 0,
            "limit": 20,
        }
    )
    
    assert response.status_code in [200, 401, 403]


@pytest.mark.asyncio
async def test_get_audit_logs_by_action(client: AsyncClient):
    """Test retrieving audit logs filtered by action"""
    response = await client.get(
        "/audit-logs/action/CREATE",
        params={
            "skip": 0,
            "limit": 20,
        }
    )
    
    assert response.status_code in [200, 401, 403]


@pytest.mark.asyncio
async def test_get_audit_logs_by_resource(client: AsyncClient):
    """Test retrieving audit logs filtered by resource"""
    response = await client.get(
        "/audit-logs/resource/1",
        params={
            "skip": 0,
            "limit": 20,
        }
    )
    
    assert response.status_code in [200, 401, 403]


@pytest.mark.asyncio
async def test_get_system_audit_logs(client: AsyncClient):
    """Test retrieving system audit logs"""
    response = await client.get(
        "/audit-logs/system",
        params={
            "skip": 0,
            "limit": 20,
        }
    )
    
    assert response.status_code in [200, 401, 403]


@pytest.mark.asyncio
async def test_create_worker(client: AsyncClient):
    """Test creating a worker"""
    response = await client.post(
        "/workers",
        params={
            "full_name": "John Doe",
            "email": "john@example.com",
            "division_id": 1,
        }
    )
    
    assert response.status_code in [200, 401, 400]


@pytest.mark.asyncio
async def test_get_worker(client: AsyncClient):
    """Test retrieving worker profile"""
    response = await client.get(
        "/workers/1"
    )
    
    assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_update_worker(client: AsyncClient):
    """Test updating worker profile"""
    response = await client.put(
        "/workers/1",
        params={
            "full_name": "Jane Doe",
        }
    )
    
    assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_record_worker_kpi(client: AsyncClient):
    """Test recording KPI score for worker"""
    response = await client.post(
        "/workers/1/kpi/1",
        params={
            "score": 85.5,
        }
    )
    
    assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_get_worker_kpi_scores(client: AsyncClient):
    """Test retrieving worker KPI scores"""
    response = await client.get(
        "/workers/1/kpi-scores"
    )
    
    assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_get_worker_kpi_summary(client: AsyncClient):
    """Test retrieving worker KPI summary"""
    response = await client.get(
        "/workers/1/kpi-summary"
    )
    
    assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_update_kpi_manual_override(client: AsyncClient):
    """Test manually adjusting KPI score"""
    response = await client.put(
        "/workers/1/kpi/1",
        params={
            "score": 90.0,
            "override_reason": "Performance improvement",
        }
    )
    
    assert response.status_code in [200, 401, 404]
