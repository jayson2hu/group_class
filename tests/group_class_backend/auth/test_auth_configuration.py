from apps.group_class_backend.auth.configuration import AuthConfiguration, InMemoryAuthConfigurationRepository


def test_auth_configuration_defaults_to_username_login_only() -> None:
    configuration = AuthConfiguration.default()

    assert configuration.enabled_login_methods == ["username"]
    assert configuration.enabled_registration_methods == []
    assert configuration.email_code_ttl_seconds == 300


def test_auth_configuration_from_payload_supports_wechat_and_email_settings() -> None:
    configuration = AuthConfiguration.from_payload(
        {
            "enabledLoginMethods": ["username", "wechat_qr", "email"],
            "enabledRegistrationMethods": ["wechat_qr", "email"],
            "wechatEnabled": True,
            "wechatQrCodeUrl": "https://example.test/qrcode.png",
            "wechatAppId": "wx-app",
            "wechatAppSecret": "secret",
            "wechatCallbackUrl": "https://example.test/callback",
            "emailEnabled": True,
            "smtpHost": "smtp.example.test",
            "smtpPort": 465,
            "smtpUsername": "noreply@example.test",
            "smtpSender": "noreply@example.test",
            "emailCodeTtlSeconds": 300,
        }
    )

    response = configuration.to_response()

    assert response["enabledLoginMethods"] == ["username", "wechat_qr", "email"]
    assert response["enabledRegistrationMethods"] == ["wechat_qr", "email"]
    assert response["wechatEnabled"] is True
    assert response["wechatAppSecretConfigured"] is True
    assert response["emailEnabled"] is True
    assert response["emailCodeTtlSeconds"] == 300


def test_in_memory_auth_configuration_repository_saves_configuration() -> None:
    repository = InMemoryAuthConfigurationRepository()
    saved = repository.save(AuthConfiguration(email_enabled=True, enabled_login_methods=["email"]))

    assert repository.get() == saved
    assert repository.get().enabled_login_methods == ["email"]
