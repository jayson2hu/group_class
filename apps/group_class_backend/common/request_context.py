from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class RequestContext:
    request_id: str


def build_request_context(request_id: str | None = None) -> RequestContext:
    return RequestContext(request_id=request_id or f"req-{uuid4().hex[:12]}")
