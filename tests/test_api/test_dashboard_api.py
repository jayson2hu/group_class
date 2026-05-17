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
