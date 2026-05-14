from __future__ import annotations

import sqlite3
from dataclasses import replace
from datetime import datetime

from apps.group_class_backend.common.enums import ClassStatus
from apps.group_class_backend.models.group_class import GroupClass


class InMemoryClassRepository:
    def __init__(self) -> None:
        self._items: dict[str, GroupClass] = {}

    def save(self, group_class: GroupClass) -> GroupClass:
        self._items[group_class.class_id] = group_class
        return group_class

    def get(self, class_id: str) -> GroupClass | None:
        return self._items.get(class_id)

    def list(self) -> list[GroupClass]:
        return list(self._items.values())

    def update(self, group_class: GroupClass) -> GroupClass:
        current = self._items[group_class.class_id]
        updated = replace(group_class, version=current.version + 1)
        self._items[group_class.class_id] = updated
        return updated


class SQLiteClassRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.row_factory = sqlite3.Row

    def save(self, group_class: GroupClass) -> GroupClass:
        self._connection.execute(
            """
            INSERT INTO classes (
                class_id, version, creator_id, class_name, template_id, status, reviewer_id, class_type,
                price_amount, deposit_amount, min_students, max_students,
                current_students, waitlist_count, course_subtitle, target_audience, unsuitable_audience,
                opening_level, level_marker, display_color, wechat_contact, phone_contact,
                course_goal, schedule_summary, session_count, group_rule, absence_rule, waitlist_rule,
                failure_rule, faq_summary, start_date, end_date,
                signup_deadline, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            self._to_row(group_class),
        )
        self._connection.commit()
        return group_class

    def get(self, class_id: str) -> GroupClass | None:
        row = self._connection.execute(
            "SELECT * FROM classes WHERE class_id = ?",
            (class_id,),
        ).fetchone()
        if row is None:
            return None
        return self._from_row(row)

    def list(self) -> list[GroupClass]:
        rows = self._connection.execute("SELECT * FROM classes").fetchall()
        return [self._from_row(row) for row in rows]

    def update(self, group_class: GroupClass) -> GroupClass:
        current = self.get(group_class.class_id)
        if current is None:
            raise KeyError(group_class.class_id)

        updated = replace(group_class, version=current.version + 1)
        self._connection.execute(
            """
            UPDATE classes
            SET version = ?, creator_id = ?, class_name = ?, template_id = ?, status = ?, reviewer_id = ?, class_type = ?,
                price_amount = ?, deposit_amount = ?, min_students = ?, max_students = ?,
                current_students = ?, waitlist_count = ?, course_subtitle = ?, target_audience = ?, unsuitable_audience = ?,
                opening_level = ?, level_marker = ?, display_color = ?, wechat_contact = ?, phone_contact = ?,
                course_goal = ?, schedule_summary = ?, session_count = ?, group_rule = ?, absence_rule = ?, waitlist_rule = ?,
                failure_rule = ?, faq_summary = ?, start_date = ?, end_date = ?,
                signup_deadline = ?, created_at = ?, updated_at = ?
            WHERE class_id = ?
            """,
            (
                updated.version,
                updated.creator_id,
                updated.class_name,
                updated.template_id,
                updated.status.value,
                updated.reviewer_id,
                updated.class_type,
                updated.price_amount,
                updated.deposit_amount,
                updated.min_students,
                updated.max_students,
                updated.current_students,
                updated.waitlist_count,
                updated.course_subtitle,
                updated.target_audience,
                updated.unsuitable_audience,
                updated.opening_level,
                updated.level_marker,
                updated.display_color,
                updated.wechat_contact,
                updated.phone_contact,
                updated.course_goal,
                updated.schedule_summary,
                updated.session_count,
                updated.group_rule,
                updated.absence_rule,
                updated.waitlist_rule,
                updated.failure_rule,
                updated.faq_summary,
                self._serialize_datetime(updated.start_date),
                self._serialize_datetime(updated.end_date),
                self._serialize_datetime(updated.signup_deadline),
                self._serialize_datetime(updated.created_at),
                self._serialize_datetime(updated.updated_at),
                updated.class_id,
            ),
        )
        self._connection.commit()
        return updated

    def _to_row(self, group_class: GroupClass) -> tuple[object, ...]:
        return (
            group_class.class_id,
            group_class.version,
            group_class.creator_id,
            group_class.class_name,
            group_class.template_id,
            group_class.status.value,
            group_class.reviewer_id,
            group_class.class_type,
            group_class.price_amount,
            group_class.deposit_amount,
            group_class.min_students,
            group_class.max_students,
            group_class.current_students,
            group_class.waitlist_count,
            group_class.course_subtitle,
            group_class.target_audience,
            group_class.unsuitable_audience,
            group_class.opening_level,
            group_class.level_marker,
            group_class.display_color,
            group_class.wechat_contact,
            group_class.phone_contact,
            group_class.course_goal,
            group_class.schedule_summary,
            group_class.session_count,
            group_class.group_rule,
            group_class.absence_rule,
            group_class.waitlist_rule,
            group_class.failure_rule,
            group_class.faq_summary,
            self._serialize_datetime(group_class.start_date),
            self._serialize_datetime(group_class.end_date),
            self._serialize_datetime(group_class.signup_deadline),
            self._serialize_datetime(group_class.created_at),
            self._serialize_datetime(group_class.updated_at),
        )

    def _from_row(self, row: sqlite3.Row) -> GroupClass:
        return GroupClass(
            class_id=row["class_id"],
            version=row["version"],
            creator_id=row["creator_id"],
            class_name=row["class_name"],
            template_id=row["template_id"],
            status=ClassStatus(row["status"]),
            reviewer_id=row["reviewer_id"],
            class_type=row["class_type"],
            price_amount=row["price_amount"],
            deposit_amount=row["deposit_amount"],
            min_students=row["min_students"],
            max_students=row["max_students"],
            current_students=row["current_students"],
            waitlist_count=row["waitlist_count"],
            course_subtitle=row["course_subtitle"],
            opening_level=row["opening_level"],
            level_marker=row["level_marker"],
            display_color=row["display_color"],
            wechat_contact=row["wechat_contact"],
            phone_contact=row["phone_contact"],
            target_audience=row["target_audience"],
            unsuitable_audience=row["unsuitable_audience"],
            course_goal=row["course_goal"],
            schedule_summary=row["schedule_summary"],
            session_count=row["session_count"],
            group_rule=row["group_rule"],
            absence_rule=row["absence_rule"],
            waitlist_rule=row["waitlist_rule"],
            failure_rule=row["failure_rule"],
            faq_summary=row["faq_summary"],
            start_date=self._parse_datetime(row["start_date"]),
            end_date=self._parse_datetime(row["end_date"]),
            signup_deadline=self._parse_datetime(row["signup_deadline"]),
            created_at=self._parse_datetime(row["created_at"]),
            updated_at=self._parse_datetime(row["updated_at"]),
        )

    @staticmethod
    def _serialize_datetime(value: datetime | None) -> str | None:
        return value.isoformat() if value else None

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        return datetime.fromisoformat(value) if value else None
