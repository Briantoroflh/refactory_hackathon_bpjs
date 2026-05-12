"""Tests for AI assistant telemetry and health metrics."""
import pytest
from fastapi import status

from app.services.telemetry import (
    AITelemetryCollector,
    record_workflow_latency,
    get_ai_metrics,
    reset_ai_metrics,
)


def test_telemetry_collector_single_request():
    """Test recording a single successful request."""
    collector = AITelemetryCollector()
    
    collector.record_request("planning", 100.5, success=True)
    
    snapshot = collector.get_snapshot()
    assert snapshot.total_requests == 1
    assert snapshot.successful_requests == 1
    assert snapshot.failed_requests == 0
    assert snapshot.total_latency_ms == 100.5
    assert snapshot.avg_latency_ms == 100.5
    assert snapshot.workflow_counts["planning"] == 1


def test_telemetry_collector_multiple_requests():
    """Test recording multiple requests."""
    collector = AITelemetryCollector()
    
    collector.record_request("planning", 100.0, success=True)
    collector.record_request("planning", 200.0, success=True)
    collector.record_request("sprint_summary", 150.0, success=False, error_type="TimeoutError")
    
    snapshot = collector.get_snapshot()
    assert snapshot.total_requests == 3
    assert snapshot.successful_requests == 2
    assert snapshot.failed_requests == 1
    assert snapshot.avg_latency_ms == 150.0
    assert snapshot.min_latency_ms == 100.0
    assert snapshot.max_latency_ms == 200.0
    assert snapshot.workflow_counts["planning"] == 2
    assert snapshot.workflow_counts["sprint_summary"] == 1
    assert snapshot.error_counts["TimeoutError"] == 1


def test_telemetry_collector_error_tracking():
    """Test error tracking."""
    collector = AITelemetryCollector()
    
    collector.record_request("planning", 100.0, success=False, error_type="AIServiceError")
    collector.record_request("planning", 105.0, success=False, error_type="AIServiceError")
    collector.record_request("sprint_summary", 110.0, success=False, error_type="TimeoutError")
    
    snapshot = collector.get_snapshot()
    assert snapshot.error_counts["AIServiceError"] == 2
    assert snapshot.error_counts["TimeoutError"] == 1
    assert snapshot.failed_requests == 3


def test_telemetry_reset():
    """Test resetting telemetry metrics."""
    collector = AITelemetryCollector()
    
    collector.record_request("planning", 100.0, success=True)
    collector.record_request("planning", 200.0, success=False, error_type="Error")
    
    snapshot1 = collector.get_snapshot()
    assert snapshot1.total_requests == 2
    
    collector.reset()
    snapshot2 = collector.get_snapshot()
    assert snapshot2.total_requests == 0
    assert snapshot2.successful_requests == 0
    assert snapshot2.failed_requests == 0


def test_telemetry_latency_bounds():
    """Test min and max latency tracking."""
    collector = AITelemetryCollector()
    
    latencies = [50.0, 100.0, 75.0, 150.0, 25.0]
    for latency in latencies:
        collector.record_request("planning", latency, success=True)
    
    snapshot = collector.get_snapshot()
    assert snapshot.min_latency_ms == 25.0
    assert snapshot.max_latency_ms == 150.0


@pytest.mark.asyncio
async def test_health_endpoint_no_requests(client):
    """Test health endpoint when no requests have been made."""
    reset_ai_metrics()  # Clear any previous test metrics
    
    response = await client.get("/ai-assistant/health")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert data["total_requests"] == 0
    assert data["successful_requests"] == 0
    assert data["failed_requests"] == 0


@pytest.mark.asyncio
async def test_health_endpoint_with_metrics(client, test_db, test_user):
    """Test health endpoint with recorded metrics."""
    from unittest.mock import patch
    from app.models import Role, UserRole
    
    # Setup user with role
    async with test_db() as db:
        role = Role(name="admin")
        db.add(role)
        await db.commit()
        await db.refresh(role)

        user_role = UserRole(user_id=test_user.user_id, role_id=role.role_id)
        db.add(user_role)
        await db.commit()

    # First, record some metrics
    reset_ai_metrics()
    record_workflow_latency("planning", 100.0, success=True)
    record_workflow_latency("planning", 150.0, success=True)
    record_workflow_latency("sprint_summary", 200.0, success=False, error_type="TimeoutError")
    
    response = await client.get("/ai-assistant/health")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_requests"] == 3
    assert data["successful_requests"] == 2
    assert data["failed_requests"] == 1
    assert round(data["success_rate_percent"], 1) == 66.7
    assert data["latency_ms"]["avg"] == pytest.approx(150.0, abs=1)
    assert data["latency_ms"]["min"] == 100.0
    assert data["latency_ms"]["max"] == 200.0
    assert data["error_counts"]["TimeoutError"] == 1
    assert data["workflow_counts"]["planning"] == 2
    assert data["workflow_counts"]["sprint_summary"] == 1
    assert "last_updated" in data


@pytest.mark.asyncio
async def test_health_status_degraded_on_high_errors(client):
    """Test health endpoint returns degraded status on high error rate."""
    reset_ai_metrics()
    
    # Record mostly failed requests
    for i in range(10):
        record_workflow_latency("planning", 100.0 + i * 10, success=False, error_type="Error")
    record_workflow_latency("planning", 100.0, success=True)
    
    response = await client.get("/ai-assistant/health")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "degraded"
    assert data["success_rate_percent"] < 20.0
