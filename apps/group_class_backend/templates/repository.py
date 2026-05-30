from __future__ import annotations

import sqlite3
from dataclasses import replace
from datetime import datetime

from apps.group_class_backend.models.class_template import ClassTemplate


class InMemoryTemplateRepository:
    def __init__(self) -> None:
        self._items: dict[str, ClassTemplate] = {}

    def save(self, template: ClassTemplate) -> ClassTemplate:
        self._items[template.template_id] = template
        return template

    def get(self, template_id: str) -> ClassTemplate | None:
        return self._items.get(template_id)

    def list(self) -> list[ClassTemplate]:
        return list(self._items.values())

    def update(self, template: ClassTemplate) -> ClassTemplate:
        if template.template_id not in self._items:
            raise KeyError(template.template_id)
        self._items[template.template_id] = template
        return template


class SQLiteTemplateRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.row_factory = sqlite3.Row

    def save(self, template: ClassTemplate) -> ClassTemplate:
        self._connection.execute(
            """
            INSERT INTO class_templates (
                template_id, template_name, class_type, default_price_amount, default_deposit_amount,
                default_min_students, default_max_students, default_course_subtitle, default_target_audience,
                default_unsuitable_audience, default_course_goal, default_schedule_summary, default_session_count,
                default_group_rule, default_absence_rule, default_waitlist_rule, default_failure_rule,
                default_faq_summary, is_active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            self._to_row(template),
        )
        self._connection.commit()
        return template

    def get(self, template_id: str) -> ClassTemplate | None:
        row = self._connection.execute("SELECT * FROM class_templates WHERE template_id = ?", (template_id,)).fetchone()
        if row is None:
            return None
        return self._from_row(row)

    def list(self) -> list[ClassTemplate]:
        rows = self._connection.execute("SELECT * FROM class_templates ORDER BY updated_at DESC").fetchall()
        return [self._from_row(row) for row in rows]

    def update(self, template: ClassTemplate) -> ClassTemplate:
        current = self.get(template.template_id)
        if current is None:
            raise KeyError(template.template_id)
        updated = replace(template, created_at=current.created_at)
        self._connection.execute(
            """
            UPDATE class_templates
            SET template_name = ?, class_type = ?, default_price_amount = ?, default_deposit_amount = ?,
                default_min_students = ?, default_max_students = ?, default_course_subtitle = ?,
                default_target_audience = ?, default_unsuitable_audience = ?, default_course_goal = ?,
                default_schedule_summary = ?, default_session_count = ?, default_group_rule = ?,
                default_absence_rule = ?, default_waitlist_rule = ?, default_failure_rule = ?,
                default_faq_summary = ?, is_active = ?, updated_at = ?
            WHERE template_id = ?
            """,
            (
                updated.template_name,
                updated.class_type,
                updated.default_price_amount,
                updated.default_deposit_amount,
                updated.default_min_students,
                updated.default_max_students,
                updated.default_course_subtitle,
                updated.default_target_audience,
                updated.default_unsuitable_audience,
                updated.default_course_goal,
                updated.default_schedule_summary,
                updated.default_session_count,
                updated.default_group_rule,
                updated.default_absence_rule,
                updated.default_waitlist_rule,
                updated.default_failure_rule,
                updated.default_faq_summary,
                1 if updated.is_active else 0,
                self._serialize_datetime(updated.updated_at),
                updated.template_id,
            ),
        )
        self._connection.commit()
        return updated

    def _to_row(self, template: ClassTemplate) -> tuple[object, ...]:
        return (
            template.template_id,
            template.template_name,
            template.class_type,
            template.default_price_amount,
            template.default_deposit_amount,
            template.default_min_students,
            template.default_max_students,
            template.default_course_subtitle,
            template.default_target_audience,
            template.default_unsuitable_audience,
            template.default_course_goal,
            template.default_schedule_summary,
            template.default_session_count,
            template.default_group_rule,
            template.default_absence_rule,
            template.default_waitlist_rule,
            template.default_failure_rule,
            template.default_faq_summary,
            1 if template.is_active else 0,
            self._serialize_datetime(template.created_at),
            self._serialize_datetime(template.updated_at),
        )

    def _from_row(self, row: sqlite3.Row) -> ClassTemplate:
        return ClassTemplate(
            template_id=row["template_id"],
            template_name=row["template_name"],
            class_type=row["class_type"],
            default_price_amount=row["default_price_amount"],
            default_deposit_amount=row["default_deposit_amount"],
            default_min_students=row["default_min_students"],
            default_max_students=row["default_max_students"],
            default_course_subtitle=row["default_course_subtitle"],
            default_target_audience=row["default_target_audience"],
            default_unsuitable_audience=row["default_unsuitable_audience"],
            default_course_goal=row["default_course_goal"],
            default_schedule_summary=row["default_schedule_summary"],
            default_session_count=row["default_session_count"],
            default_group_rule=row["default_group_rule"],
            default_absence_rule=row["default_absence_rule"],
            default_waitlist_rule=row["default_waitlist_rule"],
            default_failure_rule=row["default_failure_rule"],
            default_faq_summary=row["default_faq_summary"],
            is_active=bool(row["is_active"]),
            created_at=self._parse_datetime(row["created_at"]),
            updated_at=self._parse_datetime(row["updated_at"]),
        )

    @staticmethod
    def _serialize_datetime(value: datetime | None) -> str | None:
        return value.isoformat() if value else None

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        return datetime.fromisoformat(value) if value else None
