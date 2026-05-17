from __future__ import annotations

import csv
from dataclasses import replace
from datetime import timezone
from io import StringIO
from uuid import uuid4

from apps.group_class_backend.audit.interface import AuditEvent, AuditReader, AuditWriter
from apps.group_class_backend.classes.repository import InMemoryClassRepository, SQLiteClassRepository
from apps.group_class_backend.common.enums import ClassStatus
from apps.group_class_backend.common.error_codes import ErrorCode
from apps.group_class_backend.common.responses import error_response, success_response
from apps.group_class_backend.models.group_class import GroupClass
from apps.group_class_backend.models.registration import Registration, RegistrationStatus, RegistrationType
from apps.group_class_backend.registrations.repository import InMemoryRegistrationRepository, SQLiteRegistrationRepository


_ALLOWED_CLASS_STATUSES: dict[RegistrationType, set[ClassStatus]] = {
    RegistrationType.ENROLLMENT: {
        ClassStatus.OPEN_FOR_ENROLLMENT,
        ClassStatus.ALMOST_CONFIRMED,
        ClassStatus.CONFIRMED,
    },
    RegistrationType.WAITLIST: {
        ClassStatus.FULL,
        ClassStatus.WAITLIST_OPEN,
    },
    RegistrationType.TRIAL: {
        ClassStatus.OPEN_FOR_ENROLLMENT,
        ClassStatus.ALMOST_CONFIRMED,
        ClassStatus.CONFIRMED,
        ClassStatus.IN_PROGRESS,
    },
}


_BACKOFFICE_VIEW_ROLES = {"CLASS_ADMIN", "SUPER_ADMIN", "INITIATOR"}
_ALLOWED_STATUS_UPDATE_ROLES = {"CLASS_ADMIN", "SUPER_ADMIN", "INITIATOR"}
_EDITABLE_REGISTRATION_STATUSES = {
    RegistrationStatus.SUBMITTED,
    RegistrationStatus.VALID,
    RegistrationStatus.INVALID,
    RegistrationStatus.WAITLISTED,
    RegistrationStatus.CANCELLED,
}


class _PayloadError(ValueError):
    def __init__(self, field: str, message: str, code: ErrorCode = ErrorCode.VALIDATION_INVALID_ARGUMENT) -> None:
        super().__init__(message)
        self.field = field
        self.code = code


def _parse_registration_type(value: object) -> RegistrationType:
    try:
        return RegistrationType(str(value))
    except ValueError as exc:
        raise _PayloadError("registerType", "registerType is invalid") from exc


def _parse_registration_status(value: object) -> RegistrationStatus:
    try:
        return RegistrationStatus(str(value))
    except ValueError as exc:
        raise _PayloadError("registrationStatus", "registrationStatus is invalid") from exc


def _validate_class_status(group_class_status: ClassStatus, registration_type: RegistrationType) -> None:
    if group_class_status not in _ALLOWED_CLASS_STATUSES[registration_type]:
        raise _PayloadError(
            "status",
            f"class status does not accept {registration_type.value} registration",
        )


def _validate_signup_deadline(group_class: GroupClass, now) -> None:
    if group_class.signup_deadline is None:
        return
    deadline = group_class.signup_deadline
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    current = now
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    if current > deadline:
        raise _PayloadError("signupDeadline", "class signup deadline has passed")


def _serialize_result(registration: Registration, class_status: ClassStatus, waitlist_count: int | None = None) -> dict[str, object]:
    if registration.registration_type == RegistrationType.ENROLLMENT:
        next_step_text = "提交成功，老师/运营将尽快联系确认"
    elif registration.registration_type == RegistrationType.WAITLIST:
        next_step_text = "已加入候补，如有空位将尽快通知你"
    else:
        next_step_text = "试听申请已提交，老师/运营将尽快联系确认"
    result: dict[str, object] = {
        "registrationId": registration.registration_id,
        "registerType": registration.registration_type.value,
        "registrationStatus": registration.status.value,
        "classStatus": class_status.value,
        "nextStepText": next_step_text,
    }
    if registration.registration_type == RegistrationType.WAITLIST and waitlist_count is not None:
        result["waitlistCount"] = waitlist_count
        result["waitlistPosition"] = waitlist_count
    return result


def _status_after_enrollment(group_class: GroupClass, next_current_students: int) -> ClassStatus:
    if group_class.status != ClassStatus.OPEN_FOR_ENROLLMENT or group_class.max_students is None:
        return group_class.status
    if next_current_students >= group_class.max_students:
        return ClassStatus.FULL
    if next_current_students / group_class.max_students >= 0.6:
        return ClassStatus.ALMOST_CONFIRMED
    return group_class.status


