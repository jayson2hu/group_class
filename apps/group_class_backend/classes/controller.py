from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from typing import Protocol

from apps.group_class_backend.audit.interface import AuditEvent, AuditWriter
from apps.group_class_backend.classes.repository import InMemoryClassRepository
from apps.group_class_backend.common.enums import ClassStatus, default_actions_for_status
from apps.group_class_backend.common.error_codes import ErrorCode
from apps.group_class_backend.common.responses import error_response, success_response
from apps.group_class_backend.models.class_template import ClassTemplate
from apps.group_class_backend.models.group_class import GroupClass


_ADMIN_REVIEW_ROLES = {"CLASS_ADMIN", "SUPER_ADMIN"}
_CANCELLABLE_STATUSES = {
    ClassStatus.OPEN_FOR_ENROLLMENT,
    ClassStatus.ALMOST_CONFIRMED,
    ClassStatus.CONFIRMED,
    ClassStatus.FULL,
    ClassStatus.WAITLIST_OPEN,
    ClassStatus.IN_PROGRESS,
}

_REVIEW_REQUIRED_FIELDS: dict[str, str] = {
    "className": "class_name",
    "priceAmount": "price_amount",
    "minStudents": "min_students",
    "maxStudents": "max_students",
    "scheduleSummary": "schedule_summary",
    "targetAudience": "target_audience",
    "courseGoal": "course_goal",
    "groupRule": "group_rule",
}


class TemplateRepository(Protocol):
    def get(self, template_id: str) -> ClassTemplate | None: ...


class ClassLookupRepository(Protocol):
    def get(self, class_id: str) -> GroupClass | None: ...


_MUTABLE_FIELD_MAP: dict[str, str] = {
    "className": "class_name",
    "templateId": "template_id",
    "classType": "class_type",
    "priceAmount": "price_amount",
    "depositAmount": "deposit_amount",
    "minStudents": "min_students",
    "maxStudents": "max_students",
    "courseSubtitle": "course_subtitle",
    "openingLevel": "opening_level",
    "levelMarker": "level_marker",
    "displayColor": "display_color",
    "wechatContact": "wechat_contact",
    "phoneContact": "phone_contact",
    "coverImageUrl": "cover_image_url",
    "highlights": "highlights",
    "ownerId": "owner_id",
    "targetAudience": "target_audience",
    "unsuitableAudience": "unsuitable_audience",
    "courseGoal": "course_goal",
    "scheduleSummary": "schedule_summary",
    "sessionCount": "session_count",
    "groupRule": "group_rule",
    "absenceRule": "absence_rule",
    "waitlistRule": "waitlist_rule",
    "failureRule": "failure_rule",
    "faqSummary": "faq_summary",
    "startDate": "start_date",
    "endDate": "end_date",
    "signupDeadline": "signup_deadline",
}

_COPYABLE_CREATE_FIELDS: dict[str, str] = {
    "className": "class_name",
    "templateId": "template_id",
    "classType": "class_type",
    "priceAmount": "price_amount",
    "depositAmount": "deposit_amount",
    "minStudents": "min_students",
    "maxStudents": "max_students",
    "courseSubtitle": "course_subtitle",
    "openingLevel": "opening_level",
    "levelMarker": "level_marker",
    "displayColor": "display_color",
    "wechatContact": "wechat_contact",
    "phoneContact": "phone_contact",
    "coverImageUrl": "cover_image_url",
    "highlights": "highlights",
    "ownerId": "owner_id",
    "targetAudience": "target_audience",
    "unsuitableAudience": "unsuitable_audience",
    "courseGoal": "course_goal",
    "scheduleSummary": "schedule_summary",
    "sessionCount": "session_count",
    "groupRule": "group_rule",
    "absenceRule": "absence_rule",
    "waitlistRule": "waitlist_rule",
    "failureRule": "failure_rule",
    "faqSummary": "faq_summary",
    "startDate": "start_date",
    "endDate": "end_date",
    "signupDeadline": "signup_deadline",
}

_LIST_ITEM_FIELDS = (
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
)

