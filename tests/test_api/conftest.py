from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from apps.group_class_backend.app import app


@pytest.fixture
def client() -> TestClient:
    """每个测试函数得到一个全新的 TestClient（独立的 AppState）。"""

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def admin_headers() -> dict[str, str]:
    return {"X-Actor-Id": "u_test_admin", "X-Actor-Roles": "CLASS_ADMIN"}


@pytest.fixture
def initiator_headers() -> dict[str, str]:
    return {"X-Actor-Id": "u_test_initiator", "X-Actor-Roles": "INITIATOR"}


@pytest.fixture
def public_headers() -> dict[str, str]:
    return {"X-Actor-Id": "u_public_visitor"}
