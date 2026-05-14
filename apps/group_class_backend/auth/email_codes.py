from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from secrets import randbelow
from typing import Protocol


@dataclass(frozen=True)
class EmailVerificationCode:
    email: str
    code: str
    expires_at: datetime

    def is_expired(self, now: datetime | None = None) -> bool:
        current = now or datetime.now(timezone.utc)
        return current >= self.expires_at


class EmailVerificationCodeRepository(Protocol):
    def issue(self, email: str, ttl_seconds: int, now: datetime | None = None) -> EmailVerificationCode:
        ...

    def verify(self, email: str, code: str, now: datetime | None = None) -> bool:
        ...


class InMemoryEmailVerificationCodeRepository:
    def __init__(self) -> None:
        self._codes: dict[str, EmailVerificationCode] = {}

    def issue(self, email: str, ttl_seconds: int, now: datetime | None = None) -> EmailVerificationCode:
        normalized = _normalize_email(email)
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be greater than 0")
        current = now or datetime.now(timezone.utc)
        code = f"{randbelow(1_000_000):06d}"
        verification = EmailVerificationCode(
            email=normalized,
            code=code,
            expires_at=current + timedelta(seconds=ttl_seconds),
        )
        self._codes[normalized] = verification
        return verification

    def verify(self, email: str, code: str, now: datetime | None = None) -> bool:
        normalized = _normalize_email(email)
        verification = self._codes.get(normalized)
        if verification is None:
            return False
        if verification.code != str(code).strip():
            return False
        if verification.is_expired(now):
            self._codes.pop(normalized, None)
            return False
        self._codes.pop(normalized, None)
        return True


def _normalize_email(email: str) -> str:
    normalized = str(email or "").strip().lower()
    if "@" not in normalized:
        raise ValueError("email must be valid")
    return normalized