def _actor_has_any_role(actor_roles: list[str] | None, allowed_roles: set[str]) -> bool:
    if actor_roles is None:
        return False
    return bool(set(actor_roles).intersection(allowed_roles))


def _can_view_registration_class(group_class: GroupClass, actor_id: str, actor_roles: list[str] | None) -> bool:
    if _actor_has_any_role(actor_roles, {"CLASS_ADMIN", "SUPER_ADMIN"}):
        return True
    return _actor_has_any_role(actor_roles, {"INITIATOR"}) and group_class.creator_id == actor_id


def _serialize_registration_list_item(registration: Registration, group_class: GroupClass) -> dict[str, object]:
    return {
        "registrationId": registration.registration_id,
        "classId": registration.class_id,
        "className": group_class.class_name,
        "registerType": registration.registration_type.value,
        "registrationStatus": registration.status.value,
        "classStatus": group_class.status.value,
        "parentName": registration.parent_name,
        "studentName": registration.student_name,
        "studentGrade": registration.student_grade,
        "contactInfo": registration.contact_info,
        "englishLevel": registration.english_level,
        "currentStudents": group_class.current_students,
        "maxStudents": group_class.max_students,
        "waitlistCount": group_class.waitlist_count,
        "acceptSimilarRecommendation": registration.accept_similar_recommendation,
        "remark": registration.remark,
        "submittedAt": registration.submitted_at.isoformat(),
        "updatedAt": registration.updated_at.isoformat() if registration.updated_at else None,
        "followUpNote": registration.follow_up_note,
        "notes": registration.notes,
    }


def _visible_registration_items(
    *,
    class_repository: InMemoryClassRepository | SQLiteClassRepository,
    registration_repository: InMemoryRegistrationRepository | SQLiteRegistrationRepository,
    actor_id: str,
    actor_roles: list[str] | None,
) -> list[dict[str, object]]:
    visible_classes = {
        group_class.class_id: group_class
        for group_class in class_repository.list()
        if _can_view_registration_class(group_class, actor_id=actor_id, actor_roles=actor_roles)
    }
    items = [
        _serialize_registration_list_item(registration, visible_classes[registration.class_id])
        for registration in registration_repository.list()
        if registration.class_id in visible_classes
    ]
    items.sort(key=lambda item: str(item["submittedAt"]), reverse=True)
    return items


def _filter_registration_items(
    items: list[dict[str, object]],
    *,
    registration_status: str | None = None,
    register_type: str | None = None,
    keyword: str | None = None,
) -> list[dict[str, object]]:
    filtered = items
    if registration_status:
        filtered = [item for item in filtered if item["registrationStatus"] == registration_status]
    if register_type:
        filtered = [item for item in filtered if item["registerType"] == register_type]
    if keyword:
        normalized = keyword.strip().lower()
        if normalized:
            searchable_fields = ("parentName", "studentName", "className")
            filtered = [
                item
                for item in filtered
                if any(normalized in str(item.get(field) or "").lower() for field in searchable_fields)
            ]
    return filtered


def _get_accessible_registration(
    *,
    registration_id: str,
    class_repository: InMemoryClassRepository | SQLiteClassRepository,
    registration_repository: InMemoryRegistrationRepository | SQLiteRegistrationRepository,
    request_id: str,
    actor_id: str,
    actor_roles: list[str] | None,
) -> tuple[Registration | None, GroupClass | None, dict[str, object] | None]:
    if not _actor_has_any_role(actor_roles, _BACKOFFICE_VIEW_ROLES):
        return None, None, error_response(
            request_id=request_id,
            code=ErrorCode.PERMISSION_DENIED,
            details=[
                {
                    "field": "actorRoles",
                    "message": "only CLASS_ADMIN, SUPER_ADMIN, or INITIATOR can view registration data",
                }
            ],
        )

    registration = registration_repository.get(registration_id)
    if registration is None:
        return None, None, error_response(
            request_id=request_id,
            code=ErrorCode.CLASS_NOT_FOUND,
            details=[{"field": "registrationId", "message": "registration not found"}],
        )

    group_class = class_repository.get(registration.class_id)
    if group_class is None or not _can_view_registration_class(group_class, actor_id=actor_id, actor_roles=actor_roles):
        return None, None, error_response(
            request_id=request_id,
            code=ErrorCode.PERMISSION_DENIED,
            details=[{"field": "registrationId", "message": "registration is not accessible for current actor"}],
        )

    return registration, group_class, None


