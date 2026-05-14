from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from apps.group_class_backend.models.registration import PaymentStatus, Registration, RegistrationStatus, RegistrationType


class InMemoryRegistrationRepository:
    def __init__(self) -> None:
        self._items: dict[str, Registration] = {}

    def save(self, registration: Registration) -> Registration:
        self._items[registration.registration_id] = registration
        return registration

    def get(self, registration_id: str) -> Registration | None:
        return self._items.get(registration_id)

    def list(self) -> list[Registration]:
        return list(self._items.values())

    def update(self, registration: Registration) -> Registration:
        if registration.registration_id not in self._items:
            raise KeyError(registration.registration_id)
        self._items[registration.registration_id] = registration
        return registration


class SQLiteRegistrationRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.row_factory = sqlite3.Row

    def save(self, registration: Registration) -> Registration:
        self._connection.execute(
            """
            INSERT INTO registrations (
                registration_id, class_id, user_id, registration_type, status, submitted_at,
                parent_name, contact_info, student_name, student_grade, english_level,
                accept_transfer, accept_waitlist, wants_trial, accept_similar_recommendation,
                remark, follow_up_note, notes, payment_status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            self._to_row(registration),
        )
        self._connection.commit()
        return registration

    def get(self, registration_id: str) -> Registration | None:
        row = self._connection.execute(
            "SELECT * FROM registrations WHERE registration_id = ?",
            (registration_id,),
        ).fetchone()
        if row is None:
            return None
        return self._from_row(row)

    def list(self) -> list[Registration]:
        rows = self._connection.execute("SELECT * FROM registrations ORDER BY submitted_at ASC").fetchall()
        return [self._from_row(row) for row in rows]

    def update(self, registration: Registration) -> Registration:
        self._connection.execute(
            """
            UPDATE registrations
            SET class_id = ?, user_id = ?, registration_type = ?, status = ?, submitted_at = ?,
                parent_name = ?, contact_info = ?, student_name = ?, student_grade = ?, english_level = ?,
                accept_transfer = ?, accept_waitlist = ?, wants_trial = ?, accept_similar_recommendation = ?,
                remark = ?, follow_up_note = ?, notes = ?, payment_status = ?, created_at = ?, updated_at = ?
            WHERE registration_id = ?
            """,
            (
                registration.class_id,
                registration.user_id,
                registration.registration_type.value,
                registration.status.value,
                self._serialize_datetime(registration.submitted_at),
                registration.parent_name,
                registration.contact_info,
                registration.student_name,
                registration.student_grade,
                registration.english_level,
                self._serialize_bool(registration.accept_transfer),
                self._serialize_bool(registration.accept_waitlist),
                self._serialize_bool(registration.wants_trial),
                self._serialize_bool(registration.accept_similar_recommendation),
                registration.remark,
                registration.follow_up_note,
                registration.notes,
                registration.payment_status.value,
                self._serialize_datetime(registration.created_at),
                self._serialize_datetime(registration.updated_at),
                registration.registration_id,
            ),
        )
        self._connection.commit()
        return registration

    def _to_row(self, registration: Registration) -> tuple[object, ...]:
        return (
            registration.registration_id,
            registration.class_id,
            registration.user_id,
            registration.registration_type.value,
            registration.status.value,
            self._serialize_datetime(registration.submitted_at),
            registration.parent_name,
            registration.contact_info,
            registration.student_name,
            registration.student_grade,
            registration.english_level,
            self._serialize_bool(registration.accept_transfer),
            self._serialize_bool(registration.accept_waitlist),
            self._serialize_bool(registration.wants_trial),
            self._serialize_bool(registration.accept_similar_recommendation),
            registration.remark,
            registration.follow_up_note,
            registration.notes,
            registration.payment_status.value,
            self._serialize_datetime(registration.created_at),
            self._serialize_datetime(registration.updated_at),
        )

    def _from_row(self, row: sqlite3.Row) -> Registration:
        return Registration(
            registration_id=row["registration_id"],
            class_id=row["class_id"],
            user_id=row["user_id"],
            registration_type=RegistrationType(row["registration_type"]),
            status=RegistrationStatus(row["status"]),
            submitted_at=self._parse_datetime(row["submitted_at"]),
            parent_name=row["parent_name"],
            contact_info=row["contact_info"],
            student_name=row["student_name"],
            student_grade=row["student_grade"],
            english_level=row["english_level"],
            accept_transfer=self._parse_bool(row["accept_transfer"]),
            accept_waitlist=self._parse_bool(row["accept_waitlist"]),
            wants_trial=self._parse_bool(row["wants_trial"]),
            accept_similar_recommendation=self._parse_bool(row["accept_similar_recommendation"]),
            remark=row["remark"],
            follow_up_note=row["follow_up_note"],
            notes=row["notes"],
            payment_status=PaymentStatus(row["payment_status"] or PaymentStatus.UNPAID.value),
            created_at=self._parse_datetime(row["created_at"]),
            updated_at=self._parse_datetime(row["updated_at"]),
        )

    @staticmethod
    def _serialize_datetime(value: datetime | None) -> str | None:
        return value.isoformat() if value else None

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        return datetime.fromisoformat(value) if value else None

    @staticmethod
    def _serialize_bool(value: bool | None) -> int | None:
        if value is None:
            return None
        return int(value)

    @staticmethod
    def _parse_bool(value: int | None) -> bool | None:
        if value is None:
            return None
        return bool(value)