_PUBLIC_LIST_ITEM_FIELDS = (
    "classId",
    "className",
    "status",
    "statusLabel",
    "classType",
    "coverImageUrl",
    "highlights",
    "priceAmount",
    "openingLevel",
    "levelMarker",
    "displayColor",
    "currentStudents",
    "minStudents",
    "maxStudents",
    "waitlistCount",
    "remainingSeats",
    "progressText",
    "primaryAction",
    "primaryActionLabel",
    "coverImageUrl",
    "highlights",
    "updatedAt",
)

_PUBLIC_VISIBLE_STATUSES = {
    ClassStatus.OPEN_FOR_ENROLLMENT,
    ClassStatus.ALMOST_CONFIRMED,
    ClassStatus.CONFIRMED,
    ClassStatus.FULL,
    ClassStatus.WAITLIST_OPEN,
    ClassStatus.IN_PROGRESS,
}

_PUBLIC_LIST_OPTIONAL_FIELDS = (
    "wechatContact",
    "phoneContact",
)

_ENROLLMENT_ACCEPTING_STATUSES = {
    ClassStatus.OPEN_FOR_ENROLLMENT,
    ClassStatus.ALMOST_CONFIRMED,
    ClassStatus.CONFIRMED,
    ClassStatus.FULL,
    ClassStatus.WAITLIST_OPEN,
}

_STATUS_LABELS: dict[ClassStatus, str] = {
    ClassStatus.OPEN_FOR_ENROLLMENT: "报名中",
    ClassStatus.ALMOST_CONFIRMED: "即将成班",
    ClassStatus.CONFIRMED: "已成班",
    ClassStatus.FULL: "已满员",
    ClassStatus.WAITLIST_OPEN: "候补中",
    ClassStatus.IN_PROGRESS: "进行中",
    ClassStatus.CANCELLED: "已取消",
}


def _serialize_class(group_class: GroupClass) -> dict[str, object]:
    return {
        "classId": group_class.class_id,
        "version": group_class.version,
        "creatorId": group_class.creator_id,
        "className": group_class.class_name,
        "templateId": group_class.template_id,
        "status": group_class.status.value,
        "reviewerId": group_class.reviewer_id,
        "classType": group_class.class_type,
        "priceAmount": group_class.price_amount,
        "depositAmount": group_class.deposit_amount,
        "minStudents": group_class.min_students,
        "maxStudents": group_class.max_students,
        "currentStudents": group_class.current_students,
        "waitlistCount": group_class.waitlist_count,
        "courseSubtitle": group_class.course_subtitle,
        "openingLevel": group_class.opening_level,
        "levelMarker": group_class.level_marker,
        "displayColor": group_class.display_color,
        "wechatContact": group_class.wechat_contact,
        "phoneContact": group_class.phone_contact,
        "coverImageUrl": group_class.cover_image_url,
        "highlights": group_class.highlights,
        "ownerId": group_class.owner_id,
        "targetAudience": group_class.target_audience,
        "unsuitableAudience": group_class.unsuitable_audience,
        "courseGoal": group_class.course_goal,
        "scheduleSummary": group_class.schedule_summary,
        "sessionCount": group_class.session_count,
        "groupRule": group_class.group_rule,
        "absenceRule": group_class.absence_rule,
        "waitlistRule": group_class.waitlist_rule,
        "failureRule": group_class.failure_rule,
        "faqSummary": group_class.faq_summary,
        "startDate": group_class.start_date.isoformat() if group_class.start_date else None,
        "endDate": group_class.end_date.isoformat() if group_class.end_date else None,
        "signupDeadline": group_class.signup_deadline.isoformat() if group_class.signup_deadline else None,
        "actions": [action.value for action in default_actions_for_status(group_class.status)],
        "createdAt": group_class.created_at.isoformat(),
        "updatedAt": group_class.updated_at.isoformat(),
    }


def _class_response_with_review_rejection(data: dict[str, object], payload: dict[str, object]) -> dict[str, object]:
    reason_code = str(payload.get("reasonCode") or "").strip()
    reason_text = str(payload.get("reasonText") or "").strip()
    if reason_code or reason_text:
        data["reviewRejection"] = {
            "reasonCode": reason_code or "OTHER",
            "reasonText": reason_text,
        }
    return data



