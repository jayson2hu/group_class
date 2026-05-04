from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Any
from uuid import uuid4

from apps.group_class_backend.common.error_codes import ErrorCode
from apps.group_class_backend.common.responses import error_response, success_response
from apps.group_class_backend.models.class_template import ClassTemplate
from apps.group_class_backend.templates.repository import InMemoryTemplateRepository, SQLiteTemplateRepository


_ADMIN_ROLES = {"CLASS_ADMIN", "SUPER_ADMIN"}

_FIELD_MAP = {
    "templateName": "template_name",
    "classType": "class_type",
    "defaultPriceAmount": "default_price_amount",
    "defaultDepositAmount": "default_deposit_amount",
    "defaultMinStudents": "default_min_students",
    "defaultMaxStudents": "default_max_students",
    "defaultCourseSubtitle": "default_course_subtitle",
    "defaultTargetAudience": "default_target_audience",
    "defaultUnsuitableAudience": "default_unsuitable_audience",
    "defaultCourseGoal": "default_course_goal",
    "defaultScheduleSummary": "default_schedule_summary",
    "defaultSessionCount": "default_session_count",
    "defaultGroupRule": "default_group_rule",
    "defaultAbsenceRule": "default_absence_rule",
    "defaultWaitlistRule": "default_waitlist_rule",
    "defaultFailureRule": "default_failure_rule",
    "defaultFaqSummary": "default_faq_summary",
    "isActive": "is_active",
}


TemplateRepository = InMemoryTemplateRepository | SQLiteTemplateRepository


def _has_admin_role(actor_roles: list[str] | None) -> bool:
    return bool(set(actor_roles or []) & _ADMIN_ROLES)


def _permission_error(request_id: str) -> dict[str, object]:
    return error_response(
        request_id=request_id,
        code=ErrorCode.PERMISSION_DENIED,
        details=[{"field": "actorRoles", "message": "only CLASS_ADMIN or SUPER_ADMIN can manage templates"}],
    )


def _template_not_found_error(request_id: str, template_id: str) -> dict[str, object]:
    return error_response(
        request_id=request_id,
        code=ErrorCode.TEMPLATE_NOT_FOUND,
        details=[{"field": "templateId", "message": f"template {template_id} not found"}],
    )


def _validation_error(request_id: str, field: str, message: str) -> dict[str, object]:
    return error_response(
        request_id=request_id,
        code=ErrorCode.VALIDATION_INVALID_ARGUMENT,
        details=[{"field": field, "message": message}],
    )


def _normalize_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_payload(payload: dict[str, object], request_id: str, *, require_name: bool) -> tuple[dict[str, object], dict[str, object] | None]:
    result: dict[str, object] = {}
    for api_field, attr in _FIELD_MAP.items():
        if api_field not in payload:
            continue
        value = payload[api_field]
        if attr.startswith("default_") and attr.endswith(("students", "count")) and value is not None:
            value = int(value)
        if attr in {"default_price_amount", "default_deposit_amount"} and value is not None:
            value = float(value)
        if attr in {"template_name", "class_type"} or attr.startswith("default_") and attr not in {
            "default_price_amount",
            "default_deposit_amount",
            "default_min_students",
            "default_max_students",
            "default_session_count",
        }:
            value = _normalize_text(value)
        if attr == "is_active" and value is not None:
            value = bool(value)
        result[attr] = value

    if require_name and not result.get("template_name"):
        return result, _validation_error(request_id, "templateName", "templateName is required")
    min_students = result.get("default_min_students")
    max_students = result.get("default_max_students")
    session_count = result.get("default_session_count")
    price_amount = result.get("default_price_amount")
    deposit_amount = result.get("default_deposit_amount")
    if min_students is not None and int(min_students) <= 0:
        return result, _validation_error(request_id, "defaultMinStudents", "defaultMinStudents must be greater than 0")
    if session_count is not None and int(session_count) <= 0:
        return result, _validation_error(request_id, "defaultSessionCount", "defaultSessionCount must be greater than 0")
    if min_students is not None and max_students is not None and int(max_students) < int(min_students):
        return result, _validation_error(
            request_id, "defaultMaxStudents", "defaultMaxStudents must be greater than or equal to defaultMinStudents"
        )
    if price_amount is not None and deposit_amount is not None and float(deposit_amount) > float(price_amount):
        return result, _validation_error(
            request_id, "defaultDepositAmount", "defaultDepositAmount must be less than or equal to defaultPriceAmount"
        )
    return result, None


