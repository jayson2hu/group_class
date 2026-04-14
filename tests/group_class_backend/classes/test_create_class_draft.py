from datetime import datetime, timezone

from apps.group_class_backend.audit.interface import NullAuditWriter
from apps.group_class_backend.classes.controller import create_class_draft
from apps.group_class_backend.classes.repository import InMemoryClassRepository
from apps.group_class_backend.common.error_codes import ErrorCode
from apps.group_class_backend.models.class_template import ClassTemplate


class _StaticTemplateRepository:
    def __init__(self, *templates: ClassTemplate) -> None:
        self._templates = {template.template_id: template for template in templates}

    def get(self, template_id: str) -> ClassTemplate | None:
        return self._templates.get(template_id)


def test_create_class_draft_returns_standard_success_response() -> None:
    repository = InMemoryClassRepository()

    response = create_class_draft(
        payload={
            "className": "周末拼课",
            "priceAmount": 299,
            "minStudents": 6,
        },
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-create-001",
        actor_id="admin-001",
        now=datetime(2026, 4, 12, 12, 0, tzinfo=timezone.utc),
    )

    assert response["requestId"] == "req-create-001"
    assert response["code"] == ErrorCode.OK
    assert response["data"]["classId"].startswith("cls-")
    assert response["data"]["version"] == 1
    assert response["data"]["status"] == "DRAFT"
    assert response["data"]["actions"] == ["view", "edit", "submit_review"]
    assert response["data"]["className"] == "周末拼课"
    assert response["data"]["minStudents"] == 6


def test_create_class_draft_prefills_defaults_from_active_template() -> None:
    repository = InMemoryClassRepository()
    template_repository = _StaticTemplateRepository(
        ClassTemplate(
            template_id="tpl-001",
            template_name="瑜伽晚课模板",
            class_type="YOGA",
            default_price_amount=399,
            default_deposit_amount=99,
            default_min_students=6,
            default_max_students=12,
            default_course_subtitle="零基础友好",
            default_target_audience="成人初学者",
            default_unsuitable_audience="近期运动损伤学员",
            default_course_goal="完成基础体式入门",
            default_schedule_summary="每周三晚 19:30",
            default_session_count=8,
            default_group_rule="满 6 人开班",
            default_absence_rule="可请假 1 次",
            default_waitlist_rule="满班后开放候补",
            default_failure_rule="未成班原路退款",
            default_faq_summary="提供瑜伽垫",
        )
    )

    response = create_class_draft(
        payload={"templateId": "tpl-001"},
        repository=repository,
        template_repository=template_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-create-template-001",
        actor_id="admin-001",
        now=datetime(2026, 4, 12, 12, 0, tzinfo=timezone.utc),
    )

    assert response["code"] == ErrorCode.OK
    assert response["data"]["templateId"] == "tpl-001"
    assert response["data"]["className"] == "瑜伽晚课模板"
    assert response["data"]["classType"] == "YOGA"
    assert response["data"]["priceAmount"] == 399
    assert response["data"]["depositAmount"] == 99
    assert response["data"]["minStudents"] == 6
    assert response["data"]["maxStudents"] == 12
    assert response["data"]["courseSubtitle"] == "零基础友好"
    assert response["data"]["targetAudience"] == "成人初学者"
    assert response["data"]["unsuitableAudience"] == "近期运动损伤学员"
    assert response["data"]["courseGoal"] == "完成基础体式入门"
    assert response["data"]["scheduleSummary"] == "每周三晚 19:30"
    assert response["data"]["sessionCount"] == 8
    assert response["data"]["groupRule"] == "满 6 人开班"
    assert response["data"]["absenceRule"] == "可请假 1 次"
    assert response["data"]["waitlistRule"] == "满班后开放候补"
    assert response["data"]["failureRule"] == "未成班原路退款"
    assert response["data"]["faqSummary"] == "提供瑜伽垫"


def test_create_class_draft_prefers_explicit_payload_over_template_defaults() -> None:
    repository = InMemoryClassRepository()
    template_repository = _StaticTemplateRepository(
        ClassTemplate(
            template_id="tpl-002",
            template_name="通用模板",
            class_type="YOGA",
            default_price_amount=399,
            default_min_students=6,
            default_course_subtitle="模板副标题",
            default_session_count=10,
        )
    )

    response = create_class_draft(
        payload={
            "templateId": "tpl-002",
            "className": "自定义课程名",
            "priceAmount": 499,
            "courseSubtitle": "自定义副标题",
            "sessionCount": 12,
        },
        repository=repository,
        template_repository=template_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-create-template-override-001",
        actor_id="admin-001",
        now=datetime(2026, 4, 12, 12, 0, tzinfo=timezone.utc),
    )

    assert response["code"] == ErrorCode.OK
    assert response["data"]["className"] == "自定义课程名"
    assert response["data"]["priceAmount"] == 499
    assert response["data"]["courseSubtitle"] == "自定义副标题"
    assert response["data"]["sessionCount"] == 12
    assert response["data"]["classType"] == "YOGA"
    assert response["data"]["minStudents"] == 6