def _status_label(status: ClassStatus) -> str:
    return _STATUS_LABELS.get(status, status.value)



def _remaining_seats(group_class: GroupClass) -> int | None:
    if group_class.max_students is None:
        return None
    return max(group_class.max_students - group_class.current_students, 0)



def _progress_text(group_class: GroupClass) -> str | None:
    if group_class.status == ClassStatus.FULL:
        return "已满员，可加入候补"
    if group_class.min_students is not None and group_class.current_students < group_class.min_students:
        missing = group_class.min_students - group_class.current_students
        return f"还差 {missing} 人成班"
    if group_class.status == ClassStatus.WAITLIST_OPEN:
        return "名额已满，可加入候补"
    if group_class.status == ClassStatus.IN_PROGRESS:
        return "课程进行中"
    return None



def _primary_action(group_class: GroupClass) -> tuple[str, str]:
    if group_class.status in {
        ClassStatus.OPEN_FOR_ENROLLMENT,
        ClassStatus.ALMOST_CONFIRMED,
        ClassStatus.CONFIRMED,
    }:
        return "enroll", "立即报名"
    if group_class.status in {ClassStatus.FULL, ClassStatus.WAITLIST_OPEN}:
        return "join_waitlist", "加入候补"
    return "view", "查看详情"



def _serialize_public_class(group_class: GroupClass, viewer_scope: str = "visitor") -> dict[str, object]:
    primary_action, primary_action_label = _primary_action(group_class)
    data = {
        "classId": group_class.class_id,
        "className": group_class.class_name,
        "status": group_class.status.value,
        "statusLabel": _status_label(group_class.status),
        "classType": group_class.class_type,
        "priceAmount": group_class.price_amount,
        "openingLevel": group_class.opening_level,
        "levelMarker": group_class.level_marker,
        "displayColor": group_class.display_color,
        "currentStudents": group_class.current_students,
        "minStudents": group_class.min_students,
        "maxStudents": group_class.max_students,
        "waitlistCount": group_class.waitlist_count,
        "remainingSeats": _remaining_seats(group_class),
        "progressText": _progress_text(group_class),
        "primaryAction": primary_action,
        "primaryActionLabel": primary_action_label,
        "isWaitlistAvailable": group_class.status in {ClassStatus.FULL, ClassStatus.WAITLIST_OPEN},
        "courseSubtitle": group_class.course_subtitle,
        "coverImageUrl": group_class.cover_image_url,
        "highlights": group_class.highlights,
        "ownerId": group_class.owner_id,
        "targetAudience": group_class.target_audience,
        "unsuitableAudience": group_class.unsuitable_audience,
        "courseGoal": group_class.course_goal,
        "scheduleSummary": group_class.schedule_summary,
        "sessionCount": group_class.session_count,
        "groupRule": group_class.group_rule,
        "absenceRule": group_class.absence_rule,
        "waitlistRule": group_class.waitlist_rule,
        "failureRule": group_class.failure_rule,
        "faqSummary": group_class.faq_summary,
        "actions": ["view"],
        "updatedAt": group_class.updated_at.isoformat(),
    }
    if viewer_scope in {"user", "backoffice"}:
        data["wechatContact"] = group_class.wechat_contact
    if viewer_scope == "backoffice":
        data["phoneContact"] = group_class.phone_contact
    return data


def _is_signup_expired(group_class: GroupClass, now: datetime | None = None) -> bool:
    if group_class.signup_deadline is None or group_class.status not in _ENROLLMENT_ACCEPTING_STATUSES:
        return False
    current = now or datetime.now(timezone.utc)
    deadline = group_class.signup_deadline
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    return current > deadline


def _similar_public_classes(repository: InMemoryClassRepository, current: GroupClass, limit: int = 3) -> list[dict[str, object]]:
    candidates = [
        item
        for item in repository.list()
        if item.class_id != current.class_id and item.status in _PUBLIC_VISIBLE_STATUSES
    ]
    candidates.sort(
        key=lambda item: (
            item.class_type != current.class_type,
            item.status in {ClassStatus.FULL, ClassStatus.WAITLIST_OPEN},
            item.updated_at,
        )
    )
    return [_serialize_public_class(item) for item in candidates[:limit]]



