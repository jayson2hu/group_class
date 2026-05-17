from dataclasses import replace
from datetime import datetime, timedelta, timezone
import sqlite3

from apps.group_class_backend.audit.interface import InMemoryAuditLog, NullAuditWriter
from apps.group_class_backend.classes.controller import (
    approve_class_review,
    cancel_class,
    create_class_draft,
    get_class_detail,
    list_classes,
    reject_class_review,
    submit_class_review,
    update_class_draft,
)
from apps.group_class_backend.classes.repository import InMemoryClassRepository, SQLiteClassRepository
from apps.group_class_backend.common.error_codes import ErrorCode
from apps.group_class_backend.common.enums import ClassStatus
from apps.group_class_backend.models.class_template import ClassTemplate
from apps.group_class_backend.persistence.schema import apply_schema


def _seed_template(template_id: str = "tpl-weekend-001", *, is_active: bool = True) -> ClassTemplate:
    now = datetime(2026, 4, 12, 11, 0, tzinfo=timezone.utc)
    return ClassTemplate(
        template_id=template_id,
        template_name="周末英语基础模板",
        class_type="ENGLISH",
        default_price_amount=399,
        default_deposit_amount=99,
        default_min_students=6,
        default_max_students=12,
        default_course_subtitle="适合零基础启蒙",
        default_target_audience="6-8岁学员",
        default_unsuitable_audience="已有系统语法基础学员",
        default_course_goal="建立基础听说表达能力",
        default_schedule_summary="每周六 10:00-11:30，连续 8 周",
        default_session_count=8,
        default_group_rule="满 6 人开班",
        default_absence_rule="请假需至少提前 24 小时",
        default_waitlist_rule="满班后按登记顺序候补",
        default_failure_rule="不成班自动退款",
        default_faq_summary="含教材，不含考试报名",
        is_active=is_active,
        created_at=now,
        updated_at=now,
    )


class InMemoryTemplateRepository:
    def __init__(self, templates: list[ClassTemplate] | None = None) -> None:
        self._items = {template.template_id: template for template in templates or []}

    def get(self, template_id: str) -> ClassTemplate | None:
        return self._items.get(template_id)


def _seed_class(repository: InMemoryClassRepository | SQLiteClassRepository) -> str:
    response = create_class_draft(
        payload={
            "className": "周末拼课",
            "priceAmount": 299,
            "minStudents": 6,
            "maxStudents": 12,
            "scheduleSummary": "每周六 10:00-11:30",
            "targetAudience": "三至四年级学员",
            "courseGoal": "提升阅读理解能力",
            "groupRule": "满 6 人开班",
        },
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-seed-001",
        actor_id="admin-001",
        now=datetime(2026, 4, 12, 12, 0, tzinfo=timezone.utc),
    )
    return response["data"]["classId"]



def test_create_class_draft_populates_fields_from_template_when_name_is_missing() -> None:
    repository = InMemoryClassRepository()
    template_repository = InMemoryTemplateRepository([_seed_template()])

    response = create_class_draft(
        payload={"templateId": "tpl-weekend-001"},
        repository=repository,
        template_repository=template_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-create-template-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 12, 0, tzinfo=timezone.utc),
    )

    assert response["code"] == ErrorCode.OK
    assert response["data"]["templateId"] == "tpl-weekend-001"
    assert response["data"]["className"] == "周末英语基础模板"
    assert response["data"]["classType"] == "ENGLISH"
    assert response["data"]["priceAmount"] == 399
    assert response["data"]["depositAmount"] == 99
    assert response["data"]["minStudents"] == 6
    assert response["data"]["maxStudents"] == 12
    assert response["data"]["courseSubtitle"] == "适合零基础启蒙"
    assert response["data"]["targetAudience"] == "6-8岁学员"
    assert response["data"]["unsuitableAudience"] == "已有系统语法基础学员"
    assert response["data"]["courseGoal"] == "建立基础听说表达能力"
    assert response["data"]["scheduleSummary"] == "每周六 10:00-11:30，连续 8 周"
    assert response["data"]["sessionCount"] == 8
    assert response["data"]["groupRule"] == "满 6 人开班"
    assert response["data"]["absenceRule"] == "请假需至少提前 24 小时"
    assert response["data"]["waitlistRule"] == "满班后按登记顺序候补"
    assert response["data"]["failureRule"] == "不成班自动退款"
    assert response["data"]["faqSummary"] == "含教材，不含考试报名"
    persisted = repository.get(response["data"]["classId"])
    assert persisted is not None
    assert persisted.template_id == "tpl-weekend-001"
    assert persisted.class_name == "周末英语基础模板"
    assert persisted.class_type == "ENGLISH"
    assert persisted.price_amount == 399
    assert persisted.deposit_amount == 99
    assert persisted.min_students == 6
    assert persisted.max_students == 12
    assert persisted.course_subtitle == "适合零基础启蒙"
    assert persisted.target_audience == "6-8岁学员"
    assert persisted.unsuitable_audience == "已有系统语法基础学员"
    assert persisted.course_goal == "建立基础听说表达能力"
    assert persisted.schedule_summary == "每周六 10:00-11:30，连续 8 周"
    assert persisted.session_count == 8
    assert persisted.group_rule == "满 6 人开班"
    assert persisted.absence_rule == "请假需至少提前 24 小时"
    assert persisted.waitlist_rule == "满班后按登记顺序候补"
    assert persisted.failure_rule == "不成班自动退款"
    assert persisted.faq_summary == "含教材，不含考试报名"



def test_create_class_draft_returns_not_found_when_template_does_not_exist() -> None:
    repository = InMemoryClassRepository()

    response = create_class_draft(
        payload={"templateId": "tpl-missing-001", "minStudents": 6},
        repository=repository,
        template_repository=InMemoryTemplateRepository(),
        audit_writer=NullAuditWriter(),
        request_id="req-create-template-missing-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 12, 0, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-create-template-missing-001",
        "code": ErrorCode.CLASS_NOT_FOUND,
        "details": [{"field": "templateId", "message": "template not found"}],
    }