def test_create_class_draft_backfills_null_or_blank_template_fields() -> None:
    repository = InMemoryClassRepository()
    template_repository = _StaticTemplateRepository(
        ClassTemplate(
            template_id="tpl-003",
            template_name="少儿口才模板",
            class_type="SPEECH",
            default_price_amount=599,
            default_min_students=5,
            default_course_subtitle="表达启蒙",
            default_session_count=6,
        )
    )

    response = create_class_draft(
        payload={
            "templateId": "tpl-003",
            "className": "",
            "priceAmount": None,
            "courseSubtitle": "",
            "sessionCount": None,
        },
        repository=repository,
        template_repository=template_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-create-template-backfill-001",
        actor_id="admin-001",
        now=datetime(2026, 4, 12, 12, 0, tzinfo=timezone.utc),
    )

    assert response["code"] == ErrorCode.OK
    assert response["data"]["className"] == "少儿口才模板"
    assert response["data"]["classType"] == "SPEECH"
    assert response["data"]["priceAmount"] == 599
    assert response["data"]["minStudents"] == 5
    assert response["data"]["courseSubtitle"] == "表达启蒙"
    assert response["data"]["sessionCount"] == 6


def test_create_class_draft_copies_fields_from_source_class_and_resets_new_draft_state() -> None:
    repository = InMemoryClassRepository()
    source_response = create_class_draft(
        payload={
            "className": "原始周末拼课",
            "templateId": "tpl-source-001",
            "classType": "ENGLISH",
            "priceAmount": 499,
            "depositAmount": 99,
            "minStudents": 6,
            "maxStudents": 12,
            "courseSubtitle": "原课程副标题",
            "targetAudience": "三年级学员",
            "unsuitableAudience": "已学完全部自然拼读",
            "courseGoal": "建立阅读习惯",
            "scheduleSummary": "每周六上午",
            "sessionCount": 10,
            "groupRule": "满 6 人开班",
            "absenceRule": "提前 24 小时请假",
            "waitlistRule": "按顺序候补",
            "failureRule": "不成班退款",
            "faqSummary": "含课后练习",
        },
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-create-source-001",
        actor_id="initiator-source",
        now=datetime(2026, 4, 12, 10, 0, tzinfo=timezone.utc),
    )
    source_class = repository.get(source_response["data"]["classId"])
    assert source_class is not None
    source_class.current_students = 8
    source_class.waitlist_count = 3
    source_class.reviewer_id = "admin-reviewer"
    repository.save(source_class)

    response = create_class_draft(
        payload={"sourceClassId": source_class.class_id},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-copy-create-001",
        actor_id="initiator-copy",
        now=datetime(2026, 4, 12, 12, 0, tzinfo=timezone.utc),
    )

    assert response["code"] == ErrorCode.OK
    assert response["data"]["classId"] != source_class.class_id
    assert response["data"]["creatorId"] == "initiator-copy"
    assert response["data"]["reviewerId"] is None
    assert response["data"]["status"] == "DRAFT"
    assert response["data"]["version"] == 1
    assert response["data"]["currentStudents"] == 0
    assert response["data"]["waitlistCount"] == 0
    assert response["data"]["className"] == "原始周末拼课"
    assert response["data"]["templateId"] == "tpl-source-001"
    assert response["data"]["classType"] == "ENGLISH"
    assert response["data"]["priceAmount"] == 499
    assert response["data"]["depositAmount"] == 99
    assert response["data"]["minStudents"] == 6
    assert response["data"]["maxStudents"] == 12
    assert response["data"]["courseSubtitle"] == "原课程副标题"
    assert response["data"]["targetAudience"] == "三年级学员"
    assert response["data"]["unsuitableAudience"] == "已学完全部自然拼读"
    assert response["data"]["courseGoal"] == "建立阅读习惯"
    assert response["data"]["scheduleSummary"] == "每周六上午"
    assert response["data"]["sessionCount"] == 10
    assert response["data"]["groupRule"] == "满 6 人开班"
    assert response["data"]["absenceRule"] == "提前 24 小时请假"
    assert response["data"]["waitlistRule"] == "按顺序候补"
    assert response["data"]["failureRule"] == "不成班退款"
    assert response["data"]["faqSummary"] == "含课后练习"


