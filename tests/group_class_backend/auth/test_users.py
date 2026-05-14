from apps.group_class_backend.auth.users import AuthUser, InMemoryAuthUserRepository


def test_user_repository_saves_registered_user() -> None:
    repository = InMemoryAuthUserRepository()
    user = AuthUser(
        username="parent001",
        password="secret",
        actor_id="u_parent001",
        actor_roles=["USER"],
        display_name="Parent",
        email="parent@example.test",
    )

    repository.save(user)

    assert repository.get("parent001") == user
    assert repository.get("parent001").to_session("tk-test")["actorRoles"] == ["USER"]