def test_create_class_draft_rejects_inactive_template() -> None:
    repository = InMemoryClassRepository()
    template_repository = InMemoryTemplateRepository([_seed_template(is_active=False)])

    response = create_class_draft(
        payload={"templateId": "tpl-weekend-001", "minStudents": 6},
        repository=repository,
        template_repository=template_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-create-template-inactive-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 12, 5, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-create-template-inactive-001",
        "code": ErrorCode.VALIDATION_INVALID_ARGUMENT,
        "details": [{"field": "templateId", "message": "template is inactive"}],
    }



def test_create_class_draft_allows_payload_to_override_template_defaults() -> None:
    repository = InMemoryClassRepository()
    template_repository = InMemoryTemplateRepository([_seed_template()])

    response = create_class_draft(
        payload={
            "templateId": "tpl-weekend-001",
            "className": "自定义课程名",
            "classType": "CUSTOM",
            "priceAmount": 499,
            "depositAmount": 129,
            "minStudents": 8,
            "maxStudents": 16,
            "courseSubtitle": "自定义副标题",
            "targetAudience": "9-12岁学员",
            "unsuitableAudience": "零基础学员",
            "courseGoal": "强化阅读写作",
            "scheduleSummary": "每周日 14:00-16:00，连续 10 周",
            "sessionCount": 10,
            "groupRule": "满 8 人开班",
            "absenceRule": "课前 48 小时请假",
            "waitlistRule": "按优先级候补",
            "failureRule": "不成班转入下一期",
            "faqSummary": "含阶段测评",
        },
        repository=repository,
        template_repository=template_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-create-template-override-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 12, 30, tzinfo=timezone.utc),
    )

    assert response["code"] == ErrorCode.OK
    assert response["data"]["className"] == "自定义课程名"
    assert response["data"]["classType"] == "CUSTOM"
    assert response["data"]["priceAmount"] == 499
    assert response["data"]["depositAmount"] == 129
    assert response["data"]["minStudents"] == 8
    assert response["data"]["maxStudents"] == 16
    assert response["data"]["courseSubtitle"] == "自定义副标题"
    assert response["data"]["targetAudience"] == "9-12岁学员"
    assert response["data"]["unsuitableAudience"] == "零基础学员"
    assert response["data"]["courseGoal"] == "强化阅读写作"
    assert response["data"]["scheduleSummary"] == "每周日 14:00-16:00，连续 10 周"
    assert response["data"]["sessionCount"] == 10
    assert response["data"]["groupRule"] == "满 8 人开班"
    assert response["data"]["absenceRule"] == "课前 48 小时请假"
    assert response["data"]["waitlistRule"] == "按优先级候补"
    assert response["data"]["failureRule"] == "不成班转入下一期"
    assert response["data"]["faqSummary"] == "含阶段测评"



def test_create_class_draft_with_sqlite_repository_keeps_resolved_template_fields() -> None:
    connection = sqlite3.connect(":memory:")
    apply_schema(connection)
    repository = SQLiteClassRepository(connection)
    template_repository = InMemoryTemplateRepository([_seed_template()])

    response = create_class_draft(
        payload={"templateId": "tpl-weekend-001"},
        repository=repository,
        template_repository=template_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-create-template-sqlite-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 12, 45, tzinfo=timezone.utc),
    )
    persisted = repository.get(response["data"]["classId"])

    assert response["code"] == ErrorCode.OK
    assert persisted is not None
    assert persisted.template_id == "tpl-weekend-001"
    assert persisted.class_name == "周末英语基础模板"
    assert persisted.class_type == "ENGLISH"
    assert persisted.price_amount == 399
    assert persisted.deposit_amount == 99
    assert persisted.min_students == 6
    assert persisted.max_students == 12
    assert persisted.course_subtitle == "适合零基础启蒙"
    assert persisted.target_audience == "6-8岁学员"
    assert persisted.unsuitable_audience == "已有系统语法基础学员"
    assert persisted.course_goal == "建立基础听说表达能力"
    assert persisted.schedule_summary == "每周六 10:00-11:30，连续 8 周"
    assert persisted.session_count == 8
    assert persisted.group_rule == "满 6 人开班"
    assert persisted.absence_rule == "请假需至少提前 24 小时"
    assert persisted.waitlist_rule == "满班后按登记顺序候补"
    assert persisted.failure_rule == "不成班自动退款"
    assert persisted.faq_summary == "含教材，不含考试报名"



def test_create_class_draft_can_copy_reusable_fields_from_existing_class() -> None:
    repository = InMemoryClassRepository()
    original = create_class_draft(
        payload={
            "className": "原始课程",
            "templateId": "tpl-origin-001",
            "classType": "ENGLISH",
            "priceAmount": 499,
            "depositAmount": 129,
            "minStudents": 6,
            "maxStudents": 12,
            "courseSubtitle": "原课副标题",
            "targetAudience": "适合三到五年级",
            "unsuitableAudience": "不适合零基础",
            "courseGoal": "提升阅读表达",
            "scheduleSummary": "每周六上午",
            "sessionCount": 10,
            "groupRule": "满 6 人开班",
            "absenceRule": "可请假一次",
            "waitlistRule": "满班开放候补",
            "failureRule": "不成班退款",
            "faqSummary": "提供课后答疑",
        },
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-copy-source-create-001",
        actor_id="initiator-source-001",
        now=datetime(2026, 4, 12, 12, 50, tzinfo=timezone.utc),
    )
    original_id = original["data"]["classId"]
    original_persisted = repository.get(original_id)
    assert original_persisted is not None
    repository.save(
        replace(
            original_persisted,
            status=ClassStatus.OPEN_FOR_ENROLLMENT,
            reviewer_id="reviewer-001",
            current_students=11,
            waitlist_count=3,
            updated_at=datetime(2026, 4, 12, 13, 0, tzinfo=timezone.utc),
        )
    )

    response = create_class_draft(
        payload={
            "sourceClassId": original_id,
            "className": "原始课程-复制",
        },
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-copy-create-001",
        actor_id="initiator-copy-001",
        now=datetime(2026, 4, 12, 13, 5, tzinfo=timezone.utc),
    )
    copied_id = response["data"]["classId"]
    copied = repository.get(copied_id)

    assert response["code"] == ErrorCode.OK
    assert copied is not None
    assert copied_id != original_id
    assert response["data"]["status"] == ClassStatus.DRAFT
    assert response["data"]["version"] == 1
    assert response["data"]["creatorId"] == "initiator-copy-001"
    assert response["data"]["reviewerId"] is None
    assert response["data"]["currentStudents"] == 0
    assert response["data"]["waitlistCount"] == 0
    assert response["data"]["className"] == "原始课程-复制"
    assert response["data"]["templateId"] == "tpl-origin-001"
    assert response["data"]["courseSubtitle"] == "原课副标题"
    assert response["data"]["faqSummary"] == "提供课后答疑"
    assert copied.creator_id == "initiator-copy-001"
    assert copied.reviewer_id is None
    assert copied.current_students == 0
    assert copied.waitlist_count == 0
    assert copied.status == ClassStatus.DRAFT
    assert copied.template_id == "tpl-origin-001"
    assert copied.class_type == "ENGLISH"
    assert copied.price_amount == 499
    assert copied.deposit_amount == 129
    assert copied.min_students == 6
    assert copied.max_students == 12
    assert copied.course_subtitle == "原课副标题"
    assert copied.target_audience == "适合三到五年级"
    assert copied.unsuitable_audience == "不适合零基础"
    assert copied.course_goal == "提升阅读表达"
    assert copied.schedule_summary == "每周六上午"
    assert copied.session_count == 10
    assert copied.group_rule == "满 6 人开班"
    assert copied.absence_rule == "可请假一次"
    assert copied.waitlist_rule == "满班开放候补"
    assert copied.failure_rule == "不成班退款"
    assert copied.faq_summary == "提供课后答疑"



