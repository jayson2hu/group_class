from __future__ import annotations

from dataclasses import replace
from typing import Any
from uuid import uuid4

from apps.group_class_backend.auth.users import AuthUser, AuthUserRepository
from apps.group_class_backend.common.error_codes import ErrorCode
from apps.group_class_backend.common.responses import error_response, success_response


ADMIN_ROLES = {"ADMIN", "CLASS_ADMIN", "SUPER_ADMIN"}
BACKOFFICE_ROLES = ADMIN_ROLES | {"OPERATOR", "TEACHER"}
MANAGEABLE_ROLES = {"ADMIN", "CLASS_ADMIN", "OPERATOR", "TEACHER", "USER"}
OPERATOR_MANAGEABLE_ROLES = {"TEACHER", "USER"}


def _has_any_role(actor_roles: list[str] | None, allowed_roles: set[str]) -> bool:
    return bool(set(actor_roles or []).intersection(allowed_roles))


def _primary_role(user: AuthUser) -> str:
    return user.actor_roles[0] if user.actor_roles else "USER"


def _permission_error(request_id: str, message: str) -> dict[str, Any]:
    return error_response(
        request_id=request_id,
        code=ErrorCode.PERMISSION_DENIED,
        details=[{"field": "actorRoles", "message": message}],
    )


def _validation_error(request_id: str, field: str, message: str) -> dict[str, Any]:
    return error_response(
        request_id=request_id,
        code=ErrorCode.VALIDATION_INVALID_ARGUMENT,
        details=[{"field": field, "message": message}],
    )


def _missing_error(request_id: str, field: str, message: str) -> dict[str, Any]:
    return error_response(
        request_id=request_id,
        code=ErrorCode.VALIDATION_REQUIRED_FIELD_MISSING,
        details=[{"field": field, "message": message}],
    )


def _can_manage_role(actor_roles: list[str] | None, target_role: str) -> bool:
    if _has_any_role(actor_roles, ADMIN_ROLES):
        return target_role in MANAGEABLE_ROLES
    if _has_any_role(actor_roles, {"OPERATOR"}):
        return target_role in OPERATOR_MANAGEABLE_ROLES
    return False


def _visible_accounts(repository: AuthUserRepository, actor_roles: list[str] | None) -> list[AuthUser]:
    accounts = repository.list()
    if _has_any_role(actor_roles, ADMIN_ROLES):
        return accounts
    if _has_any_role(actor_roles, {"OPERATOR"}):
        return [account for account in accounts if _primary_role(account) in OPERATOR_MANAGEABLE_ROLES]
    return []


def list_admin_accounts(
    *,
    repository: AuthUserRepository,
    request_id: str,
    actor_roles: list[str] | None,
) -> dict[str, Any]:
    if not _has_any_role(actor_roles, BACKOFFICE_ROLES - {"TEACHER"}):
        return _permission_error(request_id, "only admin or operator can manage accounts")
    return success_response(
        request_id=request_id,
        data={"items": [account.to_account_response() for account in _visible_accounts(repository, actor_roles)]},
    )


def create_admin_account(
    *,
    repository: AuthUserRepository,
    request_id: str,
    actor_roles: list[str] | None,
    payload: dict[str, Any],
) -> dict[str, Any]:
    username = str(payload.get("username") or "").strip()
    password = str(payload.get("password") or "")
    display_name = str(payload.get("displayName") or "").strip()
    email = str(payload.get("email") or "").strip().lower() or None
    role = str(payload.get("role") or "").strip().upper()

    if not username:
        return _missing_error(request_id, "username", "username is required")
    if not password:
        return _missing_error(request_id, "password", "password is required")
    if not display_name:
        return _missing_error(request_id, "displayName", "displayName is required")
    if role not in MANAGEABLE_ROLES:
        return _validation_error(request_id, "role", "role is invalid")
    if not _can_manage_role(actor_roles, role):
        return _permission_error(request_id, "current role cannot create this account role")
    if repository.get(username) is not None:
        return _validation_error(request_id, "username", "username already exists")

    saved = repository.save(
        AuthUser(
            username=username,
            password=password,
            actor_id=f"u_{uuid4().hex}",
            actor_roles=[role],
            display_name=display_name,
            email=email,
            is_active=True,
        )
    )
    return success_response(request_id=request_id, data=saved.to_account_response())


def update_admin_account(
    *,
    repository: AuthUserRepository,
    request_id: str,
    actor_id: str,
    actor_roles: list[str] | None,
    payload: dict[str, Any],
) -> dict[str, Any]:
    current = repository.get_by_actor_id(actor_id)
    if current is None:
        return _validation_error(request_id, "actorId", "account not found")
    current_role = _primary_role(current)
    if not _can_manage_role(actor_roles, current_role):
        return _permission_error(request_id, "current role cannot update this account")

    next_role = str(payload.get("role") or current_role).strip().upper()
    if next_role not in MANAGEABLE_ROLES:
        return _validation_error(request_id, "role", "role is invalid")
    if not _can_manage_role(actor_roles, next_role):
        return _permission_error(request_id, "current role cannot assign this account role")

    display_name = str(payload.get("displayName") or current.display_name).strip()
    email = str(payload.get("email") or "").strip().lower() or None
    password = str(payload.get("password") or current.password)
    if not display_name:
        return _missing_error(request_id, "displayName", "displayName is required")

    saved = repository.save(
        replace(
            current,
            password=password,
            actor_roles=[next_role],
            display_name=display_name,
            email=email,
        )
    )
    return success_response(request_id=request_id, data=saved.to_account_response())


def disable_admin_account(
    *,
    repository: AuthUserRepository,
    request_id: str,
    target_actor_id: str,
    actor_id: str,
    actor_roles: list[str] | None,
) -> dict[str, Any]:
    current = repository.get_by_actor_id(target_actor_id)
    if current is None:
        return _validation_error(request_id, "actorId", "account not found")
    if target_actor_id == actor_id:
        return _validation_error(request_id, "actorId", "cannot disable current account")
    if not _can_manage_role(actor_roles, _primary_role(current)):
        return _permission_error(request_id, "current role cannot disable this account")
    saved = repository.save(replace(current, is_active=False))
    return success_response(request_id=request_id, data=saved.to_account_response())


def delete_admin_account(
    *,
    repository: AuthUserRepository,
    request_id: str,
    target_actor_id: str,
    actor_id: str,
    actor_roles: list[str] | None,
) -> dict[str, Any]:
    current = repository.get_by_actor_id(target_actor_id)
    if current is None:
        return _validation_error(request_id, "actorId", "account not found")
    if target_actor_id == actor_id:
        return _validation_error(request_id, "actorId", "cannot delete current account")
    if not _can_manage_role(actor_roles, _primary_role(current)):
        return _permission_error(request_id, "current role cannot delete this account")
    repository.delete(target_actor_id)
    return success_response(request_id=request_id, data={"actorId": target_actor_id, "deleted": True})