def _validation_error(request_id: str, message: str) -> dict[str, object]:
    field = "className" if "className or templateId" in message else message.split()[0]
    return error_response(
        request_id=request_id,
        code=ErrorCode.VALIDATION_INVALID_ARGUMENT,
        details=[{"field": field, "message": message}],
    )



def _not_found_error(request_id: str) -> dict[str, object]:
    return error_response(
        request_id=request_id,
        code=ErrorCode.CLASS_NOT_FOUND,
        details=[{"field": "classId", "message": "class not found"}],
    )



def _version_conflict_error(request_id: str) -> dict[str, object]:
    return error_response(
        request_id=request_id,
        code=ErrorCode.CLASS_VERSION_CONFLICT,
        details=[{"field": "version", "message": "version does not match current resource"}],
    )



def _permission_denied(request_id: str, field: str, message: str) -> dict[str, object]:
    return error_response(
        request_id=request_id,
        code=ErrorCode.PERMISSION_DENIED,
        details=[{"field": field, "message": message}],
    )



def _template_not_found_error(request_id: str) -> dict[str, object]:
    return error_response(
        request_id=request_id,
        code=ErrorCode.CLASS_NOT_FOUND,
        details=[{"field": "templateId", "message": "template not found"}],
    )



def _template_inactive_error(request_id: str) -> dict[str, object]:
    return error_response(
        request_id=request_id,
        code=ErrorCode.VALIDATION_INVALID_ARGUMENT,
        details=[{"field": "templateId", "message": "template is inactive"}],
    )


def _class_review_readiness_error(request_id: str, current: GroupClass) -> dict[str, object] | None:
    details = []
    for api_field, model_field in _REVIEW_REQUIRED_FIELDS.items():
        value = getattr(current, model_field)
        if value is None or (isinstance(value, str) and not value.strip()):
            details.append({"field": api_field, "message": f"{api_field} is required before submitting review"})
    if not details:
        return None
    return error_response(
        request_id=request_id,
        code=ErrorCode.VALIDATION_INVALID_ARGUMENT,
        details=details,
    )



def _apply_template_default(
    resolved_payload: dict[str, object], api_field: str, template_value: object
) -> None:
    current_value = resolved_payload.get(api_field)
    if current_value is None:
        resolved_payload[api_field] = template_value
        return
    if isinstance(current_value, str) and current_value == "":
        resolved_payload[api_field] = template_value



def _resolve_create_payload(
    payload: dict[str, object],
    repository: InMemoryClassRepository,
    template_repository: TemplateRepository | None,
    request_id: str,
) -> tuple[dict[str, object] | None, dict[str, object] | None]:
    resolved_payload = dict(payload)

    source_class_id = payload.get("sourceClassId")
    if source_class_id:
        source_class = repository.get(str(source_class_id))
        if source_class is None:
            return None, error_response(
                request_id=request_id,
                code=ErrorCode.CLASS_NOT_FOUND,
                details=[{"field": "sourceClassId", "message": "source class not found"}],
            )
        for api_field, attr in _COPYABLE_CREATE_FIELDS.items():
            _apply_template_default(resolved_payload, api_field, getattr(source_class, attr))

    template_id = resolved_payload.get("templateId")
    if not template_id:
        return resolved_payload, None
    if template_repository is None:
        return resolved_payload, None

    template = template_repository.get(str(template_id))
    if template is None:
        return None, _template_not_found_error(request_id)
    if not template.is_active:
        return None, _template_inactive_error(request_id)
    _apply_template_default(resolved_payload, "className", template.template_name)
    _apply_template_default(resolved_payload, "classType", template.class_type)
    _apply_template_default(resolved_payload, "priceAmount", template.default_price_amount)
    _apply_template_default(resolved_payload, "depositAmount", template.default_deposit_amount)
    _apply_template_default(resolved_payload, "minStudents", template.default_min_students)
    _apply_template_default(resolved_payload, "maxStudents", template.default_max_students)
    _apply_template_default(resolved_payload, "courseSubtitle", template.default_course_subtitle)
    _apply_template_default(resolved_payload, "targetAudience", template.default_target_audience)
    _apply_template_default(resolved_payload, "unsuitableAudience", template.default_unsuitable_audience)
    _apply_template_default(resolved_payload, "courseGoal", template.default_course_goal)
    _apply_template_default(resolved_payload, "scheduleSummary", template.default_schedule_summary)
    _apply_template_default(resolved_payload, "sessionCount", template.default_session_count)
    _apply_template_default(resolved_payload, "groupRule", template.default_group_rule)
    _apply_template_default(resolved_payload, "absenceRule", template.default_absence_rule)
    _apply_template_default(resolved_payload, "waitlistRule", template.default_waitlist_rule)
    _apply_template_default(resolved_payload, "failureRule", template.default_failure_rule)
    _apply_template_default(resolved_payload, "faqSummary", template.default_faq_summary)
    return resolved_payload, None