def test_create_class_draft_returns_not_found_when_source_class_does_not_exist() -> None:
    repository = InMemoryClassRepository()

    response = create_class_draft(
        payload={"sourceClassId": "cls-missing-001"},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-copy-missing-001",
        actor_id="initiator-copy-001",
        now=datetime(2026, 4, 12, 13, 10, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-copy-missing-001",
        "code": ErrorCode.CLASS_NOT_FOUND,
        "details": [{"field": "sourceClassId", "message": "source class not found"}],
    }



def test_submit_class_review_transitions_draft_to_pending_review() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)

    response = submit_class_review(
        class_id=class_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-submit-review-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 13, 30, tzinfo=timezone.utc),
    )

    assert response["code"] == ErrorCode.OK
    assert response["data"]["status"] == ClassStatus.PENDING_REVIEW
    assert response["data"]["version"] == 2
    assert response["data"]["actions"] == ["view"]


def test_submit_class_review_rejects_incomplete_class() -> None:
    repository = InMemoryClassRepository()
    response = create_class_draft(
        payload={"className": "信息不完整课程", "minStudents": 4},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-create-incomplete-review-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 12, 0, tzinfo=timezone.utc),
    )

    submit_response = submit_class_review(
        class_id=response["data"]["classId"],
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-submit-review-incomplete-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 13, 30, tzinfo=timezone.utc),
    )

    assert submit_response["code"] == ErrorCode.VALIDATION_INVALID_ARGUMENT
    missing_fields = {detail["field"] for detail in submit_response["details"]}
    assert {"priceAmount", "maxStudents", "scheduleSummary", "targetAudience", "courseGoal", "groupRule"}.issubset(missing_fields)



def test_submit_class_review_rejects_non_draft_status() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)
    submit_class_review(
        class_id=class_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-submit-review-seed-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 13, 30, tzinfo=timezone.utc),
    )

    response = submit_class_review(
        class_id=class_id,
        payload={"version": 2},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-submit-review-invalid-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 14, 0, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-submit-review-invalid-001",
        "code": ErrorCode.VALIDATION_INVALID_ARGUMENT,
        "details": [{"field": "status", "message": "only DRAFT or REJECTED classes can be submitted for review"}],
    }



def test_submit_class_review_returns_version_conflict() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)

    response = submit_class_review(
        class_id=class_id,
        payload={"version": 99},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-submit-review-conflict-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 13, 30, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-submit-review-conflict-001",
        "code": ErrorCode.CLASS_VERSION_CONFLICT,
        "details": [{"field": "version", "message": "version does not match current resource"}],
    }



def test_create_class_draft_persists_creator_for_resource_scope() -> None:
    repository = InMemoryClassRepository()

    response = create_class_draft(
        payload={
            "className": "权限测试课",
            "priceAmount": 199,
            "minStudents": 4,
        },
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-create-permission-001",
        actor_id="initiator-creator-001",
        now=datetime(2026, 4, 12, 12, 30, tzinfo=timezone.utc),
    )
    persisted = repository.get(response["data"]["classId"])

    assert response["code"] == ErrorCode.OK
    assert persisted is not None
    assert persisted.creator_id == "initiator-creator-001"



def test_approve_class_review_rejects_non_admin_roles() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)
    submit_class_review(
        class_id=class_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-submit-review-before-permission-approve-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 13, 30, tzinfo=timezone.utc),
    )

    response = approve_class_review(
        class_id=class_id,
        payload={"version": 2},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-approve-review-permission-001",
        actor_id="initiator-001",
        actor_roles=["INITIATOR"],
        now=datetime(2026, 4, 12, 14, 0, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-approve-review-permission-001",
        "code": ErrorCode.PERMISSION_DENIED,
        "details": [{"field": "actorRoles", "message": "only CLASS_ADMIN or SUPER_ADMIN can approve class review"}],
    }



def test_approve_class_review_requires_explicit_admin_role_context() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)
    submit_class_review(
        class_id=class_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-submit-review-before-explicit-approve-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 13, 30, tzinfo=timezone.utc),
    )

    response = approve_class_review(
        class_id=class_id,
        payload={"version": 2},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-approve-review-explicit-role-001",
        actor_id="reviewer-001",
        actor_roles=[],
        now=datetime(2026, 4, 12, 14, 0, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-approve-review-explicit-role-001",
        "code": ErrorCode.PERMISSION_DENIED,
        "details": [{"field": "actorRoles", "message": "only CLASS_ADMIN or SUPER_ADMIN can approve class review"}],
    }



def test_approve_class_review_allows_class_admin_and_persists_reviewer() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)
    submit_class_review(
        class_id=class_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-submit-review-before-approve-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 13, 30, tzinfo=timezone.utc),
    )

    response = approve_class_review(
        class_id=class_id,
        payload={"version": 2},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-approve-review-001",
        actor_id="reviewer-001",
        actor_roles=["CLASS_ADMIN"],
        now=datetime(2026, 4, 12, 14, 0, tzinfo=timezone.utc),
    )
    persisted = repository.get(class_id)

    assert response["code"] == ErrorCode.OK
    assert response["data"]["status"] == ClassStatus.OPEN_FOR_ENROLLMENT
    assert response["data"]["version"] == 3
    assert response["data"]["actions"] == ["view", "cancel"]
    assert response["data"]["reviewerId"] == "reviewer-001"
    assert persisted is not None
    assert persisted.reviewer_id == "reviewer-001"



