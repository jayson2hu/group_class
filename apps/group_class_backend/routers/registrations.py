from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Body, Depends, Response

from apps.group_class_backend.app import get_state, new_request_id
from apps.group_class_backend.common.error_codes import ErrorCode
from apps.group_class_backend.deps import ActorContext, get_actor
from apps.group_class_backend.registrations.controller import (
    get_registration_detail,
    list_registrations,
    submit_registration,
    update_registration_notes,
    update_registration_status,
)


router = APIRouter()


def _http_status(result: dict[str, Any], fallback: int = 400) -> int:
    code = result.get("code")
    if code == ErrorCode.OK.value:
        return 200
    if code == ErrorCode.CLASS_NOT_FOUND.value:
        return 404
    if code == ErrorCode.PERMISSION_DENIED.value:
        return 403
    if code == ErrorCode.CLASS_VERSION_CONFLICT.value:
        return 409
    return fallback


@router.post("/api/v1/public/registrations")
def public_submit_registration(
    response: Response,
    body: dict[str, Any] = Body(...),
    actor: ActorContext = Depends(get_actor),
) -> dict[str, object]:
    state = get_state()
    result = submit_registration(
        payload=body,
        class_repository=state.class_repository,
        registration_repository=state.registration_repository,
        audit_writer=state.audit_writer,
        request_id=new_request_id(),
        actor_id=actor.actor_id,
        now=datetime.now(timezone.utc),
    )
    response.status_code = 200 if result.get("code") == ErrorCode.OK.value else 400
    return result


@router.get("/api/v1/admin/registrations")
def admin_list_registrations(
    response: Response,
    actor: ActorContext = Depends(get_actor),
) -> dict[str, object]:
    state = get_state()
    result = list_registrations(
        class_repository=state.class_repository,
        registration_repository=state.registration_repository,
        request_id=new_request_id(),
        actor_id=actor.actor_id,
        actor_roles=actor.actor_roles,
    )
    response.status_code = _http_status(result)
    return result


@router.get("/api/v1/admin/registrations/{registration_id}")
def admin_get_registration_detail(
    registration_id: str,
    response: Response,
    actor: ActorContext = Depends(get_actor),
) -> dict[str, object]:
    state = get_state()
    result = get_registration_detail(
        registration_id=registration_id,
        class_repository=state.class_repository,
        registration_repository=state.registration_repository,
        request_id=new_request_id(),
        actor_id=actor.actor_id,
        actor_roles=actor.actor_roles,
    )
    response.status_code = _http_status(result)
    return result


@router.post("/api/v1/admin/registrations/{registration_id}/notes")
def admin_update_registration_notes(
    registration_id: str,
    response: Response,
    body: dict[str, Any] = Body(...),
    actor: ActorContext = Depends(get_actor),
) -> dict[str, object]:
    state = get_state()
    result = update_registration_notes(
        registration_id=registration_id,
        payload=body,
        class_repository=state.class_repository,
        registration_repository=state.registration_repository,
        request_id=new_request_id(),
        actor_id=actor.actor_id,
        actor_roles=actor.actor_roles,
        now=datetime.now(timezone.utc),
    )
    response.status_code = _http_status(result)
    return result


@router.post("/api/v1/admin/registrations/{registration_id}/status")
def admin_update_registration_status(
    registration_id: str,
    response: Response,
    body: dict[str, Any] = Body(...),
    actor: ActorContext = Depends(get_actor),
) -> dict[str, object]:
    state = get_state()
    result = update_registration_status(
        registration_id=registration_id,
        payload=body,
        class_repository=state.class_repository,
        registration_repository=state.registration_repository,
        audit_writer=state.audit_writer,
        request_id=new_request_id(),
        actor_id=actor.actor_id,
        actor_roles=actor.actor_roles,
        now=datetime.now(timezone.utc),
    )
    response.status_code = _http_status(result)
    return result
