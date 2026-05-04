from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Body, Depends, Response

from apps.group_class_backend.app import get_state, new_request_id
from apps.group_class_backend.common.error_codes import ErrorCode
from apps.group_class_backend.deps import ActorContext, get_actor
from apps.group_class_backend.templates.controller import create_template, get_template, list_templates, update_template


router = APIRouter()


def _http_status(result: dict[str, Any], fallback: int = 400) -> int:
    code = result.get("code")
    if code == ErrorCode.OK.value:
        return 200
    if code == ErrorCode.TEMPLATE_NOT_FOUND.value:
        return 404
    if code == ErrorCode.PERMISSION_DENIED.value:
        return 403
    return fallback


@router.post("/api/v1/admin/templates")
def admin_create_template(
    response: Response,
    body: dict[str, Any] = Body(...),
    actor: ActorContext = Depends(get_actor),
) -> dict[str, object]:
    result = create_template(
        payload=body,
        repository=get_state().template_repository,
        request_id=new_request_id(),
        actor_roles=actor.actor_roles,
        now=datetime.now(timezone.utc),
    )
    response.status_code = _http_status(result)
    return result


@router.get("/api/v1/admin/templates")
def admin_list_templates(
    response: Response,
    actor: ActorContext = Depends(get_actor),
) -> dict[str, object]:
    result = list_templates(
        repository=get_state().template_repository,
        request_id=new_request_id(),
        actor_roles=actor.actor_roles,
    )
    response.status_code = _http_status(result)
    return result


@router.get("/api/v1/admin/templates/{template_id}")
def admin_get_template(
    template_id: str,
    response: Response,
    actor: ActorContext = Depends(get_actor),
) -> dict[str, object]:
    result = get_template(
        template_id=template_id,
        repository=get_state().template_repository,
        request_id=new_request_id(),
        actor_roles=actor.actor_roles,
    )
    response.status_code = _http_status(result)
    return result


@router.post("/api/v1/admin/templates/{template_id}/update")
def admin_update_template(
    template_id: str,
    response: Response,
    body: dict[str, Any] = Body(...),
    actor: ActorContext = Depends(get_actor),
) -> dict[str, object]:
    result = update_template(
        template_id=template_id,
        payload=body,
        repository=get_state().template_repository,
        request_id=new_request_id(),
        actor_roles=actor.actor_roles,
        now=datetime.now(timezone.utc),
    )
    response.status_code = _http_status(result)
    return result
