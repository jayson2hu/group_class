from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


_DEFAULT_EMAIL_CODE_TTL_SECONDS = 300


@dataclass(frozen=True)
class AuthConfiguration:
    enabled_login_methods: list[str] = field(default_factory=lambda: ["username"])
    enabled_registration_methods: list[str] = field(default_factory=list)
    wechat_enabled: bool = False
    wechat_qr_code_url: str | None = None
    wechat_app_id: str | None = None
    wechat_app_secret: str | None = None
    wechat_callback_url: str | None = None
    email_enabled: bool = False
    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_username: str | None = None
    smtp_sender: str | None = None
    email_code_ttl_seconds: int = _DEFAULT_EMAIL_CODE_TTL_SECONDS

    @classmethod
    def default(cls) -> "AuthConfiguration":
        return cls()

    @classmethod
    def from_payload(cls, payload: dict) -> "AuthConfiguration":
        email_ttl = int(payload.get("emailCodeTtlSeconds") or _DEFAULT_EMAIL_CODE_TTL_SECONDS)
        if email_ttl <= 0:
            raise ValueError("emailCodeTtlSeconds must be greater than 0")

        return cls(
            enabled_login_methods=_clean_methods(payload.get("enabledLoginMethods"), default=["username"]),
            enabled_registration_methods=_clean_methods(payload.get("enabledRegistrationMethods"), default=[]),
            wechat_enabled=bool(payload.get("wechatEnabled", False)),
            wechat_qr_code_url=_optional_text(payload.get("wechatQrCodeUrl")),
            wechat_app_id=_optional_text(payload.get("wechatAppId")),
            wechat_app_secret=_optional_text(payload.get("wechatAppSecret")),
            wechat_callback_url=_optional_text(payload.get("wechatCallbackUrl")),
            email_enabled=bool(payload.get("emailEnabled", False)),
            smtp_host=_optional_text(payload.get("smtpHost")),
            smtp_port=_optional_int(payload.get("smtpPort")),
            smtp_username=_optional_text(payload.get("smtpUsername")),
            smtp_sender=_optional_text(payload.get("smtpSender")),
            email_code_ttl_seconds=email_ttl,
        )

    def to_response(self) -> dict:
        return {
            "enabledLoginMethods": self.enabled_login_methods,
            "enabledRegistrationMethods": self.enabled_registration_methods,
            "wechatEnabled": self.wechat_enabled,
            "wechatQrCodeUrl": self.wechat_qr_code_url,
            "wechatAppId": self.wechat_app_id,
            "wechatAppSecretConfigured": bool(self.wechat_app_secret),
            "wechatCallbackUrl": self.wechat_callback_url,
            "emailEnabled": self.email_enabled,
            "smtpHost": self.smtp_host,
            "smtpPort": self.smtp_port,
            "smtpUsername": self.smtp_username,
            "smtpSender": self.smtp_sender,
            "emailCodeTtlSeconds": self.email_code_ttl_seconds,
        }


class AuthConfigurationRepository(Protocol):
    def get(self) -> AuthConfiguration:
        ...

    def save(self, configuration: AuthConfiguration) -> AuthConfiguration:
        ...


class InMemoryAuthConfigurationRepository:
    def __init__(self, initial: AuthConfiguration | None = None) -> None:
        self._configuration = initial or AuthConfiguration.default()

    def get(self) -> AuthConfiguration:
        return self._configuration

    def save(self, configuration: AuthConfiguration) -> AuthConfiguration:
        self._configuration = configuration
        return self._configuration


def _clean_methods(value: object, default: list[str]) -> list[str]:
    if not isinstance(value, list):
        return list(default)
    methods = [str(item).strip() for item in value if str(item).strip()]
    return methods or list(default)


def _optional_text(value: object) -> str | None:
    text = str(value or "").strip()
    return text or None


def _optional_int(value: object) -> int | None:
    if value in (None, ""):
        return None
    parsed = int(value)
    return parsed if parsed > 0 else None
