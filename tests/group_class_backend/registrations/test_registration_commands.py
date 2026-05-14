from datetime import datetime, timezone
import sqlite3
from dataclasses import replace

from apps.group_class_backend.audit.interface import NullAuditWriter
from apps.group_class_backend.classes.controller import create_class_draft
from apps.group_class_backend.classes.repository import InMemoryClassRepository, SQLiteClassRepository
from apps.group_class_backend.common.error_codes import ErrorCode
from apps.group_class_backend.common.enums import ClassStatus
from apps.group_class_backend.persistence.schema import apply_schema
from apps.group_class_backend.registrations.controller import (
    get_registration_detail,
    list_registrations,
    submit_registration,
    update_registration_notes,
    update_registration_payment_status,
    update_registration_status,
)

from apps.group_class_backend.registrations.repository import InMemoryRegistrationRepository, SQLiteRegistrationRepository


def _seed_open_class(repository: InMemoryClassRepository | SQLiteClassRepository) -> str:
    response = create_class_draft(
        payload={
            "className": "周末拼课",
            "priceAmount": 299,
            "minStudents": 2,
            "maxStudents": 3,
        },
        repository=repository,
        audit_writer=NullAuditWriter(),
        request_id="req-seed-registration-class-001",
        actor_id="admin-001",
        now=datetime(2026, 4, 12, 12, 0, tzinfo=timezone.utc),
    )
    class_id = response["data"]["classId"]
    current = repository.get(class_id)
    assert current is not None
    repository.update(replace(current, status=ClassStatus.OPEN_FOR_ENROLLMENT))
    return class_id


def test_submit_enrollment_registration_creates_record_and_updates_student_count() -> None:
    class_repository = InMemoryClassRepository()
    registration_repository = InMemoryRegistrationRepository()
    class_id = _seed_open_class(class_repository)

    response = submit_registration(
        payload={
            "classId": class_id,
            "registerType": "ENROLLMENT",
            "parentName": "张女士",
            "contactInfo": "13800000000",
            "studentName": "张三",
            "studentGrade": "三年级",
            "englishLevel": "基础一般",
            "acceptTransfer": True,
            "acceptWaitlist": True,
            "remark": "希望同校同学一起",
        },
        class_repository=class_repository,
        registration_repository=registration_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-registration-enrollment-001",
        actor_id="parent-001",
        now=datetime(2026, 4, 12, 15, 0, tzinfo=timezone.utc),
    )
    persisted_class = class_repository.get(class_id)
    persisted_registration = registration_repository.list()[0]

    assert response == {
        "requestId": "req-registration-enrollment-001",
        "code": "OK",
        "data": {
            "registrationId": persisted_registration.registration_id,
            "registerType": "ENROLLMENT",
            "registrationStatus": "SUBMITTED",
            "classStatus": "OPEN_FOR_ENROLLMENT",
            "nextStepText": "提交成功，老师/运营将尽快联系确认",
        },
    }
    assert persisted_registration.parent_name == "张女士"
    assert persisted_registration.student_name == "张三"
    assert persisted_class is not None
    assert persisted_class.current_students == 1
    assert persisted_class.waitlist_count == 0


def test_submit_waitlist_registration_creates_record_and_updates_waitlist_count() -> None:
    class_repository = InMemoryClassRepository()
    registration_repository = InMemoryRegistrationRepository()
    class_id = _seed_open_class(class_repository)
    current = class_repository.get(class_id)
    assert current is not None
    class_repository.update(replace(current, status=ClassStatus.WAITLIST_OPEN))

    response = submit_registration(
        payload={
            "classId": class_id,
            "registerType": "WAITLIST",
            "parentName": "李女士",
            "contactInfo": "13900000000",
            "studentGrade": "四年级",
            "acceptSimilarRecommendation": True,
            "remark": "可接受相近时间段",
        },
        class_repository=class_repository,
        registration_repository=registration_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-registration-waitlist-001",
        actor_id="parent-002",
        now=datetime(2026, 4, 12, 15, 10, tzinfo=timezone.utc),
    )
    persisted_class = class_repository.get(class_id)
    persisted_registration = registration_repository.list()[0]

    assert response["code"] == ErrorCode.OK
    assert response["data"]["registerType"] == "WAITLIST"
    assert response["data"]["registrationStatus"] == "WAITLISTED"
    assert persisted_registration.accept_similar_recommendation is True
    assert persisted_class is not None
    assert persisted_class.current_students == 0
    assert persisted_class.waitlist_count == 1


