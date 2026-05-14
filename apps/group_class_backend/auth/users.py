from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AuthUser:
    username: str
    password: str
    actor_id: str
    actor_roles: list[str]
    display_name: str
    email: str | None = None
    is_active: bool = True

    def to_session(self, token: str) -> dict:
        return {
            "token": token,
            "actorId": self.actor_id,
            "actorRoles": self.actor_roles,
            "displayName": self.display_name,
        }

    def to_account_response(self) -> dict:
        return {
            "username": self.username,
            "actorId": self.actor_id,
            "actorRoles": self.actor_roles,
            "displayName": self.display_name,
            "email": self.email,
            "isActive": self.is_active,
        }


class AuthUserRepository(Protocol):
    def get(self, username: str) -> AuthUser | None:
        ...

    def get_by_actor_id(self, actor_id: str) -> AuthUser | None:
        ...

    def list(self) -> list[AuthUser]:
        ...

    def save(self, user: AuthUser) -> AuthUser:
        ...

    def delete(self, actor_id: str) -> bool:
        ...


class InMemoryAuthUserRepository:
    def __init__(self, initial: list[AuthUser] | None = None) -> None:
        self._users = {user.username: user for user in initial or []}

    def get(self, username: str) -> AuthUser | None:
        return self._users.get(username)

    def get_by_actor_id(self, actor_id: str) -> AuthUser | None:
        for user in self._users.values():
            if user.actor_id == actor_id:
                return user
        return None

    def list(self) -> list[AuthUser]:
        return sorted(self._users.values(), key=lambda user: user.username)

    def save(self, user: AuthUser) -> AuthUser:
        self._users[user.username] = user
        return user

    def delete(self, actor_id: str) -> bool:
        user = self.get_by_actor_id(actor_id)
        if user is None:
            return False
        del self._users[user.username]
        return True
