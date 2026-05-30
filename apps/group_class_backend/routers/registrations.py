from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Body, Depends, Query, Response
from fastapi.responses import PlainTextResponse

from apps.group_class_backend.app import get_state, new_request_id
from apps.group_class_backend.common.error_codes import ErrorCode
from apps.group_class_backend.deps import ActorContext, get_actor
from apps.group_class_backend.registrations.controller import (
    export_registrations_csv,
    get_registration_detail,
    list_registrations,
    promote_waitlist_registration,
    submit_registration,
    update_registration_payment_status,
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


def _effective_page_size(page_size: int, page_size_camel: int | None) -> int:
    return min(page_size_camel if page_size_camel is not None else page_size, 100)


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
    page: int = 1,
    page_size: int = 20,
    page_size_camel: int | None = Query(default=None, alias="pageSize"),
    registration_status: str | None = Query(default=None, alias="registrationStatus"),
    register_type: str | None = Query(default=None, alias="registerType"),
    keyword: str | None = None,
    actor: ActorContext = Depends(get_actor),
) -> dict[str, object]:
    state = get_state()
    result = list_registrations(
        class_repository=state.class_repository,
        registration_repository=state.registration_repository,
        request_id=new_request_id(),
        actor_id=actor.actor_id,
        actor_roles=actor.actor_roles,
        page=page,
        page_size=_effective_page_size(page_size, page_size_camel),
        registration_status=registration_status,
        register_type=register_type,
        keyword=keyword,
    )
    response.status_code = _http_status(result)
    return result


@router.get("/api/v1/admin/registrations/export")
def admin_export_registrations(
    actor: ActorContext = Depends(get_actor),
) -> PlainTextResponse:
    state = get_state()
    now = datetime.now(timezone.utc)
    result = export_registrations_csv(
        class_repository=state.class_repository,
        registration_repository=state.registration_repository,
        request_id=new_request_id(),
        actor_id=actor.actor_id,
        actor_roles=actor.actor_roles,
    )
    status_code = _http_status(result)
    if status_code != 200:
        return PlainTextResponse(str(result.get("details", result.get("code", "export failed"))), status_code=status_code)
    filename = f"registrations_{now.strftime('%Y%m%d%H%M%S')}.csv"
    return PlainTextResponse(
        str(result["data"]["csv"]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


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
        audit_reader=state.audit_writer,
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
        audit_writer=state.audit_writer,
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


@router.post("/api/v1/admin/registrations/{registration_id}/promote-from-waitlist")
def admin_promote_waitlist_registration(
    registration_id: str,
    response: Response,
    actor: ActorContext = Depends(get_actor),
) -> dict[str, object]:
    state = get_state()
    result = promote_waitlist_registration(
        registration_id=registration_id,
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


@router.post("/api/v1/admin/registrations/{registration_id}/payment-status")
def admin_update_registration_payment_status(
    registration_id: str,
    response: Response,
    body: dict[str, Any] = Body(...),
    actor: ActorContext = Depends(get_actor),
) -> dict[str, object]:
    state = get_state()
    result = update_registration_payment_status(
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
