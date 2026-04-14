from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class AuditEvent:
    request_id: str
    actor_id: str
    action: str
    resource_type: str
    resource_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


class AuditWriter(Protocol):
    def record(self, event: AuditEvent) -> None: ...


class NullAuditWriter:
    def record(self, event: AuditEvent) -> None:
        return None
