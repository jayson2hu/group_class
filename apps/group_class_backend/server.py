from __future__ import annotations

import sqlite3

from apps.group_class_backend.app import app
from apps.group_class_backend.audit.interface import InMemoryAuditLog
from apps.group_class_backend.classes.repository import InMemoryClassRepository, SQLiteClassRepository
from apps.group_class_backend.persistence.schema import apply_schema
from apps.group_class_backend.registrations.repository import InMemoryRegistrationRepository, SQLiteRegistrationRepository
from apps.group_class_backend.templates.repository import InMemoryTemplateRepository
from apps.group_class_backend.app import _seed_classes


class AppState:
    def __init__(self, storage: str = "memory", sqlite_path: str | None = None) -> None:
        self.storage = storage
        self.sqlite_connection: sqlite3.Connection | None = None
        self.template_repository = InMemoryTemplateRepository()
        self.audit_writer = InMemoryAuditLog()

        if storage == "sqlite":
            self.sqlite_connection = sqlite3.connect(sqlite_path or ".runtime/group_class.sqlite3")
            try:
                apply_schema(self.sqlite_connection)
                self.class_repository = SQLiteClassRepository(self.sqlite_connection)
                self.registration_repository = SQLiteRegistrationRepository(self.sqlite_connection)
                if not self.class_repository.list():
                    _seed_classes(self.class_repository)
            except Exception:
                self.sqlite_connection.close()
                raise
            return

        self.class_repository = InMemoryClassRepository()
        self.registration_repository = InMemoryRegistrationRepository()
        _seed_classes(self.class_repository)


__all__ = ["AppState", "app"]