def test_approve_class_review_rejects_non_pending_review_status() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)

    response = approve_class_review(
        class_id=class_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-approve-review-invalid-001",
        actor_id="reviewer-001",
        now=datetime(2026, 4, 12, 14, 0, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-approve-review-invalid-001",
        "code": ErrorCode.VALIDATION_INVALID_ARGUMENT,
        "details": [{"field": "status", "message": "only PENDING_REVIEW classes can be approved"}],
    }



def test_approve_class_review_returns_version_conflict() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)
    submit_class_review(
        class_id=class_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-submit-review-before-conflict-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 13, 30, tzinfo=timezone.utc),
    )

    response = approve_class_review(
        class_id=class_id,
        payload={"version": 99},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-approve-review-conflict-001",
        actor_id="reviewer-001",
        now=datetime(2026, 4, 12, 14, 0, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-approve-review-conflict-001",
        "code": ErrorCode.CLASS_VERSION_CONFLICT,
        "details": [{"field": "version", "message": "version does not match current resource"}],
    }



def test_sqlite_repository_persists_approve_review_flow() -> None:
    connection = sqlite3.connect(":memory:")
    apply_schema(connection)
    repository = SQLiteClassRepository(connection)
    class_id = _seed_class(repository)
    submit_class_review(
        class_id=class_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-submit-review-before-sqlite-approve-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 13, 30, tzinfo=timezone.utc),
    )

    response = approve_class_review(
        class_id=class_id,
        payload={"version": 2},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-approve-review-sqlite-001",
        actor_id="reviewer-001",
        actor_roles=["CLASS_ADMIN"],
        now=datetime(2026, 4, 12, 14, 0, tzinfo=timezone.utc),
    )
    persisted = repository.get(class_id)

    assert response["code"] == ErrorCode.OK
    assert response["data"]["status"] == ClassStatus.OPEN_FOR_ENROLLMENT
    assert persisted is not None
    assert persisted.status == ClassStatus.OPEN_FOR_ENROLLMENT
    assert persisted.version == 3
    assert persisted.reviewer_id == "reviewer-001"



def test_reject_class_review_transitions_pending_review_to_rejected() -> None:
    repository = InMemoryClassRepository()
    audit_writer = InMemoryAuditLog()
    class_id = _seed_class(repository)
    submit_class_review(
        class_id=class_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=audit_writer,
        request_id="req-submit-review-before-reject-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 13, 30, tzinfo=timezone.utc),
    )

    response = reject_class_review(
        class_id=class_id,
        payload={"version": 2, "reasonCode": "CONTENT_INCOMPLETE", "reasonText": "请补充课程亮点"},
        repository=repository,
        audit_writer=audit_writer,
        request_id="req-reject-review-001",
        actor_id="reviewer-001",
        actor_roles=["CLASS_ADMIN"],
        now=datetime(2026, 4, 12, 14, 30, tzinfo=timezone.utc),
    )
    persisted = repository.get(class_id)

    assert response["code"] == ErrorCode.OK
    assert response["data"]["status"] == ClassStatus.REJECTED
    assert response["data"]["version"] == 3
    assert response["data"]["actions"] == ["view", "edit", "submit_review"]
    assert response["data"]["reviewerId"] == "reviewer-001"
    assert response["data"]["reviewRejection"] == {"reasonCode": "CONTENT_INCOMPLETE", "reasonText": "请补充课程亮点"}
    history = audit_writer.list_for_resource("class", class_id)
    assert history[-1].metadata["reasonCode"] == "CONTENT_INCOMPLETE"
    assert history[-1].metadata["reasonText"] == "请补充课程亮点"
    assert persisted is not None
    assert persisted.reviewer_id == "reviewer-001"



def test_reject_class_review_rejects_non_pending_review_status() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)

    response = reject_class_review(
        class_id=class_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-reject-review-invalid-001",
        actor_id="reviewer-001",
        now=datetime(2026, 4, 12, 14, 30, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-reject-review-invalid-001",
        "code": ErrorCode.VALIDATION_INVALID_ARGUMENT,
        "details": [{"field": "status", "message": "only PENDING_REVIEW classes can be rejected"}],
    }



def test_reject_class_review_returns_version_conflict() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)
    submit_class_review(
        class_id=class_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-submit-review-before-reject-conflict-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 13, 30, tzinfo=timezone.utc),
    )

    response = reject_class_review(
        class_id=class_id,
        payload={"version": 99},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-reject-review-conflict-001",
        actor_id="reviewer-001",
        now=datetime(2026, 4, 12, 14, 30, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-reject-review-conflict-001",
        "code": ErrorCode.CLASS_VERSION_CONFLICT,
        "details": [{"field": "version", "message": "version does not match current resource"}],
    }



def test_reject_class_review_rejects_non_admin_roles() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)
    submit_class_review(
        class_id=class_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-submit-review-before-permission-reject-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 13, 30, tzinfo=timezone.utc),
    )

    response = reject_class_review(
        class_id=class_id,
        payload={"version": 2},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-reject-review-permission-001",
        actor_id="initiator-001",
        actor_roles=["INITIATOR"],
        now=datetime(2026, 4, 12, 14, 30, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-reject-review-permission-001",
        "code": ErrorCode.PERMISSION_DENIED,
        "details": [{"field": "actorRoles", "message": "only CLASS_ADMIN or SUPER_ADMIN can reject class review"}],
    }



def test_reject_class_review_requires_explicit_admin_role_context() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)
    submit_class_review(
        class_id=class_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-submit-review-before-explicit-reject-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 13, 30, tzinfo=timezone.utc),
    )

    response = reject_class_review(
        class_id=class_id,
        payload={"version": 2},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-reject-review-explicit-role-001",
        actor_id="reviewer-001",
        actor_roles=[],
        now=datetime(2026, 4, 12, 14, 30, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-reject-review-explicit-role-001",
        "code": ErrorCode.PERMISSION_DENIED,
        "details": [{"field": "actorRoles", "message": "only CLASS_ADMIN or SUPER_ADMIN can reject class review"}],
    }



def test_sqlite_repository_persists_reject_review_flow() -> None:
    connection = sqlite3.connect(":memory:")
    apply_schema(connection)
    repository = SQLiteClassRepository(connection)
    class_id = _seed_class(repository)
    submit_class_review(
        class_id=class_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-submit-review-before-sqlite-reject-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 13, 30, tzinfo=timezone.utc),
    )

    response = reject_class_review(
        class_id=class_id,
        payload={"version": 2},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-reject-review-sqlite-001",
        actor_id="reviewer-001",
        actor_roles=["CLASS_ADMIN"],
        now=datetime(2026, 4, 12, 14, 30, tzinfo=timezone.utc),
    )
    persisted = repository.get(class_id)

    assert response["code"] == ErrorCode.OK
    assert response["data"]["status"] == ClassStatus.REJECTED
    assert persisted is not None
    assert persisted.status == ClassStatus.REJECTED
    assert persisted.version == 3
    assert persisted.reviewer_id == "reviewer-001"



