from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class AuditEvent:
    request_id: str
    actor_id: str
    action: str
    resource_type: str
    resource_id: str
    metadata: dict[str, Any] = field(default_factory=dict)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AuditWriter(Protocol):
    def record(self, event: AuditEvent) -> None: ...


class AuditReader(Protocol):
    def list_for_resource(self, resource_type: str, resource_id: str) -> list[AuditEvent]: ...


class NullAuditWriter:
    def record(self, event: AuditEvent) -> None:
        return None

    def list_for_resource(self, resource_type: str, resource_id: str) -> list[AuditEvent]:
        return []


class InMemoryAuditLog:
    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def record(self, event: AuditEvent) -> None:
        self._events.append(event)

    def list_for_resource(self, resource_type: str, resource_id: str) -> list[AuditEvent]:
        return [
            event
            for event in self._events
            if event.resource_type == resource_type and event.resource_id == resource_id
        ]