def _serialize_registration_detail(registration: Registration, group_class: GroupClass) -> dict[str, object]:
    return {
        "registrationId": registration.registration_id,
        "classId": registration.class_id,
        "className": group_class.class_name,
        "registerType": registration.registration_type.value,
        "registrationStatus": registration.status.value,
        "parentName": registration.parent_name,
        "studentName": registration.student_name,
        "studentGrade": registration.student_grade,
        "contactInfo": registration.contact_info,
        "remark": registration.remark,
        "followUpNote": registration.follow_up_note,
        "notes": registration.notes,
        "submittedAt": registration.submitted_at.isoformat(),
        "updatedAt": registration.updated_at.isoformat() if registration.updated_at else None,
    }


def _serialize_audit_event(event: AuditEvent) -> dict[str, object]:
    return {
        "requestId": event.request_id,
        "actorId": event.actor_id,
        "action": event.action,
        "occurredAt": event.occurred_at.isoformat(),
        "metadata": event.metadata,
    }


def _registration_operation_history(audit_reader: AuditReader | None, registration_id: str) -> list[dict[str, object]]:
    if audit_reader is None:
        return []
    events = audit_reader.list_for_resource("registration", registration_id)
    events.sort(key=lambda event: event.occurred_at)
    return [_serialize_audit_event(event) for event in events]


def list_registrations(
    *,
    class_repository: InMemoryClassRepository | SQLiteClassRepository,
    registration_repository: InMemoryRegistrationRepository | SQLiteRegistrationRepository,
    request_id: str,
    actor_id: str,
    actor_roles: list[str] | None = None,
    page: int = 1,
    page_size: int = 20,
    registration_status: str | None = None,
    register_type: str | None = None,
    keyword: str | None = None,
) -> dict[str, object]:
    if not _actor_has_any_role(actor_roles, _BACKOFFICE_VIEW_ROLES):
        return error_response(
            request_id=request_id,
            code=ErrorCode.PERMISSION_DENIED,
            details=[
                {
                    "field": "actorRoles",
                    "message": "only CLASS_ADMIN, SUPER_ADMIN, or INITIATOR can view registration data",
                }
            ],
        )

    all_items = _visible_registration_items(
        class_repository=class_repository,
        registration_repository=registration_repository,
        actor_id=actor_id,
        actor_roles=actor_roles,
    )
    filtered_items = _filter_registration_items(
        all_items,
        registration_status=registration_status,
        register_type=register_type,
        keyword=keyword,
    )
    start = max(page - 1, 0) * page_size
    end = start + page_size
    return success_response(
        request_id=request_id,
        data={
            "page": page,
            "pageSize": page_size,
            "total": len(filtered_items),
            "items": filtered_items[start:end],
        },
    )


def export_registrations_csv(
    *,
    class_repository: InMemoryClassRepository | SQLiteClassRepository,
    registration_repository: InMemoryRegistrationRepository | SQLiteRegistrationRepository,
    request_id: str,
    actor_id: str,
    actor_roles: list[str] | None = None,
) -> dict[str, object]:
    if not _actor_has_any_role(actor_roles, _BACKOFFICE_VIEW_ROLES):
        return error_response(
            request_id=request_id,
            code=ErrorCode.PERMISSION_DENIED,
            details=[
                {
                    "field": "actorRoles",
                    "message": "only CLASS_ADMIN, SUPER_ADMIN, or INITIATOR can view registration data",
                }
            ],
        )

    fieldnames = [
        "registrationId",
        "classId",
        "className",
        "registerType",
        "registrationStatus",
        "classStatus",
        "parentName",
        "studentName",
        "studentGrade",
        "contactInfo",
        "englishLevel",
        "currentStudents",
        "maxStudents",
        "waitlistCount",
        "acceptSimilarRecommendation",
        "remark",
        "submittedAt",
        "updatedAt",
        "followUpNote",
        "notes",
    ]
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(
        _visible_registration_items(
            class_repository=class_repository,
            registration_repository=registration_repository,
            actor_id=actor_id,
            actor_roles=actor_roles,
        )
    )
    return success_response(request_id=request_id, data={"csv": output.getvalue()})


def get_registration_detail(
    *,
    registration_id: str,
    class_repository: InMemoryClassRepository | SQLiteClassRepository,
    registration_repository: InMemoryRegistrationRepository | SQLiteRegistrationRepository,
    request_id: str,
    actor_id: str,
    actor_roles: list[str] | None = None,
    audit_reader: AuditReader | None = None,
) -> dict[str, object]:
    registration, group_class, error = _get_accessible_registration(
        registration_id=registration_id,
        class_repository=class_repository,
        registration_repository=registration_repository,
        request_id=request_id,
        actor_id=actor_id,
        actor_roles=actor_roles,
    )
    if error is not None:
        return error

    data = _serialize_registration_detail(registration, group_class)
    data["operationHistory"] = _registration_operation_history(audit_reader, registration.registration_id)
    return success_response(request_id=request_id, data=data)