def test_sqlite_repository_persists_submit_review_flow() -> None:
    connection = sqlite3.connect(":memory:")
    apply_schema(connection)
    repository = SQLiteClassRepository(connection)
    class_id = _seed_class(repository)

    response = submit_class_review(
        class_id=class_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-submit-review-sqlite-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 13, 30, tzinfo=timezone.utc),
    )
    persisted = repository.get(class_id)

    assert response["code"] == ErrorCode.OK
    assert response["data"]["status"] == ClassStatus.PENDING_REVIEW
    assert persisted is not None
    assert persisted.status == ClassStatus.PENDING_REVIEW
    assert persisted.version == 2



def test_update_class_draft_supports_partial_update_and_version_bump() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)

    response = update_class_draft(
        class_id=class_id,
        payload={
            "version": 1,
            "maxStudents": 12,
            "depositAmount": 99,
        },
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-update-001",
        actor_id="admin-001",
        now=datetime(2026, 4, 12, 13, 0, tzinfo=timezone.utc),
    )

    assert response["code"] == ErrorCode.OK
    assert response["data"]["version"] == 2
    assert response["data"]["maxStudents"] == 12
    assert response["data"]["depositAmount"] == 99
    assert response["data"]["className"] == "周末拼课"



def test_update_class_draft_rejects_initiator_editing_other_users_class() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)

    response = update_class_draft(
        class_id=class_id,
        payload={"version": 1, "className": "越权修改"},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-update-permission-001",
        actor_id="initiator-002",
        actor_roles=["INITIATOR"],
        now=datetime(2026, 4, 12, 13, 5, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-update-permission-001",
        "code": ErrorCode.PERMISSION_DENIED,
        "details": [{"field": "actorId", "message": "INITIATOR can only edit classes they created"}],
    }



def test_update_class_draft_returns_version_conflict() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)

    response = update_class_draft(
        class_id=class_id,
        payload={"version": 99, "className": "冲突名称"},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-update-conflict-001",
        actor_id="admin-001",
        now=datetime(2026, 4, 12, 13, 0, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-update-conflict-001",
        "code": ErrorCode.CLASS_VERSION_CONFLICT,
        "details": [{"field": "version", "message": "version does not match current resource"}],
    }



def test_get_class_detail_returns_frozen_fields() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)

    response = get_class_detail(class_id=class_id, repository=repository, request_id="req-detail-001")

    assert response["code"] == ErrorCode.OK
    assert response["data"]["classId"] == class_id
    assert response["data"]["className"] == "周末拼课"
    assert response["data"]["actions"] == ["view", "edit", "submit_review"]



def test_get_class_detail_public_only_hides_non_visible_status() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)

    response = get_class_detail(
        class_id=class_id,
        repository=repository,
        request_id="req-detail-public-hidden-001",
        public_only=True,
    )

    assert response == {
        "requestId": "req-detail-public-hidden-001",
        "code": ErrorCode.CLASS_NOT_FOUND,
        "details": [{"field": "classId", "message": "class not found"}],
    }



def test_get_class_detail_public_only_returns_frontend_visible_item() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)
    submit_class_review(
        class_id=class_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-detail-public-submit-001",
        actor_id="admin-001",
        now=datetime(2026, 4, 12, 15, 0, tzinfo=timezone.utc),
    )
    approve_class_review(
        class_id=class_id,
        payload={"version": 2},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-detail-public-approve-001",
        actor_id="reviewer-001",
        actor_roles=["CLASS_ADMIN"],
        now=datetime(2026, 4, 12, 15, 30, tzinfo=timezone.utc),
    )

    response = get_class_detail(
        class_id=class_id,
        repository=repository,
        request_id="req-detail-public-visible-001",
        public_only=True,
    )

    assert response["code"] == ErrorCode.OK
    assert response["data"]["classId"] == class_id
    assert response["data"]["status"] == ClassStatus.OPEN_FOR_ENROLLMENT
    assert response["data"]["actions"] == ["view"]



def test_sqlite_repository_public_detail_hides_non_visible_status() -> None:
    connection = sqlite3.connect(":memory:")
    apply_schema(connection)
    repository = SQLiteClassRepository(connection)
    class_id = _seed_class(repository)

    response = get_class_detail(
        class_id=class_id,
        repository=repository,
        request_id="req-sqlite-detail-public-hidden-001",
        public_only=True,
    )

    assert response == {
        "requestId": "req-sqlite-detail-public-hidden-001",
        "code": ErrorCode.CLASS_NOT_FOUND,
        "details": [{"field": "classId", "message": "class not found"}],
    }



