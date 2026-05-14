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

    def to_session(self, token: str) -> dict:
        return {
            "token": token,
            "actorId": self.actor_id,
            "actorRoles": self.actor_roles,
            "displayName": self.display_name,
        }


class AuthUserRepository(Protocol):
    def get(self, username: str) -> AuthUser | None:
        ...

    def save(self, user: AuthUser) -> AuthUser:
        ...


class InMemoryAuthUserRepository:
    def __init__(self, initial: list[AuthUser] | None = None) -> None:
        self._users = {user.username: user for user in initial or []}

    def get(self, username: str) -> AuthUser | None:
        return self._users.get(username)

    def save(self, user: AuthUser) -> AuthUser:
        self._users[user.username] = user
        return user
