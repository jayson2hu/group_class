from __future__ import annotations

import sqlite3

from apps.group_class_backend.persistence.schema import apply_schema, schema_statements


def _create_db() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    apply_schema(connection)
    return connection



def test_schema_statements_cover_batch1_core_tables() -> None:
    ddl = "\n".join(schema_statements())

    assert "CREATE TABLE classes" in ddl
    assert "CREATE TABLE registrations" in ddl
    assert "CREATE TABLE class_templates" in ddl
    assert "CREATE INDEX idx_classes_status_updated_at" in ddl
    assert "CREATE INDEX idx_registrations_class_status" in ddl
    assert "CREATE UNIQUE INDEX uq_class_templates_template_name" in ddl



def test_classes_table_enforces_batch1_constraints() -> None:
    connection = _create_db()

    connection.execute(
        """
        INSERT INTO classes (
            class_id, version, creator_id, class_name, template_id, status, class_type,
            price_amount, deposit_amount, min_students, max_students,
            current_students, waitlist_count, start_date, end_date,
            signup_deadline, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "cls-001",
            1,
            "initiator-001",
            "周末拼课",
            None,
            "DRAFT",
            "YOGA",
            299,
            99,
            6,
            12,
            0,
            0,
            "2026-04-20T10:00:00+00:00",
            "2026-04-21T10:00:00+00:00",
            "2026-04-19T10:00:00+00:00",
            "2026-04-12T10:00:00+00:00",
            "2026-04-12T10:00:00+00:00",
        ),
    )

    invalid_rows = [
        (
            "cls-002",
            1,
            "initiator-001",
            "无效最小人数",
            None,
            "DRAFT",
            None,
            None,
            None,
            0,
            10,
            0,
            0,
            None,
            None,
            None,
            "2026-04-12T10:00:00+00:00",
            "2026-04-12T10:00:00+00:00",
        ),
        (
            "cls-003",
            1,
            "initiator-001",
            "无效人数区间",
            None,
            "DRAFT",
            None,
            None,
            None,
            8,
            6,
            0,
            0,
            None,
            None,
            None,
            "2026-04-12T10:00:00+00:00",
            "2026-04-12T10:00:00+00:00",
        ),
        (
            "cls-004",
            1,
            "initiator-001",
            None,
            None,
            "DRAFT",
            None,
            None,
            None,
            None,
            None,
            0,
            0,
            None,
            None,
            None,
            "2026-04-12T10:00:00+00:00",
            "2026-04-12T10:00:00+00:00",
        ),
    ]

    for row in invalid_rows:
        try:
            connection.execute(
                """
                INSERT INTO classes (
                    class_id, version, creator_id, class_name, template_id, status, class_type,
                    price_amount, deposit_amount, min_students, max_students,
                    current_students, waitlist_count, start_date, end_date,
                    signup_deadline, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                row,
            )
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError(f"expected integrity error for row {row[0]}")



def test_registration_and_template_indexes_exist() -> None:
    connection = _create_db()

    registration_indexes = {
        row[1] for row in connection.execute("PRAGMA index_list('registrations')").fetchall()
    }
    template_indexes = {
        row[1] for row in connection.execute("PRAGMA index_list('class_templates')").fetchall()
    }

    assert "idx_registrations_class_status" in registration_indexes
    assert "idx_registrations_user_status" in registration_indexes
    assert "uq_class_templates_template_name" in template_indexes



def test_registrations_table_supports_batch4_contact_fields() -> None:
    connection = _create_db()

    connection.execute(
        """
        INSERT INTO classes (
            class_id, version, creator_id, class_name, template_id, status,
            current_students, waitlist_count, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "cls-registrations-001",
            1,
            "initiator-001",
            "周末拼课",
            None,
            "OPEN_FOR_ENROLLMENT",
            0,
            0,
            "2026-04-12T10:00:00+00:00",
            "2026-04-12T10:00:00+00:00",
        ),
    )
    connection.execute(
        """
        INSERT INTO registrations (
            registration_id, class_id, user_id, registration_type, status, submitted_at,
            parent_name, contact_info, student_name, student_grade, english_level,
            accept_transfer, accept_waitlist, wants_trial, accept_similar_recommendation,
            remark, follow_up_note, notes, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "reg-001",
            "cls-registrations-001",
            "usr-001",
            "ENROLLMENT",
            "SUBMITTED",
            "2026-04-12T15:00:00+00:00",
            "张女士",
            "13800000000",
            "张三",
            "三年级",
            "基础一般",
            1,
            1,
            0,
            None,
            "希望同校同学一起",
            None,
            None,
            "2026-04-12T15:00:00+00:00",
            "2026-04-12T15:00:00+00:00",
        ),
    )

    row = connection.execute(
        "SELECT parent_name, contact_info, student_grade, accept_waitlist FROM registrations WHERE registration_id = ?",
        ("reg-001",),
    ).fetchone()

    assert row == ("张女士", "13800000000", "三年级", 1)