def _actor_has_role(actor_roles: list[str] | None, allowed_roles: set[str]) -> bool:
    if actor_roles is None:
        return False
    return bool(set(actor_roles).intersection(allowed_roles))



def _can_mutate_owned_class(current: GroupClass, actor_id: str, actor_roles: list[str] | None) -> bool:
    if actor_roles is None:
        return True
    if _actor_has_role(actor_roles, _ADMIN_REVIEW_ROLES):
        return True
    return _actor_has_role(actor_roles, {"INITIATOR"}) and current.creator_id == actor_id



def _load_class_for_mutation(
    *, class_id: str, payload: dict[str, object], repository: InMemoryClassRepository, request_id: str
) -> tuple[GroupClass | None, dict[str, object] | None]:
    current = repository.get(class_id)
    if current is None:
        return None, _not_found_error(request_id)
    if payload.get("version") != current.version:
        return None, _version_conflict_error(request_id)
    return current, None



def _validate_payload(candidate: GroupClass) -> None:
    GroupClass.create_draft(
        created_at=candidate.created_at,
        creator_id=candidate.creator_id,
        class_name=candidate.class_name,
        template_id=candidate.template_id,
        class_type=candidate.class_type,
        price_amount=candidate.price_amount,
        deposit_amount=candidate.deposit_amount,
        min_students=candidate.min_students,
        max_students=candidate.max_students,
        course_subtitle=candidate.course_subtitle,
        opening_level=candidate.opening_level,
        level_marker=candidate.level_marker,
        display_color=candidate.display_color,
        wechat_contact=candidate.wechat_contact,
        phone_contact=candidate.phone_contact,
        cover_image_url=candidate.cover_image_url,
        highlights=candidate.highlights,
        owner_id=candidate.owner_id,
        target_audience=candidate.target_audience,
        unsuitable_audience=candidate.unsuitable_audience,
        course_goal=candidate.course_goal,
        schedule_summary=candidate.schedule_summary,
        session_count=candidate.session_count,
        group_rule=candidate.group_rule,
        absence_rule=candidate.absence_rule,
        waitlist_rule=candidate.waitlist_rule,
        failure_rule=candidate.failure_rule,
        faq_summary=candidate.faq_summary,
        start_date=candidate.start_date,
        end_date=candidate.end_date,
        signup_deadline=candidate.signup_deadline,
    )



