"""
Shared API response envelope helpers.
"""
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict


class ApiResponse(BaseModel):
    """Standard API response envelope."""

    model_config = ConfigDict(from_attributes=True)

    status: str
    message: str
    data: Any = None


def build_response_envelope(status: str, message: str, data: Any = None) -> Dict[str, Any]:
    return {"status": status, "message": message, "data": data}


def success_response(data: Any = None, message: str = "success") -> Dict[str, Any]:
    return build_response_envelope("success", message, data)


def error_response(message: str, data: Any = None) -> Dict[str, Any]:
    return build_response_envelope("error", message, data)


def is_enveloped_payload(payload: Any) -> bool:
    return (
        isinstance(payload, dict)
        and {"status", "message", "data"}.issubset(payload.keys())
        and payload.get("status") in {"success", "error"}
    )


def extract_error_message(detail: Any) -> str:
    if isinstance(detail, str):
        return detail
    return "Request failed"