def test_submit_trial_registration_creates_record_without_incrementing_class_counts() -> None:
    class_repository = InMemoryClassRepository()
    registration_repository = InMemoryRegistrationRepository()
    class_id = _seed_open_class(class_repository)

    response = submit_registration(
        payload={
            "classId": class_id,
            "registerType": "TRIAL",
            "parentName": "王女士",
            "contactInfo": "13700000000",
            "studentGrade": "二年级",
            "wantsTrial": True,
            "remark": "希望先试听再决定",
        },
        class_repository=class_repository,
        registration_repository=registration_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-registration-trial-001",
        actor_id="parent-003",
        now=datetime(2026, 4, 12, 15, 20, tzinfo=timezone.utc),
    )
    persisted_class = class_repository.get(class_id)
    persisted_registration = registration_repository.list()[0]

    assert response == {
        "requestId": "req-registration-trial-001",
        "code": "OK",
        "data": {
            "registrationId": persisted_registration.registration_id,
            "registerType": "TRIAL",
            "registrationStatus": "SUBMITTED",
            "classStatus": "OPEN_FOR_ENROLLMENT",
            "nextStepText": "试听申请已提交，老师/运营将尽快联系确认",
        },
    }
    assert persisted_registration.wants_trial is True
    assert persisted_registration.student_name is None
    assert persisted_class is not None
    assert persisted_class.current_students == 0
    assert persisted_class.waitlist_count == 0