def test_create_class_draft_prefers_explicit_payload_over_source_class_fields() -> None:
    repository = InMemoryClassRepository()
    source_response = create_class_draft(
        payload={
            "className": "原课",
            "templateId": "tpl-source-002",
            "classType": "ENGLISH",
            "priceAmount": 399,
            "minStudents": 6,
            "courseSubtitle": "原副标题",
            "sessionCount": 8,
        },
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-create-source-override-001",
        actor_id="initiator-source",
        now=datetime(2026, 4, 12, 10, 0, tzinfo=timezone.utc),
    )

    response = create_class_draft(
        payload={
            "sourceClassId": source_response["data"]["classId"],
            "className": "复制后的新课",
            "priceAmount": 599,
            "courseSubtitle": "复制后副标题",
            "sessionCount": 12,
        },
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-copy-create-override-001",
        actor_id="initiator-copy",
        now=datetime(2026, 4, 12, 12, 0, tzinfo=timezone.utc),
    )

    assert response["code"] == ErrorCode.OK
    assert response["data"]["className"] == "复制后的新课"
    assert response["data"]["priceAmount"] == 599
    assert response["data"]["courseSubtitle"] == "复制后副标题"
    assert response["data"]["sessionCount"] == 12
    assert response["data"]["templateId"] == "tpl-source-002"
    assert response["data"]["classType"] == "ENGLISH"
    assert response["data"]["minStudents"] == 6


def test_create_class_draft_returns_not_found_when_source_class_does_not_exist() -> None:
    repository = InMemoryClassRepository()

    response = create_class_draft(
        payload={"sourceClassId": "cls-missing-001"},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-copy-create-missing-001",
        actor_id="admin-001",
        now=datetime(2026, 4, 12, 12, 0, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-copy-create-missing-001",
        "code": ErrorCode.CLASS_NOT_FOUND,
        "details": [{"field": "sourceClassId", "message": "source class not found"}],
    }


def test_create_class_draft_with_sqlite_repository_copies_source_class_fields() -> None:
    import sqlite3

    from apps.group_class_backend.classes.repository import SQLiteClassRepository
    from apps.group_class_backend.persistence.schema import apply_schema

    connection = sqlite3.connect(":memory:")
    apply_schema(connection)
    repository = SQLiteClassRepository(connection)
    source_response = create_class_draft(
        payload={
            "className": "SQLite 原课",
            "templateId": "tpl-sqlite-001",
            "classType": "YOGA",
            "priceAmount": 299,
            "minStudents": 5,
            "maxStudents": 10,
            "courseSubtitle": "SQLite 副标题",
        },
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-copy-sqlite-source-001",
        actor_id="initiator-source",
        now=datetime(2026, 4, 12, 9, 0, tzinfo=timezone.utc),
    )

    response = create_class_draft(
        payload={"sourceClassId": source_response["data"]["classId"]},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-copy-sqlite-001",
        actor_id="initiator-copy",
        now=datetime(2026, 4, 12, 13, 0, tzinfo=timezone.utc),
    )
    persisted = repository.get(response["data"]["classId"])

    assert response["code"] == ErrorCode.OK
    assert persisted is not None
    assert persisted.class_id != source_response["data"]["classId"]
    assert persisted.creator_id == "initiator-copy"
    assert persisted.reviewer_id is None
    assert persisted.status.value == "DRAFT"
    assert persisted.current_students == 0
    assert persisted.waitlist_count == 0
    assert persisted.class_name == "SQLite 原课"
    assert persisted.template_id == "tpl-sqlite-001"
    assert persisted.class_type == "YOGA"
    assert persisted.price_amount == 299
    assert persisted.min_students == 5
    assert persisted.max_students == 10
    assert persisted.course_subtitle == "SQLite 副标题"


def test_create_class_draft_returns_validation_error_with_details() -> None:
    repository = InMemoryClassRepository()

    response = create_class_draft(
        payload={
            "priceAmount": 299,
            "depositAmount": 399,
        },
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-create-err-001",
        actor_id="admin-001",
        now=datetime(2026, 4, 12, 12, 0, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-create-err-001",
        "code": ErrorCode.VALIDATION_INVALID_ARGUMENT,
        "details": [
            {
                "field": "className",
                "message": "className or templateId is required",
            }
        ],
    }
