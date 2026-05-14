from __future__ import annotations

import sqlite3
from collections.abc import Iterable


_CLASSES_DDL = """
CREATE TABLE classes (
    class_id TEXT PRIMARY KEY,
    version INTEGER NOT NULL CHECK (version >= 1),
    creator_id TEXT NOT NULL,
    class_name TEXT,
    template_id TEXT,
    status TEXT NOT NULL,
    reviewer_id TEXT,
    class_type TEXT,
    price_amount REAL,
    deposit_amount REAL,
    min_students INTEGER,
    max_students INTEGER,
    current_students INTEGER NOT NULL DEFAULT 0 CHECK (current_students >= 0),
    waitlist_count INTEGER NOT NULL DEFAULT 0 CHECK (waitlist_count >= 0),
    course_subtitle TEXT,
    opening_level TEXT,
    level_marker TEXT,
    display_color TEXT,
    wechat_contact TEXT,
    phone_contact TEXT,
    target_audience TEXT,
    unsuitable_audience TEXT,
    course_goal TEXT,
    schedule_summary TEXT,
    session_count INTEGER,
    group_rule TEXT,
    absence_rule TEXT,
    waitlist_rule TEXT,
    failure_rule TEXT,
    faq_summary TEXT,
    start_date TEXT,
    end_date TEXT,
    signup_deadline TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    CHECK (class_name IS NOT NULL OR template_id IS NOT NULL),
    CHECK (min_students IS NULL OR min_students > 0),
    CHECK (session_count IS NULL OR session_count > 0),
    CHECK (max_students IS NULL OR min_students IS NULL OR max_students >= min_students),
    CHECK (start_date IS NULL OR end_date IS NULL OR end_date >= start_date),
    CHECK (signup_deadline IS NULL OR start_date IS NULL OR signup_deadline <= start_date),
    CHECK (price_amount IS NULL OR deposit_amount IS NULL OR deposit_amount <= price_amount)
)
""".strip()

_REGISTRATIONS_DDL = """
CREATE TABLE registrations (
    registration_id TEXT PRIMARY KEY,
    class_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    registration_type TEXT NOT NULL,
    status TEXT NOT NULL,
    submitted_at TEXT NOT NULL,
    parent_name TEXT,
    contact_info TEXT,
    student_name TEXT,
    student_grade TEXT,
    english_level TEXT,
    accept_transfer INTEGER,
    accept_waitlist INTEGER,
    wants_trial INTEGER,
    accept_similar_recommendation INTEGER,
    remark TEXT,
    follow_up_note TEXT,
    notes TEXT,
    payment_status TEXT NOT NULL DEFAULT 'UNPAID',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (class_id) REFERENCES classes(class_id)
)
""".strip()

_CLASS_TEMPLATES_DDL = """
CREATE TABLE class_templates (
    template_id TEXT PRIMARY KEY,
    template_name TEXT NOT NULL,
    class_type TEXT,
    default_price_amount REAL,
    is_active INTEGER NOT NULL CHECK (is_active IN (0, 1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
""".strip()

_INDEX_DDLS = (
    "CREATE INDEX idx_classes_status_updated_at ON classes(status, updated_at DESC)",
    "CREATE INDEX idx_registrations_class_status ON registrations(class_id, status)",
    "CREATE INDEX idx_registrations_user_status ON registrations(user_id, status)",
    "CREATE UNIQUE INDEX uq_class_templates_template_name ON class_templates(template_name)",
)


def schema_statements() -> list[str]:
    return [_CLASSES_DDL, _REGISTRATIONS_DDL, _CLASS_TEMPLATES_DDL, *_INDEX_DDLS]



def apply_schema(connection: sqlite3.Connection, statements: Iterable[str] | None = None) -> None:
    connection.execute("PRAGMA foreign_keys = ON")
    for statement in statements or schema_statements():
        try:
            connection.execute(statement)
        except sqlite3.OperationalError as exc:
            if "already exists" not in str(exc).lower():
                raise
    connection.commit()