def update_registration_notes(
    *,
    registration_id: str,
    payload: dict[str, object],
    class_repository: InMemoryClassRepository | SQLiteClassRepository,
    registration_repository: InMemoryRegistrationRepository | SQLiteRegistrationRepository,
    audit_writer: AuditWriter,
    request_id: str,
    actor_id: str,
    actor_roles: list[str] | None = None,
    now,
) -> dict[str, object]:
    registration, group_class, error = _get_accessible_registration(
        registration_id=registration_id,
        class_repository=class_repository,
        registration_repository=registration_repository,
        request_id=request_id,
        actor_id=actor_id,
        actor_roles=actor_roles,
    )
    if error is not None:
        return error

    updated_registration = registration_repository.update(
        replace(
            registration,
            follow_up_note=payload.get("followUpNote"),
            notes=payload.get("notes"),
            updated_at=now,
        )
    )
    audit_writer.record(
        AuditEvent(
            request_id=request_id,
            actor_id=actor_id,
            action="registration.notes_updated",
            resource_type="registration",
            resource_id=registration.registration_id,
            metadata={
                "classId": group_class.class_id,
                "hasFollowUpNote": bool(updated_registration.follow_up_note),
                "hasNotes": bool(updated_registration.notes),
            },
        )
    )
    return success_response(request_id=request_id, data=_serialize_registration_detail(updated_registration, group_class))


def update_registration_status(
    *,
    registration_id: str,
    payload: dict[str, object],
    class_repository: InMemoryClassRepository | SQLiteClassRepository,
    registration_repository: InMemoryRegistrationRepository | SQLiteRegistrationRepository,
    audit_writer: AuditWriter,
    request_id: str,
    actor_id: str,
    actor_roles: list[str] | None = None,
    now,
) -> dict[str, object]:
    registration, group_class, error = _get_accessible_registration(
        registration_id=registration_id,
        class_repository=class_repository,
        registration_repository=registration_repository,
        request_id=request_id,
        actor_id=actor_id,
        actor_roles=actor_roles,
    )
    if error is not None:
        return error

    if not _actor_has_any_role(actor_roles, _ALLOWED_STATUS_UPDATE_ROLES):
        return error_response(
            request_id=request_id,
            code=ErrorCode.PERMISSION_DENIED,
            details=[
                {
                    "field": "actorRoles",
                    "message": "only CLASS_ADMIN, SUPER_ADMIN, or INITIATOR can update registration status",
                }
            ],
        )

    try:
        next_status = _parse_registration_status(payload.get("registrationStatus"))
    except _PayloadError as exc:
        return error_response(
            request_id=request_id,
            code=exc.code,
            details=[{"field": exc.field, "message": str(exc)}],
        )

    if next_status not in _EDITABLE_REGISTRATION_STATUSES:
        return error_response(
            request_id=request_id,
            code=ErrorCode.VALIDATION_INVALID_ARGUMENT,
            details=[{"field": "registrationStatus", "message": "registrationStatus is invalid"}],
        )

    updated_registration = registration_repository.update(
        replace(
            registration,
            status=next_status,
            updated_at=now,
        )
    )
    audit_writer.record(
        AuditEvent(
            request_id=request_id,
            actor_id=actor_id,
            action="registration.status_updated",
            resource_type="registration",
            resource_id=registration.registration_id,
            metadata={
                "classId": group_class.class_id,
                "previousRegistrationStatus": registration.status.value,
                "registrationStatus": next_status.value,
            },
        )
    )
    return success_response(request_id=request_id, data=_serialize_registration_detail(updated_registration, group_class))


