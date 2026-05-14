from datetime import datetime, timedelta, timezone

from apps.group_class_backend.auth.email_codes import InMemoryEmailVerificationCodeRepository


def test_issue_email_code_uses_six_digits_and_five_minute_ttl() -> None:
    repository = InMemoryEmailVerificationCodeRepository()
    now = datetime(2026, 5, 14, 12, 0, tzinfo=timezone.utc)

    issued = repository.issue("USER@example.com", ttl_seconds=300, now=now)

    assert issued.email == "user@example.com"
    assert issued.code.isdigit()
    assert len(issued.code) == 6
    assert issued.expires_at == now + timedelta(seconds=300)


def test_verify_email_code_consumes_valid_code() -> None:
    repository = InMemoryEmailVerificationCodeRepository()
    now = datetime(2026, 5, 14, 12, 0, tzinfo=timezone.utc)
    issued = repository.issue("user@example.com", ttl_seconds=300, now=now)

    assert repository.verify("user@example.com", issued.code, now=now + timedelta(seconds=60)) is True
    assert repository.verify("user@example.com", issued.code, now=now + timedelta(seconds=61)) is False


def test_verify_email_code_rejects_wrong_or_expired_code() -> None:
    repository = InMemoryEmailVerificationCodeRepository()
    now = datetime(2026, 5, 14, 12, 0, tzinfo=timezone.utc)
    issued = repository.issue("user@example.com", ttl_seconds=300, now=now)

    assert repository.verify("user@example.com", "000000", now=now + timedelta(seconds=60)) is False
    assert repository.verify("user@example.com", issued.code, now=now + timedelta(seconds=301)) is False
