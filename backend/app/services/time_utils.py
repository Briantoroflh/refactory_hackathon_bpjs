"""Utilities for consistent timestamp handling."""
from datetime import datetime, timezone


def utcnow_naive() -> datetime:
    """Return a timezone-naive UTC datetime for databases that store TIMESTAMP WITHOUT TIME ZONE."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def utcnow_iso() -> str:
    """Return an ISO 8601 UTC timestamp string."""
    return datetime.now(timezone.utc).isoformat()