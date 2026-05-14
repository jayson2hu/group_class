from apps.group_class_backend.auth.accounts import (
    create_admin_account,
    delete_admin_account,
    disable_admin_account,
    list_admin_accounts,
    update_admin_account,
)
from apps.group_class_backend.auth.users import AuthUser, InMemoryAuthUserRepository


def _repository() -> InMemoryAuthUserRepository:
    return InMemoryAuthUserRepository(
        [
            AuthUser(username="admin", password="123456", actor_id="u_admin", actor_roles=["ADMIN"], display_name="Admin"),
            AuthUser(username="operator", password="123456", actor_id="u_operator", actor_roles=["OPERATOR"], display_name="Operator"),
            AuthUser(username="teacher", password="123456", actor_id="u_teacher", actor_roles=["TEACHER"], display_name="Teacher"),
            AuthUser(username="parent", password="123456", actor_id="u_parent", actor_roles=["USER"], display_name="Parent"),
        ]
    )


def test_admin_can_list_all_accounts() -> None:
    result = list_admin_accounts(repository=_repository(), request_id="req-accounts", actor_roles=["ADMIN"])

    assert result["code"] == "OK"
    assert {item["username"] for item in result["data"]["items"]} == {"admin", "operator", "teacher", "parent"}


def test_operator_only_lists_teacher_and_user_accounts() -> None:
    result = list_admin_accounts(repository=_repository(), request_id="req-accounts", actor_roles=["OPERATOR"])

    assert result["code"] == "OK"
    assert {item["username"] for item in result["data"]["items"]} == {"teacher", "parent"}


def test_teacher_cannot_manage_accounts() -> None:
    result = list_admin_accounts(repository=_repository(), request_id="req-accounts", actor_roles=["TEACHER"])

    assert result["code"] == "PERMISSION_DENIED"


def test_admin_can_create_operator_account() -> None:
    repository = _repository()

    result = create_admin_account(
        repository=repository,
        request_id="req-create",
        actor_roles=["ADMIN"],
        payload={"username": "ops2", "password": "secret", "displayName": "Ops 2", "role": "OPERATOR"},
    )

    assert result["code"] == "OK"
    assert repository.get("ops2").actor_roles == ["OPERATOR"]


def test_operator_cannot_create_admin_or_operator_accounts() -> None:
    repository = _repository()

    result = create_admin_account(
        repository=repository,
        request_id="req-create",
        actor_roles=["OPERATOR"],
        payload={"username": "ops2", "password": "secret", "displayName": "Ops 2", "role": "OPERATOR"},
    )

    assert result["code"] == "PERMISSION_DENIED"
    assert repository.get("ops2") is None


def test_operator_can_update_teacher_and_user_accounts() -> None:
    repository = _repository()

    result = update_admin_account(
        repository=repository,
        request_id="req-update",
        actor_id="u_teacher",
        actor_roles=["OPERATOR"],
        payload={"displayName": "Teacher Updated", "role": "TEACHER"},
    )

    assert result["code"] == "OK"
    assert repository.get_by_actor_id("u_teacher").display_name == "Teacher Updated"


def test_operator_cannot_update_admin_accounts() -> None:
    result = update_admin_account(
        repository=_repository(),
        request_id="req-update",
        actor_id="u_admin",
        actor_roles=["OPERATOR"],
        payload={"displayName": "Admin Updated", "role": "ADMIN"},
    )

    assert result["code"] == "PERMISSION_DENIED"


def test_admin_can_disable_and_delete_accounts() -> None:
    repository = _repository()

    disabled = disable_admin_account(
        repository=repository,
        request_id="req-disable",
        target_actor_id="u_teacher",
        actor_id="u_admin",
        actor_roles=["ADMIN"],
    )
    deleted = delete_admin_account(
        repository=repository,
        request_id="req-delete",
        target_actor_id="u_teacher",
        actor_id="u_admin",
        actor_roles=["ADMIN"],
    )

    assert disabled["code"] == "OK"
    assert deleted["code"] == "OK"
    assert repository.get_by_actor_id("u_teacher") is None