def _serialize_template(template: ClassTemplate) -> dict[str, object]:
    return {
        "templateId": template.template_id,
        "templateName": template.template_name,
        "classType": template.class_type,
        "defaultPriceAmount": template.default_price_amount,
        "defaultDepositAmount": template.default_deposit_amount,
        "defaultMinStudents": template.default_min_students,
        "defaultMaxStudents": template.default_max_students,
        "defaultCourseSubtitle": template.default_course_subtitle,
        "defaultTargetAudience": template.default_target_audience,
        "defaultUnsuitableAudience": template.default_unsuitable_audience,
        "defaultCourseGoal": template.default_course_goal,
        "defaultScheduleSummary": template.default_schedule_summary,
        "defaultSessionCount": template.default_session_count,
        "defaultGroupRule": template.default_group_rule,
        "defaultAbsenceRule": template.default_absence_rule,
        "defaultWaitlistRule": template.default_waitlist_rule,
        "defaultFailureRule": template.default_failure_rule,
        "defaultFaqSummary": template.default_faq_summary,
        "isActive": template.is_active,
        "createdAt": template.created_at.isoformat() if template.created_at else None,
        "updatedAt": template.updated_at.isoformat() if template.updated_at else None,
    }


def create_template(
    *,
    payload: dict[str, object],
    repository: TemplateRepository,
    request_id: str,
    actor_roles: list[str] | None,
    now: datetime,
) -> dict[str, object]:
    if not _has_admin_role(actor_roles):
        return _permission_error(request_id)
    normalized, error = _normalize_payload(payload, request_id, require_name=True)
    if error is not None:
        return error
    template = ClassTemplate(
        template_id=f"tpl-{uuid4().hex[:12]}",
        template_name=str(normalized["template_name"]),
        class_type=normalized.get("class_type"),  # type: ignore[arg-type]
        default_price_amount=normalized.get("default_price_amount"),  # type: ignore[arg-type]
        default_deposit_amount=normalized.get("default_deposit_amount"),  # type: ignore[arg-type]
        default_min_students=normalized.get("default_min_students"),  # type: ignore[arg-type]
        default_max_students=normalized.get("default_max_students"),  # type: ignore[arg-type]
        default_course_subtitle=normalized.get("default_course_subtitle"),  # type: ignore[arg-type]
        default_target_audience=normalized.get("default_target_audience"),  # type: ignore[arg-type]
        default_unsuitable_audience=normalized.get("default_unsuitable_audience"),  # type: ignore[arg-type]
        default_course_goal=normalized.get("default_course_goal"),  # type: ignore[arg-type]
        default_schedule_summary=normalized.get("default_schedule_summary"),  # type: ignore[arg-type]
        default_session_count=normalized.get("default_session_count"),  # type: ignore[arg-type]
        default_group_rule=normalized.get("default_group_rule"),  # type: ignore[arg-type]
        default_absence_rule=normalized.get("default_absence_rule"),  # type: ignore[arg-type]
        default_waitlist_rule=normalized.get("default_waitlist_rule"),  # type: ignore[arg-type]
        default_failure_rule=normalized.get("default_failure_rule"),  # type: ignore[arg-type]
        default_faq_summary=normalized.get("default_faq_summary"),  # type: ignore[arg-type]
        is_active=bool(normalized.get("is_active", True)),
        created_at=now,
        updated_at=now,
    )
    return success_response(request_id=request_id, data=_serialize_template(repository.save(template)))


def update_template(
    *,
    template_id: str,
    payload: dict[str, object],
    repository: TemplateRepository,
    request_id: str,
    actor_roles: list[str] | None,
    now: datetime,
) -> dict[str, object]:
    if not _has_admin_role(actor_roles):
        return _permission_error(request_id)
    current = repository.get(template_id)
    if current is None:
        return _template_not_found_error(request_id, template_id)
    normalized, error = _normalize_payload(payload, request_id, require_name=False)
    if error is not None:
        return error
    updated_values: dict[str, Any] = {**normalized, "updated_at": now}
    updated = replace(current, **updated_values)
    return success_response(request_id=request_id, data=_serialize_template(repository.update(updated)))


def get_template(
    *,
    template_id: str,
    repository: TemplateRepository,
    request_id: str,
    actor_roles: list[str] | None,
) -> dict[str, object]:
    if not _has_admin_role(actor_roles):
        return _permission_error(request_id)
    template = repository.get(template_id)
    if template is None:
        return _template_not_found_error(request_id, template_id)
    return success_response(request_id=request_id, data=_serialize_template(template))


def list_templates(
    *,
    repository: TemplateRepository,
    request_id: str,
    actor_roles: list[str] | None,
) -> dict[str, object]:
    if not _has_admin_role(actor_roles):
        return _permission_error(request_id)
    items = sorted(repository.list(), key=lambda item: item.updated_at or datetime.min, reverse=True)
    return success_response(request_id=request_id, data={"items": [_serialize_template(item) for item in items]})