def test_sqlite_repository_public_detail_returns_frontend_visible_item() -> None:
    connection = sqlite3.connect(":memory:")
    apply_schema(connection)
    repository = SQLiteClassRepository(connection)
    class_id = _seed_class(repository)
    submit_class_review(
        class_id=class_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-sqlite-detail-public-submit-001",
        actor_id="admin-001",
        now=datetime(2026, 4, 12, 16, 0, tzinfo=timezone.utc),
    )
    approve_class_review(
        class_id=class_id,
        payload={"version": 2},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-sqlite-detail-public-approve-001",
        actor_id="reviewer-001",
        actor_roles=["CLASS_ADMIN"],
        now=datetime(2026, 4, 12, 16, 20, tzinfo=timezone.utc),
    )

    response = get_class_detail(
        class_id=class_id,
        repository=repository,
        request_id="req-sqlite-detail-public-visible-001",
        public_only=True,
    )

    assert response["code"] == ErrorCode.OK
    assert response["data"]["classId"] == class_id
    assert response["data"]["status"] == ClassStatus.OPEN_FOR_ENROLLMENT
    assert response["data"]["actions"] == ["view"]



def test_submit_class_review_rejects_initiator_submitting_other_users_class() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)

    response = submit_class_review(
        class_id=class_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-submit-review-permission-001",
        actor_id="initiator-002",
        actor_roles=["INITIATOR"],
        now=datetime(2026, 4, 12, 13, 30, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-submit-review-permission-001",
        "code": ErrorCode.PERMISSION_DENIED,
        "details": [{"field": "actorId", "message": "INITIATOR can only submit classes they created for review"}],
    }



def test_list_classes_returns_paged_admin_items() -> None:
    repository = InMemoryClassRepository()
    first_id = _seed_class(repository)
    second = create_class_draft(
        payload={"className": "工作日晚课", "minStudents": 4},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-seed-002",
        actor_id="admin-001",
        now=datetime(2026, 4, 12, 14, 0, tzinfo=timezone.utc),
    )
    second_id = second["data"]["classId"]
    update_class_draft(
        class_id=first_id,
        payload={"version": 1, "maxStudents": 10},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-update-ordered-001",
        actor_id="admin-001",
        now=datetime(2026, 4, 12, 15, 0, tzinfo=timezone.utc),
    )

    response = list_classes(repository=repository, request_id="req-list-001", page=1, page_size=1)

    assert response["code"] == ErrorCode.OK
    assert response["data"]["page"] == 1
    assert response["data"]["pageSize"] == 1
    assert response["data"]["total"] == 2
    assert len(response["data"]["items"]) == 1
    assert response["data"]["items"][0]["classId"] == first_id
    assert set(response["data"]["items"][0].keys()) == {
        "classId",
        "className",
        "status",
        "classType",
        "startDate",
        "endDate",
        "signupDeadline",
        "currentStudents",
        "minStudents",
        "maxStudents",
        "actions",
        "updatedAt",
    }
    assert second_id != first_id



def test_list_classes_public_only_returns_frontend_visible_items() -> None:
    repository = InMemoryClassRepository()
    visible_id = _seed_class(repository)
    pending_id = create_class_draft(
        payload={"className": "待审核课程", "minStudents": 4},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-public-seed-pending-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 14, 0, tzinfo=timezone.utc),
    )["data"]["classId"]
    rejected_id = create_class_draft(
        payload={"className": "已驳回课程", "minStudents": 4},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-public-seed-rejected-001",
        actor_id="initiator-002",
        now=datetime(2026, 4, 12, 14, 30, tzinfo=timezone.utc),
    )["data"]["classId"]

    submit_class_review(
        class_id=visible_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-public-submit-visible-001",
        actor_id="admin-001",
        now=datetime(2026, 4, 12, 15, 0, tzinfo=timezone.utc),
    )
    approve_class_review(
        class_id=visible_id,
        payload={"version": 2},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-public-approve-visible-001",
        actor_id="reviewer-001",
        actor_roles=["CLASS_ADMIN"],
        now=datetime(2026, 4, 12, 15, 30, tzinfo=timezone.utc),
    )
    submit_class_review(
        class_id=pending_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-public-submit-pending-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 15, 10, tzinfo=timezone.utc),
    )
    submit_class_review(
        class_id=rejected_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-public-submit-rejected-001",
        actor_id="initiator-002",
        now=datetime(2026, 4, 12, 15, 20, tzinfo=timezone.utc),
    )
    reject_class_review(
        class_id=rejected_id,
        payload={"version": 2},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-public-reject-rejected-001",
        actor_id="reviewer-002",
        actor_roles=["CLASS_ADMIN"],
        now=datetime(2026, 4, 12, 15, 40, tzinfo=timezone.utc),
    )

    response = list_classes(
        repository=repository,
        request_id="req-public-list-001",
        page=1,
        page_size=10,
        public_only=True,
    )

    assert response["code"] == ErrorCode.OK
    assert response["data"]["total"] == 1
    assert [item["classId"] for item in response["data"]["items"]] == [visible_id]
    assert all(item["status"] == ClassStatus.OPEN_FOR_ENROLLMENT for item in response["data"]["items"])



def test_sqlite_repository_public_only_list_filters_non_visible_statuses() -> None:
    connection = sqlite3.connect(":memory:")
    apply_schema(connection)
    repository = SQLiteClassRepository(connection)
    visible_id = _seed_class(repository)
    pending_id = create_class_draft(
        payload={"className": "SQLite 待审核课", "minStudents": 4},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-sqlite-public-pending-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 16, 0, tzinfo=timezone.utc),
    )["data"]["classId"]

    submit_class_review(
        class_id=visible_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-sqlite-public-submit-visible-001",
        actor_id="admin-001",
        now=datetime(2026, 4, 12, 16, 10, tzinfo=timezone.utc),
    )
    approve_class_review(
        class_id=visible_id,
        payload={"version": 2},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-sqlite-public-approve-visible-001",
        actor_id="reviewer-001",
        actor_roles=["CLASS_ADMIN"],
        now=datetime(2026, 4, 12, 16, 20, tzinfo=timezone.utc),
    )
    submit_class_review(
        class_id=pending_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-sqlite-public-submit-pending-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 16, 15, tzinfo=timezone.utc),
    )

    response = list_classes(
        repository=repository,
        request_id="req-sqlite-public-list-001",
        page=1,
        page_size=10,
        public_only=True,
    )

    assert response["code"] == ErrorCode.OK
    assert response["data"]["total"] == 1
    assert [item["classId"] for item in response["data"]["items"]] == [visible_id]



