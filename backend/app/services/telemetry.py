"""
AI assistant telemetry and metrics collection.
"""
import time
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


@dataclass
class AIMetricsSnapshot:
    """Current state of AI metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency_ms: float = 0.0
    avg_latency_ms: float = 0.0
    min_latency_ms: float = float("inf")
    max_latency_ms: float = 0.0
    error_counts: Dict[str, int] = field(default_factory=dict)
    workflow_counts: Dict[str, int] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AITelemetryCollector:
    """Collect and aggregate AI assistant metrics."""

    def __init__(self):
        self._total_requests = 0
        self._successful_requests = 0
        self._failed_requests = 0
        self._total_latency_ms = 0.0
        self._min_latency_ms = float("inf")
        self._max_latency_ms = 0.0
        self._error_counts: Dict[str, int] = {}
        self._workflow_counts: Dict[str, int] = {}

    def record_request(
        self,
        workflow: str,
        latency_ms: float,
        success: bool,
        error_type: Optional[str] = None,
    ) -> None:
        """Record a workflow execution metric."""
        self._total_requests += 1
        self._total_latency_ms += latency_ms

        # Update latency bounds
        if latency_ms < self._min_latency_ms:
            self._min_latency_ms = latency_ms
        if latency_ms > self._max_latency_ms:
            self._max_latency_ms = latency_ms

        # Update success/failure counts
        if success:
            self._successful_requests += 1
        else:
            self._failed_requests += 1

        # Update workflow counts
        self._workflow_counts[workflow] = self._workflow_counts.get(workflow, 0) + 1

        # Update error counts
        if error_type and not success:
            self._error_counts[error_type] = self._error_counts.get(error_type, 0) + 1

        logger.debug(
            "AI telemetry recorded: workflow=%s latency_ms=%.2f success=%s error_type=%s",
            workflow,
            latency_ms,
            success,
            error_type,
        )

    def get_snapshot(self) -> AIMetricsSnapshot:
        """Get current metrics snapshot."""
        avg_latency = (
            self._total_latency_ms / self._total_requests if self._total_requests > 0 else 0.0
        )

        return AIMetricsSnapshot(
            total_requests=self._total_requests,
            successful_requests=self._successful_requests,
            failed_requests=self._failed_requests,
            total_latency_ms=self._total_latency_ms,
            avg_latency_ms=avg_latency,
            min_latency_ms=self._min_latency_ms if self._min_latency_ms != float("inf") else 0.0,
            max_latency_ms=self._max_latency_ms,
            error_counts=self._error_counts.copy(),
            workflow_counts=self._workflow_counts.copy(),
            last_updated=datetime.now(timezone.utc),
        )

    def reset(self) -> None:
        """Reset all metrics."""
        self._total_requests = 0
        self._successful_requests = 0
        self._failed_requests = 0
        self._total_latency_ms = 0.0
        self._min_latency_ms = float("inf")
        self._max_latency_ms = 0.0
        self._error_counts.clear()
        self._workflow_counts.clear()


# Global telemetry collector instance
_collector = AITelemetryCollector()


def record_workflow_latency(
    workflow: str,
    latency_ms: float,
    success: bool,
    error_type: Optional[str] = None,
) -> None:
    """Record workflow execution metrics."""
    _collector.record_request(workflow, latency_ms, success, error_type)


def get_ai_metrics() -> AIMetricsSnapshot:
    """Get current AI metrics snapshot."""
    return _collector.get_snapshot()


def reset_ai_metrics() -> None:
    """Reset all AI metrics."""
    _collector.reset()


class LatencyTimer:
    """Context manager for measuring latency."""

    def __init__(self):
        self.start_time: Optional[float] = None
        self.elapsed_ms: float = 0.0

    def __enter__(self):
        self.start_time = time.monotonic()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            self.elapsed_ms = (time.monotonic() - self.start_time) * 1000

    async def __aenter__(self):
        self.start_time = time.monotonic()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            self.elapsed_ms = (time.monotonic() - self.start_time) * 1000
