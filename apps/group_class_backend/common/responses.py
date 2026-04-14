from __future__ import annotations

from typing import Any

from apps.group_class_backend.common.error_codes import ErrorCode


def success_response(*, request_id: str, data: Any) -> dict[str, Any]:
    return {
        "requestId": request_id,
        "code": ErrorCode.OK.value,
        "data": data,
    }


def error_response(*, request_id: str, code: ErrorCode, details: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "requestId": request_id,
        "code": code.value,
        "details": details,
    }
