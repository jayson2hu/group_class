from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Response

from apps.group_class_backend.app import get_state
from apps.group_class_backend.common.enums import ClassStatus
from apps.group_class_backend.common.error_codes import ErrorCode
from apps.group_class_backend.deps import ActorContext, get_actor
from apps.group_class_backend.models.registration import RegistrationStatus, RegistrationType


router = APIRouter()

_DASHBOARD_ROLES = {"CLASS_ADMIN", "SUPER_ADMIN", "INITIATOR"}
_NOTIFICATION_SCENARIOS = {
    "REGISTRATION_SUBMITTED": "报名已提交，运营会尽快联系确认课程安排。",
    "WAITLIST_PROMOTED": "候补已有空位，请确认是否转为正式报名。",
    "CLASS_APPROVED": "课程已审核通过，可以开始对外报名。",
    "CLASS_REJECTED": "课程审核未通过，请根据驳回原因补充后重新提交。",
}


def _http_status(result: dict[str, Any], fallback: int = 400) -> int:
    code = result.get("code")
    if code == ErrorCode.OK.value:
        return 200
    if code == ErrorCode.PERMISSION_DENIED.value:
        return 403
    return fallback


def _can_view_dashboard(actor_roles: list[str]) -> bool:
    return bool(set(actor_roles).intersection(_DASHBOARD_ROLES))


def _notification_preview(payload: dict[str, object]) -> dict[str, object]:
    scenario = str(payload.get("scenario") or "").strip()
    target = str(payload.get("target") or "").strip()
    if scenario not in _NOTIFICATION_SCENARIOS:
        return {
            "code": ErrorCode.VALIDATION_INVALID_ARGUMENT.value,
            "details": [{"field": "scenario", "message": "notification scenario is invalid"}],
        }
    if not target:
        return {
            "code": ErrorCode.VALIDATION_INVALID_ARGUMENT.value,
            "details": [{"field": "target", "message": "notification target is required"}],
        }
    message = str(payload.get("message") or "").strip() or _NOTIFICATION_SCENARIOS[scenario]
    return {
        "code": ErrorCode.OK.value,
        "data": {
            "scenario": scenario,
            "target": target,
            "channel": str(payload.get("channel") or "MANUAL"),
            "message": message,
            "providerStatus": "DRY_RUN",
        },
    }


@router.get("/api/v1/admin/dashboard")
def admin_dashboard(response: Response, actor: ActorContext = Depends(get_actor)) -> dict[str, object]:
    if not _can_view_dashboard(actor.actor_roles):
        result = {
            "code": ErrorCode.PERMISSION_DENIED.value,
            "details": [{"field": "actorRoles", "message": "only CLASS_ADMIN, SUPER_ADMIN, or INITIATOR can view dashboard"}],
        }
        response.status_code = _http_status(result)
        return result

    state = get_state()
    classes = state.class_repository.list()
    registrations = state.registration_repository.list()
    published_statuses = {
        ClassStatus.OPEN_FOR_ENROLLMENT,
        ClassStatus.ALMOST_CONFIRMED,
        ClassStatus.CONFIRMED,
        ClassStatus.FULL,
        ClassStatus.WAITLIST_OPEN,
        ClassStatus.IN_PROGRESS,
    }
    result = {
        "code": ErrorCode.OK.value,
        "data": {
            "classCount": len(classes),
            "publishedClassCount": sum(1 for item in classes if item.status in published_statuses),
            "pendingReviewCount": sum(1 for item in classes if item.status == ClassStatus.PENDING_REVIEW),
            "openEnrollmentCount": sum(1 for item in classes if item.status == ClassStatus.OPEN_FOR_ENROLLMENT),
            "registrationCount": len(registrations),
            "submittedRegistrationCount": sum(1 for item in registrations if item.status == RegistrationStatus.SUBMITTED),
            "waitlistedRegistrationCount": sum(1 for item in registrations if item.status == RegistrationStatus.WAITLISTED),
            "waitlistIntentCount": sum(1 for item in registrations if item.registration_type == RegistrationType.WAITLIST),
            "totalCurrentStudents": sum(item.current_students for item in classes),
            "totalWaitlistCount": sum(item.waitlist_count for item in classes),
        },
    }
    response.status_code = _http_status(result)
    return result


@router.post("/api/v1/admin/notifications/preview")
def admin_notification_preview(
    payload: dict[str, object],
    response: Response,
    actor: ActorContext = Depends(get_actor),
) -> dict[str, object]:
    if not _can_view_dashboard(actor.actor_roles):
        result = {
            "code": ErrorCode.PERMISSION_DENIED.value,
            "details": [{"field": "actorRoles", "message": "only CLASS_ADMIN, SUPER_ADMIN, or INITIATOR can preview notifications"}],
        }
        response.status_code = _http_status(result)
        return result
    result = _notification_preview(payload)
    response.status_code = _http_status(result)
    return result
