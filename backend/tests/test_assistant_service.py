"""Unit tests for AI assistant service."""
import pytest

from app.services import assistant
from app.config import get_settings


@pytest.mark.asyncio
async def test_run_workflow_fallback_when_disabled():
    settings = get_settings()
    orig = settings.OPENROUTER_ENABLED
    try:
        settings.OPENROUTER_ENABLED = False
        result = await assistant.run_workflow("planning", "Test prompt", {"project_id": 1})
        assert result["status"] == "completed"
        assert result["source"] == "fallback"
        assert "structured_output" in result
    finally:
        settings.OPENROUTER_ENABLED = orig