def test_submit_registration_rejects_unknown_class() -> None:
    response = submit_registration(
        payload={
            "classId": "cls-missing",
            "registerType": "ENROLLMENT",
            "parentName": "张女士",
            "contactInfo": "13800000000",
            "studentName": "张三",
            "studentGrade": "三年级",
        },
        class_repository=InMemoryClassRepository(),
        registration_repository=InMemoryRegistrationRepository(),
        audit_writer=NullAuditWriter(),
        request_id="req-registration-not-found-001",
        actor_id="parent-001",
        now=datetime(2026, 4, 12, 15, 0, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-registration-not-found-001",
        "code": ErrorCode.CLASS_NOT_FOUND,
        "details": [{"field": "classId", "message": "class not found"}],
    }


def test_submit_registration_rejects_disallowed_class_status() -> None:
    class_repository = InMemoryClassRepository()
    registration_repository = InMemoryRegistrationRepository()
    class_id = create_class_draft(
        payload={"className": "待审核拼课", "minStudents": 2},
        repository=class_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-seed-draft-class-001",
        actor_id="admin-001",
        now=datetime(2026, 4, 12, 12, 0, tzinfo=timezone.utc),
    )["data"]["classId"]

    response = submit_registration(
        payload={
            "classId": class_id,
            "registerType": "ENROLLMENT",
            "parentName": "张女士",
            "contactInfo": "13800000000",
            "studentName": "张三",
            "studentGrade": "三年级",
        },
        class_repository=class_repository,
        registration_repository=registration_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-registration-invalid-status-001",
        actor_id="parent-001",
        now=datetime(2026, 4, 12, 15, 0, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-registration-invalid-status-001",
        "code": ErrorCode.VALIDATION_INVALID_ARGUMENT,
        "details": [{"field": "status", "message": "class status does not accept ENROLLMENT registration"}],
    }


def test_submit_registration_rejects_waitlist_for_non_waitlist_status() -> None:
    class_repository = InMemoryClassRepository()
    registration_repository = InMemoryRegistrationRepository()
    class_id = _seed_open_class(class_repository)

    response = submit_registration(
        payload={
            "classId": class_id,
            "registerType": "WAITLIST",
            "parentName": "李女士",
            "contactInfo": "13900000000",
            "studentGrade": "四年级",
        },
        class_repository=class_repository,
        registration_repository=registration_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-registration-invalid-waitlist-status-001",
        actor_id="parent-002",
        now=datetime(2026, 4, 12, 15, 10, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-registration-invalid-waitlist-status-001",
        "code": ErrorCode.VALIDATION_INVALID_ARGUMENT,
        "details": [{"field": "status", "message": "class status does not accept WAITLIST registration"}],
    }


def test_submit_registration_persists_sqlite_flow() -> None:
    connection = sqlite3.connect(":memory:")
    apply_schema(connection)
    class_repository = SQLiteClassRepository(connection)
    registration_repository = SQLiteRegistrationRepository(connection)
    class_id = _seed_open_class(class_repository)

    response = submit_registration(
        payload={
            "classId": class_id,
            "registerType": "ENROLLMENT",
            "parentName": "张女士",
            "contactInfo": "13800000000",
            "studentName": "张三",
            "studentGrade": "三年级",
        },
        class_repository=class_repository,
        registration_repository=registration_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-registration-sqlite-001",
        actor_id="parent-001",
        now=datetime(2026, 4, 12, 15, 0, tzinfo=timezone.utc),
    )
    persisted_class = class_repository.get(class_id)
    persisted_registration = registration_repository.list()[0]

    assert response["code"] == ErrorCode.OK
    assert persisted_registration.class_id == class_id
    assert persisted_class is not None
    assert persisted_class.current_students == 1


def test_submit_trial_registration_persists_sqlite_flow_without_incrementing_class_counts() -> None:
    connection = sqlite3.connect(":memory:")
    apply_schema(connection)
    class_repository = SQLiteClassRepository(connection)
    registration_repository = SQLiteRegistrationRepository(connection)
    class_id = _seed_open_class(class_repository)

    response = submit_registration(
        payload={
            "classId": class_id,
            "registerType": "TRIAL",
            "parentName": "王女士",
            "contactInfo": "13700000000",
            "studentGrade": "二年级",
            "wantsTrial": True,
        },
        class_repository=class_repository,
        registration_repository=registration_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-registration-trial-sqlite-001",
        actor_id="parent-003",
        now=datetime(2026, 4, 12, 15, 20, tzinfo=timezone.utc),
    )
    persisted_class = class_repository.get(class_id)
    persisted_registration = registration_repository.list()[0]

    assert response["code"] == ErrorCode.OK
    assert response["data"]["registerType"] == "TRIAL"
    assert persisted_registration.class_id == class_id
    assert persisted_registration.wants_trial is True
    assert persisted_class is not None
    assert persisted_class.current_students == 0
    assert persisted_class.waitlist_count == 0


def test_list_registrations_returns_only_owned_class_records_for_initiator() -> None:
    class_repository = InMemoryClassRepository()
    registration_repository = InMemoryRegistrationRepository()
    owned_class_id = _seed_open_class(class_repository)
    other_class_response = create_class_draft(
        payload={
            "className": "其他发起人的拼课",
            "priceAmount": 199,
            "minStudents": 2,
            "maxStudents": 4,
        },
        repository=class_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-seed-other-class-001",
        actor_id="initiator-002",
        now=datetime(2026, 4, 12, 12, 30, tzinfo=timezone.utc),
    )
    other_class_id = other_class_response["data"]["classId"]
    other_class = class_repository.get(other_class_id)
    assert other_class is not None
    class_repository.update(replace(other_class, status=ClassStatus.OPEN_FOR_ENROLLMENT))

    submit_registration(
        payload={
            "classId": owned_class_id,
            "registerType": "ENROLLMENT",
            "parentName": "张女士",
            "contactInfo": "13800000000",
            "studentName": "张三",
            "studentGrade": "三年级",
        },
        class_repository=class_repository,
        registration_repository=registration_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-registration-owned-class-001",
        actor_id="parent-001",
        now=datetime(2026, 4, 12, 15, 0, tzinfo=timezone.utc),
    )
    submit_registration(
        payload={
            "classId": other_class_id,
            "registerType": "WAITLIST",
            "parentName": "李女士",
            "contactInfo": "13900000000",
            "studentGrade": "四年级",
            "acceptSimilarRecommendation": True,
        },
        class_repository=class_repository,
        registration_repository=registration_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-registration-other-class-001",
        actor_id="parent-002",
        now=datetime(2026, 4, 12, 15, 10, tzinfo=timezone.utc),
    )

    response = list_registrations(
        class_repository=class_repository,
        registration_repository=registration_repository,
        request_id="req-registration-list-initiator-001",
        actor_id="admin-001",
        actor_roles=["INITIATOR"],
    )

    assert response == {
        "requestId": "req-registration-list-initiator-001",
        "code": ErrorCode.OK,
        "data": {
            "items": [
                {
                    "registrationId": registration_repository.list()[0].registration_id,
                    "classId": owned_class_id,
                    "className": "周末拼课",
                    "registerType": "ENROLLMENT",
                    "registrationStatus": "SUBMITTED",
                    "parentName": "张女士",
                    "studentName": "张三",
                    "studentGrade": "三年级",
                    "contactInfo": "13800000000",
                        "submittedAt": "2026-04-12T15:00:00+00:00",
                        "paymentStatus": "UNPAID",
                        "followUpNote": None,
                    "notes": None,
                }
            ]
        },
    }


def test_list_registrations_rejects_user_without_backoffice_roles() -> None:
    class_repository = InMemoryClassRepository()
    registration_repository = InMemoryRegistrationRepository()
    _seed_open_class(class_repository)

    response = list_registrations(
        class_repository=class_repository,
        registration_repository=registration_repository,
        request_id="req-registration-list-user-001",
        actor_id="user-001",
        actor_roles=["USER"],
    )

    assert response == {
        "requestId": "req-registration-list-user-001",
        "code": ErrorCode.PERMISSION_DENIED,
        "details": [{"field": "actorRoles", "message": "only CLASS_ADMIN, SUPER_ADMIN, or INITIATOR can view registration data"}],
    }


def test_list_registrations_persists_sqlite_filtering_for_initiator() -> None:
    connection = sqlite3.connect(":memory:")
    apply_schema(connection)
    class_repository = SQLiteClassRepository(connection)
    registration_repository = SQLiteRegistrationRepository(connection)
    owned_class_id = _seed_open_class(class_repository)
    other_class_response = create_class_draft(
        payload={
            "className": "其他发起人的 SQLite 拼课",
            "priceAmount": 399,
            "minStudents": 2,
            "maxStudents": 5,
        },
        repository=class_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-seed-sqlite-other-class-001",
        actor_id="initiator-002",
        now=datetime(2026, 4, 12, 12, 40, tzinfo=timezone.utc),
    )
    other_class_id = other_class_response["data"]["classId"]
    other_class = class_repository.get(other_class_id)
    assert other_class is not None
    class_repository.update(replace(other_class, status=ClassStatus.OPEN_FOR_ENROLLMENT))

    submit_registration(
        payload={
            "classId": owned_class_id,
            "registerType": "ENROLLMENT",
            "parentName": "王女士",
            "contactInfo": "13700000000",
            "studentName": "王小明",
            "studentGrade": "五年级",
        },
        class_repository=class_repository,
        registration_repository=registration_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-registration-sqlite-owned-class-001",
        actor_id="parent-003",
        now=datetime(2026, 4, 12, 15, 20, tzinfo=timezone.utc),
    )
    submit_registration(
        payload={
            "classId": other_class_id,
            "registerType": "ENROLLMENT",
            "parentName": "赵女士",
            "contactInfo": "13600000000",
            "studentName": "赵小红",
            "studentGrade": "六年级",
        },
        class_repository=class_repository,
        registration_repository=registration_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-registration-sqlite-other-class-001",
        actor_id="parent-004",
        now=datetime(2026, 4, 12, 15, 30, tzinfo=timezone.utc),
    )

    response = list_registrations(
        class_repository=class_repository,
        registration_repository=registration_repository,
        request_id="req-registration-list-sqlite-001",
        actor_id="admin-001",
        actor_roles=["INITIATOR"],
    )

    assert response["code"] == ErrorCode.OK
    assert [item["classId"] for item in response["data"]["items"]] == [owned_class_id]
    assert response["data"]["items"][0]["parentName"] == "王女士"


def test_get_registration_detail_and_update_notes_for_owned_class_initiator() -> None:
    class_repository = InMemoryClassRepository()
    registration_repository = InMemoryRegistrationRepository()
    class_id = _seed_open_class(class_repository)

    submit_registration(
        payload={
            "classId": class_id,
            "registerType": "ENROLLMENT",
            "parentName": "张女士",
            "contactInfo": "13800000000",
            "studentName": "张三",
            "studentGrade": "三年级",
            "remark": "需要靠窗座位",
        },
        class_repository=class_repository,
        registration_repository=registration_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-registration-detail-seed-001",
        actor_id="parent-001",
        now=datetime(2026, 4, 12, 15, 0, tzinfo=timezone.utc),
    )
    registration_id = registration_repository.list()[0].registration_id

    update_response = update_registration_notes(
        registration_id=registration_id,
        payload={"followUpNote": "已电话联系，待确认试课时间", "notes": "家长偏好周末上午"},
        class_repository=class_repository,
        registration_repository=registration_repository,
        request_id="req-registration-note-update-001",
        actor_id="admin-001",
        actor_roles=["INITIATOR"],
        now=datetime(2026, 4, 12, 16, 0, tzinfo=timezone.utc),
    )
    detail_response = get_registration_detail(
        registration_id=registration_id,
        class_repository=class_repository,
        registration_repository=registration_repository,
        request_id="req-registration-detail-001",
        actor_id="admin-001",
        actor_roles=["INITIATOR"],
    )

    assert update_response["code"] == ErrorCode.OK
    assert update_response["data"]["followUpNote"] == "已电话联系，待确认试课时间"
    assert update_response["data"]["notes"] == "家长偏好周末上午"
    assert detail_response == {
        "requestId": "req-registration-detail-001",
        "code": ErrorCode.OK,
        "data": {
            "registrationId": registration_id,
            "classId": class_id,
            "className": "周末拼课",
            "registerType": "ENROLLMENT",
            "registrationStatus": "SUBMITTED",
            "parentName": "张女士",
            "studentName": "张三",
            "studentGrade": "三年级",
            "contactInfo": "13800000000",
            "remark": "需要靠窗座位",
            "followUpNote": "已电话联系，待确认试课时间",
            "notes": "家长偏好周末上午",
            "submittedAt": "2026-04-12T15:00:00+00:00",
            "updatedAt": "2026-04-12T16:00:00+00:00",
            "paymentStatus": "UNPAID",
        },
    }


def test_get_registration_detail_rejects_unowned_initiator() -> None:
    class_repository = InMemoryClassRepository()
    registration_repository = InMemoryRegistrationRepository()
    class_id = _seed_open_class(class_repository)

    submit_registration(
        payload={
            "classId": class_id,
            "registerType": "ENROLLMENT",
            "parentName": "张女士",
            "contactInfo": "13800000000",
            "studentName": "张三",
            "studentGrade": "三年级",
        },
        class_repository=class_repository,
        registration_repository=registration_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-registration-detail-seed-002",
        actor_id="parent-001",
        now=datetime(2026, 4, 12, 15, 0, tzinfo=timezone.utc),
    )
    registration_id = registration_repository.list()[0].registration_id

    response = get_registration_detail(
        registration_id=registration_id,
        class_repository=class_repository,
        registration_repository=registration_repository,
        request_id="req-registration-detail-denied-001",
        actor_id="initiator-002",
        actor_roles=["INITIATOR"],
    )

    assert response == {
        "requestId": "req-registration-detail-denied-001",
        "code": ErrorCode.PERMISSION_DENIED,
        "details": [{"field": "registrationId", "message": "registration is not accessible for current actor"}],
    }


def test_update_registration_status_marks_owned_class_registration_valid_and_preserves_counts() -> None:
    class_repository = InMemoryClassRepository()
    registration_repository = InMemoryRegistrationRepository()
    class_id = _seed_open_class(class_repository)

    submit_registration(
        payload={
            "classId": class_id,
            "registerType": "ENROLLMENT",
            "parentName": "周女士",
            "contactInfo": "13500000000",
            "studentName": "周小宇",
            "studentGrade": "二年级",
        },
        class_repository=class_repository,
        registration_repository=registration_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-registration-status-seed-001",
        actor_id="parent-010",
        now=datetime(2026, 4, 12, 15, 40, tzinfo=timezone.utc),
    )
    registration_id = registration_repository.list()[0].registration_id

    response = update_registration_status(
        registration_id=registration_id,
        payload={"registrationStatus": "VALID"},
        class_repository=class_repository,
        registration_repository=registration_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-registration-status-update-001",
        actor_id="admin-001",
        actor_roles=["INITIATOR"],
        now=datetime(2026, 4, 12, 16, 40, tzinfo=timezone.utc),
    )
    detail_response = get_registration_detail(
        registration_id=registration_id,
        class_repository=class_repository,
        registration_repository=registration_repository,
        request_id="req-registration-status-detail-001",
        actor_id="admin-001",
        actor_roles=["INITIATOR"],
    )
    persisted_class = class_repository.get(class_id)

    assert response["code"] == ErrorCode.OK
    assert response["data"]["registrationStatus"] == "VALID"
    assert detail_response["data"]["registrationStatus"] == "VALID"
    assert persisted_class is not None
    assert persisted_class.current_students == 1
    assert persisted_class.waitlist_count == 0


def test_update_registration_payment_status_marks_registration_paid() -> None:
    class_repository = InMemoryClassRepository()
    registration_repository = InMemoryRegistrationRepository()
    class_id = _seed_open_class(class_repository)

    submit_registration(
        payload={
            "classId": class_id,
            "registerType": "ENROLLMENT",
            "parentName": "张女士",
            "contactInfo": "13800000000",
            "studentName": "张三",
            "studentGrade": "三年级",
        },
        class_repository=class_repository,
        registration_repository=registration_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-registration-payment-seed-001",
        actor_id="parent-001",
        now=datetime(2026, 4, 12, 15, 0, tzinfo=timezone.utc),
    )
    registration_id = registration_repository.list()[0].registration_id

    response = update_registration_payment_status(
        registration_id=registration_id,
        payload={"paymentStatus": "PAID"},
        class_repository=class_repository,
        registration_repository=registration_repository,
        request_id="req-registration-payment-update-001",
        actor_id="admin-001",
        actor_roles=["CLASS_ADMIN"],
        now=datetime(2026, 4, 12, 16, 0, tzinfo=timezone.utc),
    )

    assert response["code"] == ErrorCode.OK
    assert response["data"]["paymentStatus"] == "PAID"


def test_update_registration_status_rejects_unowned_initiator() -> None:
    class_repository = InMemoryClassRepository()
    registration_repository = InMemoryRegistrationRepository()
    class_id = _seed_open_class(class_repository)

    submit_registration(
        payload={
            "classId": class_id,
            "registerType": "ENROLLMENT",
            "parentName": "吴女士",
            "contactInfo": "13400000000",
            "studentName": "吴小乐",
            "studentGrade": "一年级",
        },
        class_repository=class_repository,
        registration_repository=registration_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-registration-status-seed-002",
        actor_id="parent-011",
        now=datetime(2026, 4, 12, 15, 50, tzinfo=timezone.utc),
    )
    registration_id = registration_repository.list()[0].registration_id

    response = update_registration_status(
        registration_id=registration_id,
        payload={"registrationStatus": "INVALID"},
        class_repository=class_repository,
        registration_repository=registration_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-registration-status-denied-001",
        actor_id="initiator-002",
        actor_roles=["INITIATOR"],
        now=datetime(2026, 4, 12, 16, 50, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-registration-status-denied-001",
        "code": ErrorCode.PERMISSION_DENIED,
        "details": [{"field": "registrationId", "message": "registration is not accessible for current actor"}],
    }


def test_update_registration_status_rejects_unknown_status_value() -> None:
    class_repository = InMemoryClassRepository()
    registration_repository = InMemoryRegistrationRepository()
    class_id = _seed_open_class(class_repository)

    submit_registration(
        payload={
            "classId": class_id,
            "registerType": "ENROLLMENT",
            "parentName": "郑女士",
            "contactInfo": "13300000000",
            "studentName": "郑小雨",
            "studentGrade": "五年级",
        },
        class_repository=class_repository,
        registration_repository=registration_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-registration-status-seed-003",
        actor_id="parent-012",
        now=datetime(2026, 4, 12, 16, 0, tzinfo=timezone.utc),
    )
    registration_id = registration_repository.list()[0].registration_id

    response = update_registration_status(
        registration_id=registration_id,
        payload={"registrationStatus": "ARCHIVED"},
        class_repository=class_repository,
        registration_repository=registration_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-registration-status-invalid-001",
        actor_id="super-admin-001",
        actor_roles=["SUPER_ADMIN"],
        now=datetime(2026, 4, 12, 17, 0, tzinfo=timezone.utc),
    )

    assert response == {
        "requestId": "req-registration-status-invalid-001",
        "code": ErrorCode.VALIDATION_INVALID_ARGUMENT,
        "details": [{"field": "registrationStatus", "message": "registrationStatus is invalid"}],
    }


def test_update_registration_status_persists_in_sqlite() -> None:
    connection = sqlite3.connect(":memory:")
    apply_schema(connection)
    class_repository = SQLiteClassRepository(connection)
    registration_repository = SQLiteRegistrationRepository(connection)
    class_id = _seed_open_class(class_repository)

    current = class_repository.get(class_id)
    assert current is not None
    class_repository.update(replace(current, status=ClassStatus.WAITLIST_OPEN))

    submit_registration(
        payload={
            "classId": class_id,
            "registerType": "WAITLIST",
            "parentName": "钱女士",
            "contactInfo": "13200000000",
            "studentGrade": "六年级",
        },
        class_repository=class_repository,
        registration_repository=registration_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-registration-status-sqlite-seed-001",
        actor_id="parent-013",
        now=datetime(2026, 4, 12, 16, 10, tzinfo=timezone.utc),
    )
    registration_id = registration_repository.list()[0].registration_id

    update_response = update_registration_status(
        registration_id=registration_id,
        payload={"registrationStatus": "CANCELLED"},
        class_repository=class_repository,
        registration_repository=registration_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-registration-status-sqlite-update-001",
        actor_id="super-admin-001",
        actor_roles=["SUPER_ADMIN"],
        now=datetime(2026, 4, 12, 17, 10, tzinfo=timezone.utc),
    )
    detail_response = get_registration_detail(
        registration_id=registration_id,
        class_repository=class_repository,
        registration_repository=registration_repository,
        request_id="req-registration-status-sqlite-detail-001",
        actor_id="super-admin-001",
        actor_roles=["SUPER_ADMIN"],
    )

    assert update_response["code"] == ErrorCode.OK
    assert update_response["data"]["registrationStatus"] == "CANCELLED"
    assert detail_response["data"]["registrationStatus"] == "CANCELLED"
    assert detail_response["data"]["updatedAt"] == "2026-04-12T17:10:00+00:00"


    connection = sqlite3.connect(":memory:")
    apply_schema(connection)
    class_repository = SQLiteClassRepository(connection)
    registration_repository = SQLiteRegistrationRepository(connection)
    class_id = _seed_open_class(class_repository)

    submit_registration(
        payload={
            "classId": class_id,
            "registerType": "ENROLLMENT",
            "parentName": "李女士",
            "contactInfo": "13900000000",
            "studentName": "李四",
            "studentGrade": "四年级",
        },
        class_repository=class_repository,
        registration_repository=registration_repository,
        audit_writer=NullAuditWriter(),
        request_id="req-registration-detail-sqlite-seed-001",
        actor_id="parent-002",
        now=datetime(2026, 4, 12, 15, 10, tzinfo=timezone.utc),
    )
    registration_id = registration_repository.list()[0].registration_id

    update_response = update_registration_notes(
        registration_id=registration_id,
        payload={"followUpNote": "已加入回访清单", "notes": "家长询问教材版本"},
        class_repository=class_repository,
        registration_repository=registration_repository,
        request_id="req-registration-note-update-sqlite-001",
        actor_id="super-admin-001",
        actor_roles=["SUPER_ADMIN"],
        now=datetime(2026, 4, 12, 16, 30, tzinfo=timezone.utc),
    )
    detail_response = get_registration_detail(
        registration_id=registration_id,
        class_repository=class_repository,
        registration_repository=registration_repository,
        request_id="req-registration-detail-sqlite-001",
        actor_id="super-admin-001",
        actor_roles=["SUPER_ADMIN"],
    )

    assert update_response["code"] == ErrorCode.OK
    assert detail_response["code"] == ErrorCode.OK
    assert detail_response["data"]["followUpNote"] == "已加入回访清单"
    assert detail_response["data"]["notes"] == "家长询问教材版本"
    assert detail_response["data"]["updatedAt"] == "2026-04-12T16:30:00+00:00"