def test_sqlite_repository_supports_create_update_detail_and_list_flow() -> None:
    connection = sqlite3.connect(":memory:")
    apply_schema(connection)
    repository = SQLiteClassRepository(connection)

    created = create_class_draft(
        payload={
            "className": "晚间瑜伽班",
            "templateId": "tpl-yoga-001",
            "priceAmount": 399,
            "depositAmount": 99,
            "minStudents": 5,
            "maxStudents": 10,
        },
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-sqlite-create-001",
        actor_id="admin-001",
        now=datetime(2026, 4, 12, 16, 0, tzinfo=timezone.utc),
    )
    class_id = created["data"]["classId"]

    updated = update_class_draft(
        class_id=class_id,
        payload={"version": 1, "maxStudents": 12, "classType": "YOGA"},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-sqlite-update-001",
        actor_id="admin-001",
        now=datetime(2026, 4, 12, 16, 30, tzinfo=timezone.utc),
    )
    detail = get_class_detail(class_id=class_id, repository=repository, request_id="req-sqlite-detail-001")
    listing = list_classes(repository=repository, request_id="req-sqlite-list-001", page=1, page_size=10)

    assert created["code"] == ErrorCode.OK
    assert updated["code"] == ErrorCode.OK
    assert updated["data"]["version"] == 2
    assert updated["data"]["maxStudents"] == 12
    assert updated["data"]["classType"] == "YOGA"
    assert detail["code"] == ErrorCode.OK
    assert detail["data"]["classId"] == class_id
    assert detail["data"]["templateId"] == "tpl-yoga-001"
    assert listing["code"] == ErrorCode.OK
    assert listing["data"]["total"] == 1
    assert listing["data"]["items"][0]["classId"] == class_id
    assert listing["data"]["items"][0]["actions"] == ["view", "edit", "submit_review"]



def test_get_class_detail_public_only_returns_frontend_detail_fields() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)
    current = repository.get(class_id)
    assert current is not None
    repository.save(
        replace(
            current,
            status=ClassStatus.ALMOST_CONFIRMED,
            class_type="ENGLISH",
            price_amount=299,
            min_students=6,
            max_students=8,
            current_students=5,
            waitlist_count=0,
            course_subtitle="小班冲刺提升",
            target_audience="适合三至五年级学员",
            unsuitable_audience="不适合零基础学员",
            course_goal="建立阅读与表达基础",
            schedule_summary="每周六 10:00-12:00",
            session_count=12,
            group_rule="满 6 人开班",
            absence_rule="支持请假一次并补发回放",
            waitlist_rule="满员后按登记顺序候补",
            failure_rule="未成班则原路退款",
            faq_summary="可先预约测评，再决定是否报名",
            updated_at=datetime(2026, 4, 12, 17, 0, tzinfo=timezone.utc),
        )
    )

    response = get_class_detail(
        class_id=class_id,
        repository=repository,
        request_id="req-public-detail-frontend-001",
        public_only=True,
    )

    assert response["code"] == ErrorCode.OK
    assert response["data"]["classId"] == class_id
    assert response["data"]["status"] == ClassStatus.ALMOST_CONFIRMED
    assert response["data"]["statusLabel"] == "即将成班"
    assert response["data"]["progressText"] == "还差 1 人成班"
    assert response["data"]["primaryAction"] == "enroll"
    assert response["data"]["primaryActionLabel"] == "立即报名"
    assert response["data"]["remainingSeats"] == 3
    assert response["data"]["isWaitlistAvailable"] is False
    assert response["data"]["courseSubtitle"] == "小班冲刺提升"
    assert response["data"]["targetAudience"] == "适合三至五年级学员"
    assert response["data"]["unsuitableAudience"] == "不适合零基础学员"
    assert response["data"]["courseGoal"] == "建立阅读与表达基础"
    assert response["data"]["scheduleSummary"] == "每周六 10:00-12:00"
    assert response["data"]["sessionCount"] == 12
    assert response["data"]["groupRule"] == "满 6 人开班"
    assert response["data"]["absenceRule"] == "支持请假一次并补发回放"
    assert response["data"]["waitlistRule"] == "满员后按登记顺序候补"
    assert response["data"]["failureRule"] == "未成班则原路退款"
    assert response["data"]["faqSummary"] == "可先预约测评，再决定是否报名"



def test_get_class_detail_public_only_returns_detail_content_from_sqlite_repository() -> None:
    connection = sqlite3.connect(":memory:")
    apply_schema(connection)
    repository = SQLiteClassRepository(connection)
    created = create_class_draft(
        payload={
            "className": "寒假阅读班",
            "priceAmount": 499,
            "minStudents": 6,
            "maxStudents": 12,
            "courseSubtitle": "阅读专项提升",
            "scheduleSummary": "每周六 10:00-11:30",
            "targetAudience": "适合四至六年级",
            "courseGoal": "提升阅读理解能力",
            "groupRule": "满 6 人开班",
            "faqSummary": "开课前会统一建群通知",
        },
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-public-detail-sqlite-create-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 16, 0, tzinfo=timezone.utc),
    )
    class_id = created["data"]["classId"]
    submit_class_review(
        class_id=class_id,
        payload={"version": 1},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-public-detail-sqlite-submit-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 16, 10, tzinfo=timezone.utc),
    )
    approve_class_review(
        class_id=class_id,
        payload={"version": 2},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-public-detail-sqlite-approve-001",
        actor_id="reviewer-001",
        actor_roles=["CLASS_ADMIN"],
        now=datetime(2026, 4, 12, 16, 20, tzinfo=timezone.utc),
    )

    response = get_class_detail(
        class_id=class_id,
        repository=repository,
        request_id="req-public-detail-sqlite-visible-001",
        public_only=True,
    )

    assert response["code"] == ErrorCode.OK
    assert response["data"]["courseSubtitle"] == "阅读专项提升"
    assert response["data"]["targetAudience"] == "适合四至六年级"
    assert response["data"]["courseGoal"] == "提升阅读理解能力"
    assert response["data"]["groupRule"] == "满 6 人开班"
    assert response["data"]["faqSummary"] == "开课前会统一建群通知"