def create_class_draft(
    *,
    payload: dict[str, object],
    repository: InMemoryClassRepository,
    template_repository: TemplateRepository | None = None,
    audit_writer: AuditWriter,
    request_id: str,
    actor_id: str,
    now: datetime,
) -> dict[str, object]:
    resolved_payload, payload_error = _resolve_create_payload(
        payload,
        repository,
        template_repository,
        request_id,
    )
    if payload_error is not None:
        assert resolved_payload is None
        return payload_error

    try:
        group_class = GroupClass.create_draft(
            created_at=now,
            creator_id=actor_id,
            class_name=resolved_payload.get("className"),
            template_id=resolved_payload.get("templateId"),
            class_type=resolved_payload.get("classType"),
            price_amount=resolved_payload.get("priceAmount"),
            deposit_amount=resolved_payload.get("depositAmount"),
            min_students=resolved_payload.get("minStudents"),
            max_students=resolved_payload.get("maxStudents"),
            course_subtitle=resolved_payload.get("courseSubtitle"),
            opening_level=resolved_payload.get("openingLevel"),
            level_marker=resolved_payload.get("levelMarker"),
            display_color=resolved_payload.get("displayColor"),
            wechat_contact=resolved_payload.get("wechatContact"),
            phone_contact=resolved_payload.get("phoneContact"),
            cover_image_url=resolved_payload.get("coverImageUrl"),
            highlights=resolved_payload.get("highlights"),
            owner_id=resolved_payload.get("ownerId"),
            target_audience=resolved_payload.get("targetAudience"),
            unsuitable_audience=resolved_payload.get("unsuitableAudience"),
            course_goal=resolved_payload.get("courseGoal"),
            schedule_summary=resolved_payload.get("scheduleSummary"),
            session_count=resolved_payload.get("sessionCount"),
            group_rule=resolved_payload.get("groupRule"),
            absence_rule=resolved_payload.get("absenceRule"),
            waitlist_rule=resolved_payload.get("waitlistRule"),
            failure_rule=resolved_payload.get("failureRule"),
            faq_summary=resolved_payload.get("faqSummary"),
            start_date=resolved_payload.get("startDate"),
            end_date=resolved_payload.get("endDate"),
            signup_deadline=resolved_payload.get("signupDeadline"),
        )
    except ValueError as exc:
        return _validation_error(request_id, str(exc))

    saved = repository.save(group_class)
    audit_writer.record(
        AuditEvent(
            request_id=request_id,
            actor_id=actor_id,
            action="class.created",
            resource_type="class",
            resource_id=saved.class_id,
            metadata={"status": saved.status.value},
        )
    )
    return success_response(request_id=request_id, data=_serialize_class(saved))



def update_class_draft(
    *,
    class_id: str,
    payload: dict[str, object],
    repository: InMemoryClassRepository,
    audit_writer: AuditWriter,
    request_id: str,
    actor_id: str,
    actor_roles: list[str] | None = None,
    now: datetime,
) -> dict[str, object]:
    current, error = _load_class_for_mutation(
        class_id=class_id,
        payload=payload,
        repository=repository,
        request_id=request_id,
    )
    if error is not None:
        return error
    assert current is not None

    if not _can_mutate_owned_class(current, actor_id, actor_roles):
        return _permission_denied(request_id, "actorId", "INITIATOR can only edit classes they created")

    updates = {attr: payload[api_field] for api_field, attr in _MUTABLE_FIELD_MAP.items() if api_field in payload}
    candidate = replace(current, **updates, updated_at=now)

    try:
        _validate_payload(candidate)
    except ValueError as exc:
        return _validation_error(request_id, str(exc))

    saved = repository.update(candidate)
    audit_writer.record(
        AuditEvent(
            request_id=request_id,
            actor_id=actor_id,
            action="class.updated",
            resource_type="class",
            resource_id=saved.class_id,
            metadata={"version": saved.version},
        )
    )
    return success_response(request_id=request_id, data=_serialize_class(saved))



def submit_class_review(
    *,
    class_id: str,
    payload: dict[str, object],
    repository: InMemoryClassRepository,
    audit_writer: AuditWriter,
    request_id: str,
    actor_id: str,
    actor_roles: list[str] | None = None,
    now: datetime,
) -> dict[str, object]:
    current, error = _load_class_for_mutation(
        class_id=class_id,
        payload=payload,
        repository=repository,
        request_id=request_id,
    )
    if error is not None:
        return error
    assert current is not None

    if not _can_mutate_owned_class(current, actor_id, actor_roles):
        return _permission_denied(request_id, "actorId", "INITIATOR can only submit classes they created for review")

    if current.status not in {ClassStatus.DRAFT, ClassStatus.REJECTED}:
        return error_response(
            request_id=request_id,
            code=ErrorCode.VALIDATION_INVALID_ARGUMENT,
            details=[{"field": "status", "message": "only DRAFT or REJECTED classes can be submitted for review"}],
        )

    readiness_error = _class_review_readiness_error(request_id, current)
    if readiness_error is not None:
        return readiness_error

    candidate = replace(current, status=ClassStatus.PENDING_REVIEW, updated_at=now)
    saved = repository.update(candidate)
    audit_writer.record(
        AuditEvent(
            request_id=request_id,
            actor_id=actor_id,
            action="class.submitted_for_review",
            resource_type="class",
            resource_id=saved.class_id,
            metadata={
                "previousStatus": current.status.value,
                "status": saved.status.value,
                "version": saved.version,
            },
        )
    )
    return success_response(request_id=request_id, data=_serialize_class(saved))