def promote_waitlist_registration(
    *,
    registration_id: str,
    class_repository: InMemoryClassRepository | SQLiteClassRepository,
    registration_repository: InMemoryRegistrationRepository | SQLiteRegistrationRepository,
    audit_writer: AuditWriter,
    request_id: str,
    actor_id: str,
    actor_roles: list[str] | None = None,
    now,
) -> dict[str, object]:
    registration, group_class, error = _get_accessible_registration(
        registration_id=registration_id,
        class_repository=class_repository,
        registration_repository=registration_repository,
        request_id=request_id,
        actor_id=actor_id,
        actor_roles=actor_roles,
    )
    if error is not None:
        return error

    if not _actor_has_any_role(actor_roles, _ALLOWED_STATUS_UPDATE_ROLES):
        return error_response(
            request_id=request_id,
            code=ErrorCode.PERMISSION_DENIED,
            details=[
                {
                    "field": "actorRoles",
                    "message": "only CLASS_ADMIN, SUPER_ADMIN, or INITIATOR can promote waitlist registrations",
                }
            ],
        )
    if registration.registration_type != RegistrationType.WAITLIST or registration.status != RegistrationStatus.WAITLISTED:
        return error_response(
            request_id=request_id,
            code=ErrorCode.VALIDATION_INVALID_ARGUMENT,
            details=[{"field": "registrationId", "message": "only WAITLISTED waitlist registrations can be promoted"}],
        )

    updated_class = class_repository.update(
        replace(
            group_class,
            current_students=group_class.current_students + 1,
            waitlist_count=max(group_class.waitlist_count - 1, 0),
            updated_at=now,
        )
    )
    updated_registration = registration_repository.update(replace(registration, status=RegistrationStatus.VALID, updated_at=now))
    audit_writer.record(
        AuditEvent(
            request_id=request_id,
            actor_id=actor_id,
            action="registration.waitlist_promoted",
            resource_type="registration",
            resource_id=registration.registration_id,
            metadata={
                "classId": group_class.class_id,
                "currentStudents": updated_class.current_students,
                "waitlistCount": updated_class.waitlist_count,
            },
        )
    )
    return success_response(request_id=request_id, data=_serialize_registration_detail(updated_registration, updated_class))


def submit_registration(
    *,
    payload: dict[str, object],
    class_repository: InMemoryClassRepository | SQLiteClassRepository,
    registration_repository: InMemoryRegistrationRepository | SQLiteRegistrationRepository,
    audit_writer: AuditWriter,
    request_id: str,
    actor_id: str,
    now,
) -> dict[str, object]:
    class_id = payload.get("classId")
    group_class = class_repository.get(str(class_id)) if class_id is not None else None
    if group_class is None:
        return error_response(
            request_id=request_id,
            code=ErrorCode.CLASS_NOT_FOUND,
            details=[{"field": "classId", "message": "class not found"}],
        )

    try:
        registration_type = _parse_registration_type(payload.get("registerType"))
        _validate_class_status(group_class.status, registration_type)
        _validate_signup_deadline(group_class, now)
        registration = Registration.create(
            registration_id=f"reg-{uuid4().hex[:12]}",
            class_id=group_class.class_id,
            user_id=actor_id,
            registration_type=registration_type,
            submitted_at=now,
            parent_name=payload.get("parentName"),
            contact_info=payload.get("contactInfo"),
            student_name=payload.get("studentName"),
            student_grade=payload.get("studentGrade"),
            english_level=payload.get("englishLevel"),
            accept_transfer=payload.get("acceptTransfer"),
            accept_waitlist=payload.get("acceptWaitlist"),
            wants_trial=payload.get("wantsTrial"),
            accept_similar_recommendation=payload.get("acceptSimilarRecommendation"),
            remark=payload.get("remark"),
            follow_up_note=payload.get("followUpNote"),
            notes=payload.get("notes"),
        )
    except _PayloadError as exc:
        return error_response(
            request_id=request_id,
            code=exc.code,
            details=[{"field": exc.field, "message": str(exc)}],
        )
    except ValueError as exc:
        field = str(exc).split()[0]
        return error_response(
            request_id=request_id,
            code=ErrorCode.VALIDATION_INVALID_ARGUMENT,
            details=[{"field": field, "message": str(exc)}],
        )

    registration_repository.save(registration)
    if registration_type == RegistrationType.WAITLIST:
        updated_class = class_repository.update(replace(group_class, waitlist_count=group_class.waitlist_count + 1, updated_at=now))
    elif registration_type == RegistrationType.ENROLLMENT:
        next_current_students = group_class.current_students + 1
        updated_class = class_repository.update(
            replace(
                group_class,
                current_students=next_current_students,
                status=_status_after_enrollment(group_class, next_current_students),
                updated_at=now,
            )
        )
    else:
        updated_class = group_class

    audit_writer.record(
        AuditEvent(
            request_id=request_id,
            actor_id=actor_id,
            action="registration.submitted",
            resource_type="registration",
            resource_id=registration.registration_id,
            metadata={
                "classId": group_class.class_id,
                "registerType": registration.registration_type.value,
                "registrationStatus": registration.status.value,
            },
        )
    )
    waitlist_count = updated_class.waitlist_count if registration_type == RegistrationType.WAITLIST else None
    return success_response(request_id=request_id, data=_serialize_result(registration, updated_class.status, waitlist_count))
