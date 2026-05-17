from __future__ import annotations


def test_admin_dashboard_without_role_returns_403(client):
    response = client.get("/api/v1/admin/dashboard", headers={"X-Actor-Id": "u_nobody"})

    assert response.status_code == 403


def test_admin_dashboard_returns_core_metrics(client, admin_headers):
    response = client.get("/api/v1/admin/dashboard", headers=admin_headers)
    data = response.json()["data"]

    assert response.status_code == 200
    assert data["classCount"] >= 3
    assert data["publishedClassCount"] >= 2
    assert data["registrationCount"] == 0
    assert data["totalCurrentStudents"] >= 12
    assert data["totalWaitlistCount"] >= 2


def test_admin_notification_preview_returns_dry_run_message(client, admin_headers):
    response = client.post(
        "/api/v1/admin/notifications/preview",
        json={"scenario": "WAITLIST_PROMOTED", "target": "13900139000"},
        headers=admin_headers,
    )
    data = response.json()["data"]

    assert response.status_code == 200
    assert data["scenario"] == "WAITLIST_PROMOTED"
    assert data["target"] == "13900139000"
    assert data["providerStatus"] == "DRY_RUN"
    assert "候补" in data["message"]


def test_admin_notification_preview_rejects_invalid_scenario(client, admin_headers):
    response = client.post(
        "/api/v1/admin/notifications/preview",
        json={"scenario": "UNKNOWN", "target": "13900139000"},
        headers=admin_headers,
    )

    assert response.status_code == 400
    assert response.json()["details"][0]["field"] == "scenario"