def test_update_class_draft_supports_batch3_detail_content_fields() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)

    response = update_class_draft(
        class_id=class_id,
        payload={
            "version": 1,
            "courseSubtitle": "春季拼课进阶班",
            "targetAudience": "适合三年级学员",
            "unsuitableAudience": "不适合完全零基础",
            "courseGoal": "建立自然拼读基础",
            "scheduleSummary": "每周三 19:00-20:30",
            "sessionCount": 10,
            "groupRule": "满 5 人开班",
            "absenceRule": "请假后可补看录播",
            "waitlistRule": "满员后开放候补",
            "failureRule": "未成班自动退款",
            "faqSummary": "支持课前水平测评",
        },
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-update-detail-fields-001",
        actor_id="admin-001",
        now=datetime(2026, 4, 12, 18, 30, tzinfo=timezone.utc),
    )

    assert response["code"] == ErrorCode.OK
    assert response["data"]["courseSubtitle"] == "春季拼课进阶班"
    assert response["data"]["targetAudience"] == "适合三年级学员"
    assert response["data"]["unsuitableAudience"] == "不适合完全零基础"
    assert response["data"]["courseGoal"] == "建立自然拼读基础"
    assert response["data"]["scheduleSummary"] == "每周三 19:00-20:30"
    assert response["data"]["sessionCount"] == 10
    assert response["data"]["groupRule"] == "满 5 人开班"
    assert response["data"]["absenceRule"] == "请假后可补看录播"
    assert response["data"]["waitlistRule"] == "满员后开放候补"
    assert response["data"]["failureRule"] == "未成班自动退款"
    assert response["data"]["faqSummary"] == "支持课前水平测评"



def test_create_class_draft_rejects_non_positive_session_count() -> None:
    repository = InMemoryClassRepository()

    response = create_class_draft(
        payload={
            "className": "无效课时班",
            "sessionCount": 0,
        },
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-invalid-session-count-001",
        actor_id="initiator-001",
        now=datetime(2026, 4, 12, 18, 45, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-invalid-session-count-001",
        "code": ErrorCode.VALIDATION_INVALID_ARGUMENT,
        "details": [{"field": "sessionCount", "message": "sessionCount must be greater than 0"}],
    }



def test_list_classes_public_only_returns_frontend_card_fields() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)
    current = repository.get(class_id)
    assert current is not None
    repository.save(
        replace(
            current,
            status=ClassStatus.FULL,
            class_type="ENGLISH",
            price_amount=399,
            min_students=6,
            max_students=6,
            current_students=6,
            waitlist_count=2,
            updated_at=datetime(2026, 4, 12, 18, 0, tzinfo=timezone.utc),
        )
    )

    response = list_classes(
        repository=repository,
        request_id="req-public-list-frontend-001",
        page=1,
        page_size=10,
        public_only=True,
    )

    assert response["code"] == ErrorCode.OK
    assert response["data"]["total"] == 1
    item = response["data"]["items"][0]
    assert item["classId"] == class_id
    assert item["status"] == ClassStatus.FULL
    assert item["statusLabel"] == "已满员"
    assert item["progressText"] == "已满员，可加入候补"
    assert item["primaryAction"] == "join_waitlist"
    assert item["primaryActionLabel"] == "加入候补"
    assert item["remainingSeats"] == 0
    assert item["waitlistCount"] == 2



def test_get_class_detail_returns_not_found() -> None:
    repository = InMemoryClassRepository()

    response = get_class_detail(class_id="cls-missing", repository=repository, request_id="req-detail-missing-001")

    assert response == {
        "requestId": "req-detail-missing-001",
        "code": ErrorCode.CLASS_NOT_FOUND,
        "details": [{"field": "classId", "message": "class not found"}],
    }


def test_cancel_class_allows_admin_for_published_status_and_hides_from_public() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)
    current = repository.get(class_id)
    assert current is not None
    repository.update(replace(current, status=ClassStatus.OPEN_FOR_ENROLLMENT))
    published = repository.get(class_id)
    assert published is not None

    response = cancel_class(
        class_id=class_id,
        payload={"version": published.version},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-cancel-001",
        actor_id="admin-001",
        actor_roles=["CLASS_ADMIN"],
        now=datetime(2026, 4, 12, 19, 0, tzinfo=timezone.utc),
    )
    public_detail = get_class_detail(
        class_id=class_id,
        repository=repository,
        request_id="req-cancel-public-detail-001",
        public_only=True,
    )
    public_list = list_classes(
        repository=repository,
        request_id="req-cancel-public-list-001",
        page=1,
        page_size=10,
        public_only=True,
    )

    assert response["code"] == ErrorCode.OK
    assert response["data"]["status"] == ClassStatus.CANCELLED
    assert public_detail["code"] == ErrorCode.CLASS_NOT_FOUND
    assert public_list["data"]["items"] == []


def test_cancel_class_rejects_initiator_role() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)
    current = repository.get(class_id)
    assert current is not None
    repository.update(replace(current, status=ClassStatus.OPEN_FOR_ENROLLMENT))
    published = repository.get(class_id)
    assert published is not None

    response = cancel_class(
        class_id=class_id,
        payload={"version": published.version},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-cancel-denied-001",
        actor_id="initiator-001",
        actor_roles=["INITIATOR"],
        now=datetime(2026, 4, 12, 19, 10, tzinfo=timezone.utc),
    )

    assert response["code"] == ErrorCode.PERMISSION_DENIED


def test_cancel_class_rejects_draft_status() -> None:
    repository = InMemoryClassRepository()
    class_id = _seed_class(repository)
    current = repository.get(class_id)
    assert current is not None

    response = cancel_class(
        class_id=class_id,
        payload={"version": current.version},
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-cancel-draft-001",
        actor_id="admin-001",
        actor_roles=["CLASS_ADMIN"],
        now=datetime(2026, 4, 12, 19, 20, tzinfo=timezone.utc),
    )

    assert response["code"] == ErrorCode.VALIDATION_INVALID_ARGUMENT
