from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from apps.group_class_backend.classes.repository import InMemoryClassRepository, SQLiteClassRepository
from apps.group_class_backend.models.group_class import GroupClass
from apps.group_class_backend.persistence.schema import apply_schema
from apps.group_class_backend.server import AppState


def test_app_state_defaults_to_in_memory_repository() -> None:
    state = AppState()

    assert state.storage == "memory"
    assert isinstance(state.class_repository, InMemoryClassRepository)
    assert len(state.class_repository.list()) == 3


def test_apply_schema_can_run_more_than_once() -> None:
    connection = sqlite3.connect(":memory:")

    apply_schema(connection)
    apply_schema(connection)

    class_count = connection.execute("SELECT COUNT(*) FROM classes").fetchone()[0]
    assert class_count == 0


def test_app_state_sqlite_runtime_persists_classes_between_instances() -> None:
    runtime_dir = Path(".runtime")
    runtime_dir.mkdir(exist_ok=True)
    db_path = runtime_dir / f"test_server_runtime_{uuid4().hex}.sqlite3"
    first_state = None
    second_state = None
    try:
        first_state = AppState(storage="sqlite", sqlite_path=str(db_path))
        assert isinstance(first_state.class_repository, SQLiteClassRepository)

        created = GroupClass.create_draft(
            created_at=datetime.now(timezone.utc),
            creator_id="u_test",
            class_name="持久化验证课程",
            class_type="GROUP_CLASS",
            min_students=2,
            max_students=6,
        )
        first_state.class_repository.save(created)
        first_state.sqlite_connection.close()

        second_state = AppState(storage="sqlite", sqlite_path=str(db_path))
        persisted = second_state.class_repository.get(created.class_id)

        assert persisted is not None
        assert persisted.class_name == "持久化验证课程"
        assert len(second_state.class_repository.list()) == 4
    finally:
        if first_state and first_state.sqlite_connection:
            first_state.sqlite_connection.close()
        if second_state and second_state.sqlite_connection:
            second_state.sqlite_connection.close()
        for suffix in ("", "-wal", "-shm"):
            path = Path(f"{db_path}{suffix}")
            if path.exists():
                path.unlink()
