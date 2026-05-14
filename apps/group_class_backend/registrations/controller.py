from __future__ import annotations

from dataclasses import replace
from uuid import uuid4

from apps.group_class_backend.audit.interface import AuditEvent, AuditWriter
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


def _serialize_result(registration: Registration, class_status: ClassStatus) -> dict[str, object]:
    if registration.registration_type == RegistrationType.ENROLLMENT:
        next_step_text = "提交成功，老师/运营将尽快联系确认"
    elif registration.registration_type == RegistrationType.WAITLIST:
        next_step_text = "已加入候补，如有空位将尽快通知你"
    else:
        next_step_text = "试听申请已提交，老师/运营将尽快联系确认"
    return {
        "registrationId": registration.registration_id,
        "registerType": registration.registration_type.value,
        "registrationStatus": registration.status.value,
        "classStatus": class_status.value,
        "nextStepText": next_step_text,
    }


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
        "parentName": registration.parent_name,
        "studentName": registration.student_name,
        "studentGrade": registration.student_grade,
        "contactInfo": registration.contact_info,
        "submittedAt": registration.submitted_at.isoformat(),
        "followUpNote": registration.follow_up_note,
        "notes": registration.notes,
    }


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


def update_my_registration(
    *,
    registration_id: str,
    payload: dict[str, object],
    class_repository: InMemoryClassRepository | SQLiteClassRepository,
    registration_repository: InMemoryRegistrationRepository | SQLiteRegistrationRepository,
    request_id: str,
    actor_id: str,
    now,
) -> dict[str, object]:
    registration = registration_repository.get(registration_id)
    if registration is None or registration.user_id != actor_id:
        return error_response(
            request_id=request_id,
            code=ErrorCode.CLASS_NOT_FOUND,
            details=[{"field": "registrationId", "message": "registration not found"}],
        )
    if registration.status == RegistrationStatus.CANCELLED:
        return error_response(
            request_id=request_id,
            code=ErrorCode.VALIDATION_INVALID_ARGUMENT,
            details=[{"field": "registrationStatus", "message": "cancelled registration cannot be edited"}],
        )
    group_class = class_repository.get(registration.class_id)
    if group_class is None:
        return error_response(
            request_id=request_id,
            code=ErrorCode.CLASS_NOT_FOUND,
            details=[{"field": "classId", "message": "class not found"}],
        )
    updated = registration_repository.update(
        replace(
            registration,
            parent_name=payload.get("parentName", registration.parent_name),
            contact_info=payload.get("contactInfo", registration.contact_info),
            student_name=payload.get("studentName", registration.student_name),
            student_grade=payload.get("studentGrade", registration.student_grade),
            english_level=payload.get("englishLevel", registration.english_level),
            remark=payload.get("remark", registration.remark),
            updated_at=now,
        )
    )
    return success_response(request_id=request_id, data=_serialize_registration_detail(updated, group_class))


def cancel_my_registration(
    *,
    registration_id: str,
    class_repository: InMemoryClassRepository | SQLiteClassRepository,
    registration_repository: InMemoryRegistrationRepository | SQLiteRegistrationRepository,
    request_id: str,
    actor_id: str,
    now,
) -> dict[str, object]:
    registration = registration_repository.get(registration_id)
    if registration is None or registration.user_id != actor_id:
        return error_response(
            request_id=request_id,
            code=ErrorCode.CLASS_NOT_FOUND,
            details=[{"field": "registrationId", "message": "registration not found"}],
        )
    group_class = class_repository.get(registration.class_id)
    if group_class is None:
        return error_response(
            request_id=request_id,
            code=ErrorCode.CLASS_NOT_FOUND,
            details=[{"field": "classId", "message": "class not found"}],
        )
    updated = registration_repository.update(
        replace(registration, status=RegistrationStatus.CANCELLED, updated_at=now)
    )
    return success_response(request_id=request_id, data=_serialize_registration_detail(updated, group_class))


def list_registrations(
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
    return success_response(request_id=request_id, data={"items": items})


def list_my_registrations(
    *,
    class_repository: InMemoryClassRepository | SQLiteClassRepository,
    registration_repository: InMemoryRegistrationRepository | SQLiteRegistrationRepository,
    request_id: str,
    actor_id: str,
) -> dict[str, object]:
    visible_classes = {group_class.class_id: group_class for group_class in class_repository.list()}
    items = [
        _serialize_registration_list_item(registration, visible_classes[registration.class_id])
        for registration in registration_repository.list()
        if registration.user_id == actor_id and registration.class_id in visible_classes
    ]
    return success_response(request_id=request_id, data={"items": items})


def get_registration_detail(
    *,
    registration_id: str,
    class_repository: InMemoryClassRepository | SQLiteClassRepository,
    registration_repository: InMemoryRegistrationRepository | SQLiteRegistrationRepository,
    request_id: str,
    actor_id: str,
    actor_roles: list[str] | None = None,
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

    return success_response(request_id=request_id, data=_serialize_registration_detail(registration, group_class))


def update_registration_notes(
    *,
    registration_id: str,
    payload: dict[str, object],
    class_repository: InMemoryClassRepository | SQLiteClassRepository,
    registration_repository: InMemoryRegistrationRepository | SQLiteRegistrationRepository,
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
        updated_class = class_repository.update(replace(group_class, current_students=group_class.current_students + 1, updated_at=now))
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
    return success_response(request_id=request_id, data=_serialize_result(registration, updated_class.status))