def approve_class_review(
    *,
    class_id: str,
    payload: dict[str, object],
    repository: InMemoryClassRepository,
    audit_writer: AuditWriter,
    request_id: str,
    actor_id: str,
    actor_roles: list[str] | None = None,
    now: datetime,
) -> dict[str, object]:
    current, error = _load_class_for_mutation(
        class_id=class_id,
        payload=payload,
        repository=repository,
        request_id=request_id,
    )
    if error is not None:
        return error
    assert current is not None

    if current.status != ClassStatus.PENDING_REVIEW:
        return error_response(
            request_id=request_id,
            code=ErrorCode.VALIDATION_INVALID_ARGUMENT,
            details=[{"field": "status", "message": "only PENDING_REVIEW classes can be approved"}],
        )

    if not _actor_has_role(actor_roles, _ADMIN_REVIEW_ROLES):
        return _permission_denied(request_id, "actorRoles", "only CLASS_ADMIN or SUPER_ADMIN can approve class review")

    candidate = replace(current, status=ClassStatus.OPEN_FOR_ENROLLMENT, reviewer_id=actor_id, updated_at=now)
    saved = repository.update(candidate)
    audit_writer.record(
        AuditEvent(
            request_id=request_id,
            actor_id=actor_id,
            action="class.review_approved",
            resource_type="class",
            resource_id=saved.class_id,
            metadata={
                "previousStatus": current.status.value,
                "status": saved.status.value,
                "version": saved.version,
            },
        )
    )
    return success_response(request_id=request_id, data=_serialize_class(saved))



def reject_class_review(
    *,
    class_id: str,
    payload: dict[str, object],
    repository: InMemoryClassRepository,
    audit_writer: AuditWriter,
    request_id: str,
    actor_id: str,
    actor_roles: list[str] | None = None,
    now: datetime,
) -> dict[str, object]:
    current, error = _load_class_for_mutation(
        class_id=class_id,
        payload=payload,
        repository=repository,
        request_id=request_id,
    )
    if error is not None:
        return error
    assert current is not None

    if current.status != ClassStatus.PENDING_REVIEW:
        return error_response(
            request_id=request_id,
            code=ErrorCode.VALIDATION_INVALID_ARGUMENT,
            details=[{"field": "status", "message": "only PENDING_REVIEW classes can be rejected"}],
        )

    if not _actor_has_role(actor_roles, _ADMIN_REVIEW_ROLES):
        return _permission_denied(request_id, "actorRoles", "only CLASS_ADMIN or SUPER_ADMIN can reject class review")

    candidate = replace(current, status=ClassStatus.REJECTED, reviewer_id=actor_id, updated_at=now)
    saved = repository.update(candidate)
    reason_code = str(payload.get("reasonCode") or "").strip() or "OTHER"
    reason_text = str(payload.get("reasonText") or "").strip()
    audit_writer.record(
        AuditEvent(
            request_id=request_id,
            actor_id=actor_id,
            action="class.review_rejected",
            resource_type="class",
            resource_id=saved.class_id,
            metadata={
                "previousStatus": current.status.value,
                "status": saved.status.value,
                "version": saved.version,
                "reasonCode": reason_code,
                "reasonText": reason_text,
            },
        )
    )
    return success_response(request_id=request_id, data=_class_response_with_review_rejection(_serialize_class(saved), payload))


