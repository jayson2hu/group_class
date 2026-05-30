from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from apps.group_class_backend.common.error_codes import ErrorCode
from apps.group_class_backend.persistence.schema import apply_schema
from apps.group_class_backend.templates.controller import create_template, get_template, list_templates, update_template
from apps.group_class_backend.templates.repository import InMemoryTemplateRepository, SQLiteTemplateRepository


def test_create_template_requires_admin_role() -> None:
    repository = InMemoryTemplateRepository()

    response = create_template(
        payload={"templateName": "周末英语模板"},
        repository=repository,
        request_id="req-template-permission-001",
        actor_roles=["INITIATOR"],
        now=datetime(2026, 4, 28, tzinfo=timezone.utc),
    )

    assert response["code"] == ErrorCode.PERMISSION_DENIED
    assert repository.list() == []


def test_create_template_persists_core_fields() -> None:
    repository = InMemoryTemplateRepository()

    response = create_template(
        payload={
            "templateName": "周末英语模板",
            "classType": "GROUP_CLASS",
            "defaultPriceAmount": 1999,
            "defaultMinStudents": 4,
            "defaultMaxStudents": 8,
            "defaultScheduleSummary": "每周六 10:00-11:30",
        },
        repository=repository,
        request_id="req-template-create-001",
        actor_roles=["CLASS_ADMIN"],
        now=datetime(2026, 4, 28, 9, 0, tzinfo=timezone.utc),
    )

    data = response["data"]
    assert response["code"] == ErrorCode.OK
    assert data["templateId"].startswith("tpl-")
    assert data["templateName"] == "周末英语模板"
    assert data["defaultPriceAmount"] == 1999
    assert repository.get(data["templateId"]) is not None


def test_create_template_validates_student_bounds() -> None:
    repository = InMemoryTemplateRepository()

    response = create_template(
        payload={"templateName": "人数错误模板", "defaultMinStudents": 8, "defaultMaxStudents": 4},
        repository=repository,
        request_id="req-template-bounds-001",
        actor_roles=["CLASS_ADMIN"],
        now=datetime(2026, 4, 28, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-template-bounds-001",
        "code": ErrorCode.VALIDATION_INVALID_ARGUMENT,
        "details": [
            {
                "field": "defaultMaxStudents",
                "message": "defaultMaxStudents must be greater than or equal to defaultMinStudents",
            }
        ],
    }


def test_update_and_get_template() -> None:
    repository = InMemoryTemplateRepository()
    created = create_template(
        payload={"templateName": "旧模板", "isActive": True},
        repository=repository,
        request_id="req-template-seed-001",
        actor_roles=["CLASS_ADMIN"],
        now=datetime(2026, 4, 28, 9, 0, tzinfo=timezone.utc),
    )["data"]

    response = update_template(
        template_id=created["templateId"],
        payload={"templateName": "新模板", "isActive": False},
        repository=repository,
        request_id="req-template-update-001",
        actor_roles=["SUPER_ADMIN"],
        now=datetime(2026, 4, 28, 10, 0, tzinfo=timezone.utc),
    )
    detail = get_template(
        template_id=created["templateId"],
        repository=repository,
        request_id="req-template-get-001",
        actor_roles=["CLASS_ADMIN"],
    )

    assert response["code"] == ErrorCode.OK
    assert response["data"]["templateName"] == "新模板"
    assert detail["data"]["isActive"] is False


def test_list_templates_orders_newest_first() -> None:
    repository = InMemoryTemplateRepository()
    first = create_template(
        payload={"templateName": "旧模板"},
        repository=repository,
        request_id="req-template-list-001",
        actor_roles=["CLASS_ADMIN"],
        now=datetime(2026, 4, 28, 9, 0, tzinfo=timezone.utc),
    )["data"]
    second = create_template(
        payload={"templateName": "新模板"},
        repository=repository,
        request_id="req-template-list-002",
        actor_roles=["CLASS_ADMIN"],
        now=datetime(2026, 4, 28, 10, 0, tzinfo=timezone.utc),
    )["data"]

    response = list_templates(
        repository=repository,
        request_id="req-template-list-003",
        actor_roles=["CLASS_ADMIN"],
    )

    assert [item["templateId"] for item in response["data"]["items"]] == [second["templateId"], first["templateId"]]


def test_sqlite_template_repository_roundtrip() -> None:
    connection = sqlite3.connect(":memory:")
    apply_schema(connection)
    repository = SQLiteTemplateRepository(connection)

    created = create_template(
        payload={
            "templateName": "SQLite 模板",
            "classType": "GROUP_CLASS",
            "defaultPriceAmount": 2999,
            "defaultDepositAmount": 499,
            "defaultMinStudents": 5,
            "defaultMaxStudents": 10,
            "defaultCourseGoal": "提升阅读",
        },
        repository=repository,
        request_id="req-template-sqlite-001",
        actor_roles=["CLASS_ADMIN"],
        now=datetime(2026, 4, 28, 9, 0, tzinfo=timezone.utc),
    )["data"]

    persisted = repository.get(created["templateId"])

    assert persisted is not None
    assert persisted.template_name == "SQLite 模板"
    assert persisted.default_deposit_amount == 499
    assert persisted.default_course_goal == "提升阅读"
