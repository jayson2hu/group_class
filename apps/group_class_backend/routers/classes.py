from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Body, Depends, Response

from apps.group_class_backend.app import get_state, new_request_id
from apps.group_class_backend.classes.controller import (
    approve_class_review,
    create_class_draft,
    get_class_detail,
    list_classes,
    reject_class_review,
    submit_class_review,
    update_class_draft,
)
from apps.group_class_backend.common.error_codes import ErrorCode
from apps.group_class_backend.deps import ActorContext, get_actor


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


@router.get("/api/v1/public/classes")
def public_list_classes(response: Response, page: int = 1, page_size: int = 20) -> dict[str, object]:
    state = get_state()
    result = list_classes(
        repository=state.class_repository,
        request_id=new_request_id(),
        page=page,
        page_size=min(page_size, 100),
        public_only=True,
    )
    response.status_code = _http_status(result)
    return result


@router.get("/api/v1/public/classes/{class_id}")
def public_get_class_detail(class_id: str, response: Response) -> dict[str, object]:
    state = get_state()
    result = get_class_detail(
        class_id=class_id,
        repository=state.class_repository,
        request_id=new_request_id(),
        public_only=True,
    )
    response.status_code = _http_status(result)
    return result


@router.get("/api/v1/admin/classes")
def admin_list_classes(response: Response, page: int = 1, page_size: int = 20) -> dict[str, object]:
    state = get_state()
    result = list_classes(
        repository=state.class_repository,
        request_id=new_request_id(),
        page=page,
        page_size=min(page_size, 100),
        public_only=False,
    )
    response.status_code = _http_status(result)
    return result


@router.get("/api/v1/admin/classes/{class_id}")
def admin_get_class_detail(class_id: str, response: Response) -> dict[str, object]:
    state = get_state()
    result = get_class_detail(
        class_id=class_id,
        repository=state.class_repository,
        request_id=new_request_id(),
        public_only=False,
    )
    response.status_code = _http_status(result)
    return result


@router.post("/api/v1/admin/classes")
def admin_create_class(
    response: Response,
    body: dict[str, Any] = Body(...),
    actor: ActorContext = Depends(get_actor),
) -> dict[str, object]:
    state = get_state()
    result = create_class_draft(
        payload=body,
        repository=state.class_repository,
        audit_writer=state.audit_writer,
        request_id=new_request_id(),
        actor_id=actor.actor_id,
        now=datetime.now(timezone.utc),
    )
    response.status_code = _http_status(result)
    return result


@router.post("/api/v1/admin/classes/{class_id}/update")
def admin_update_class(
    class_id: str,
    response: Response,
    body: dict[str, Any] = Body(...),
    actor: ActorContext = Depends(get_actor),
) -> dict[str, object]:
    state = get_state()
    result = update_class_draft(
        class_id=class_id,
        payload=body,
        repository=state.class_repository,
        audit_writer=state.audit_writer,
        request_id=new_request_id(),
        actor_id=actor.actor_id,
        actor_roles=actor.actor_roles,
        now=datetime.now(timezone.utc),
    )
    response.status_code = _http_status(result)
    return result


@router.post("/api/v1/admin/classes/{class_id}/submit-review")
def admin_submit_review(
    class_id: str,
    response: Response,
    body: dict[str, Any] = Body(...),
    actor: ActorContext = Depends(get_actor),
) -> dict[str, object]:
    state = get_state()
    result = submit_class_review(
        class_id=class_id,
        payload=body,
        repository=state.class_repository,
        audit_writer=state.audit_writer,
        request_id=new_request_id(),
        actor_id=actor.actor_id,
        actor_roles=actor.actor_roles,
        now=datetime.now(timezone.utc),
    )
    response.status_code = _http_status(result)
    return result


@router.post("/api/v1/admin/classes/{class_id}/approve")
def admin_approve_review(
    class_id: str,
    response: Response,
    body: dict[str, Any] = Body(...),
    actor: ActorContext = Depends(get_actor),
) -> dict[str, object]:
    state = get_state()
    result = approve_class_review(
        class_id=class_id,
        payload=body,
        repository=state.class_repository,
        audit_writer=state.audit_writer,
        request_id=new_request_id(),
        actor_id=actor.actor_id,
        actor_roles=actor.actor_roles,
        now=datetime.now(timezone.utc),
    )
    response.status_code = _http_status(result)
    return result


@router.post("/api/v1/admin/classes/{class_id}/reject")
def admin_reject_review(
    class_id: str,
    response: Response,
    body: dict[str, Any] = Body(...),
    actor: ActorContext = Depends(get_actor),
) -> dict[str, object]:
    state = get_state()
    result = reject_class_review(
        class_id=class_id,
        payload=body,
        repository=state.class_repository,
        audit_writer=state.audit_writer,
        request_id=new_request_id(),
        actor_id=actor.actor_id,
        actor_roles=actor.actor_roles,
        now=datetime.now(timezone.utc),
    )
    response.status_code = _http_status(result)
    return result