def cancel_class(
    *,
    class_id: str,
    payload: dict[str, object],
    repository: InMemoryClassRepository,
    audit_writer: AuditWriter,
    request_id: str,
    actor_id: str,
    actor_roles: list[str] | None = None,
    now: datetime,
) -> dict[str, object]:
    current, error = _load_class_for_mutation(
        class_id=class_id,
        payload=payload,
        repository=repository,
        request_id=request_id,
    )
    if error is not None:
        return error
    assert current is not None

    if current.status not in _CANCELLABLE_STATUSES:
        return error_response(
            request_id=request_id,
            code=ErrorCode.VALIDATION_INVALID_ARGUMENT,
            details=[{"field": "status", "message": "current class status cannot be cancelled"}],
        )

    if not _actor_has_role(actor_roles, _ADMIN_REVIEW_ROLES):
        return _permission_denied(request_id, "actorRoles", "only CLASS_ADMIN or SUPER_ADMIN can cancel class")

    candidate = replace(current, status=ClassStatus.CANCELLED, updated_at=now)
    saved = repository.update(candidate)
    audit_writer.record(
        AuditEvent(
            request_id=request_id,
            actor_id=actor_id,
            action="class.cancelled",
            resource_type="class",
            resource_id=saved.class_id,
            metadata={
                "previousStatus": current.status.value,
                "status": saved.status.value,
                "version": saved.version,
            },
        )
    )
    return success_response(request_id=request_id, data=_serialize_class(saved))



def get_class_detail(
    *,
    class_id: str,
    repository: InMemoryClassRepository,
    request_id: str,
    public_only: bool = False,
    viewer_scope: str = "visitor",
) -> dict[str, object]:
    group_class = repository.get(class_id)
    if group_class is None:
        return _not_found_error(request_id)
    if public_only and group_class.status not in _PUBLIC_VISIBLE_STATUSES:
        return _not_found_error(request_id)
    if public_only and _is_signup_expired(group_class):
        return _not_found_error(request_id)
    data = _serialize_public_class(group_class, viewer_scope=viewer_scope) if public_only else _serialize_class(group_class)
    if public_only:
        data["similarClasses"] = _similar_public_classes(repository, group_class)
    return success_response(request_id=request_id, data=data)



def list_classes(
    *,
    repository: InMemoryClassRepository,
    request_id: str,
    page: int,
    page_size: int,
    public_only: bool = False,
    viewer_scope: str = "visitor",
    status_filter: list[str] | None = None,
    creator_id_filter: str | None = None,
    keyword: str | None = None,
) -> dict[str, object]:
    all_items = sorted(repository.list(), key=lambda item: item.updated_at, reverse=True)
    if public_only:
        all_items = [item for item in all_items if item.status in _PUBLIC_VISIBLE_STATUSES]
        all_items = [item for item in all_items if not _is_signup_expired(item)]
    if status_filter:
        allowed_statuses = {status for status in status_filter if status}
        all_items = [item for item in all_items if item.status.value in allowed_statuses]
    if creator_id_filter:
        all_items = [item for item in all_items if item.creator_id == creator_id_filter]
    if keyword:
        normalized_keyword = keyword.strip().lower()
        if normalized_keyword:
            all_items = [item for item in all_items if normalized_keyword in (item.class_name or "").lower()]
    start = max(page - 1, 0) * page_size
    end = start + page_size
    serialized_items = []
    for group_class in all_items[start:end]:
        if public_only:
            public_item = _serialize_public_class(group_class, viewer_scope=viewer_scope)
            serialized_items.append(
                {
                    field: public_item[field]
                    for field in (*_PUBLIC_LIST_ITEM_FIELDS, *_PUBLIC_LIST_OPTIONAL_FIELDS)
                    if field in public_item
                }
            )
        else:
            full_item = _serialize_class(group_class)
            serialized_items.append({field: full_item[field] for field in _LIST_ITEM_FIELDS})

    return success_response(
        request_id=request_id,
        data={
            "page": page,
            "pageSize": page_size,
            "total": len(all_items),
            "items": serialized_items,
        },
    )
