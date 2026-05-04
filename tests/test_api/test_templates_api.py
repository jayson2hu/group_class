from __future__ import annotations


def test_create_template_api_success(client, admin_headers):
    """TC-T01: 管理员可创建模板。"""

    response = client.post(
        "/api/v1/admin/templates",
        json={
            "templateName": "API 英语模板",
            "classType": "GROUP_CLASS",
            "defaultPriceAmount": 1999,
            "defaultMinStudents": 4,
            "defaultMaxStudents": 8,
        },
        headers=admin_headers,
    )

    data = response.json()["data"]
    assert response.status_code == 200
    assert data["templateId"].startswith("tpl-")
    assert data["templateName"] == "API 英语模板"


def test_create_template_without_admin_role_returns_403(client, initiator_headers):
    """TC-T02: 非管理员创建模板返回 403。"""

    response = client.post(
        "/api/v1/admin/templates",
        json={"templateName": "无权限模板"},
        headers=initiator_headers,
    )

    assert response.status_code == 403


def test_list_get_update_template_api(client, admin_headers):
    """TC-T03: 模板列表、详情、更新接口可用。"""

    created = client.post(
        "/api/v1/admin/templates",
        json={"templateName": "待更新模板", "defaultPriceAmount": 1200},
        headers=admin_headers,
    ).json()["data"]
    update = client.post(
        f"/api/v1/admin/templates/{created['templateId']}/update",
        json={"templateName": "已更新模板", "isActive": False},
        headers=admin_headers,
    )
    detail = client.get(f"/api/v1/admin/templates/{created['templateId']}", headers=admin_headers)
    listing = client.get("/api/v1/admin/templates", headers=admin_headers)

    assert update.status_code == 200
    assert detail.json()["data"]["templateName"] == "已更新模板"
    assert detail.json()["data"]["isActive"] is False
    assert any(item["templateId"] == created["templateId"] for item in listing.json()["data"]["items"])


def test_template_create_can_prefill_class_create(client, admin_headers, initiator_headers):
    """TC-T04: 课程创建可使用模板默认值。"""

    template = client.post(
        "/api/v1/admin/templates",
        json={
            "templateName": "课程创建模板",
            "classType": "GROUP_CLASS",
            "defaultPriceAmount": 2000,
            "defaultMinStudents": 3,
            "defaultMaxStudents": 6,
            "defaultScheduleSummary": "每周日 15:00-16:30",
        },
        headers=admin_headers,
    ).json()["data"]

    created = client.post(
        "/api/v1/admin/classes",
        json={"templateId": template["templateId"]},
        headers=initiator_headers,
    )

    data = created.json()["data"]
    assert created.status_code == 200
    assert data["templateId"] == template["templateId"]
    assert data["className"] == "课程创建模板"
    assert data["priceAmount"] == 2000


def test_get_missing_template_returns_404(client, admin_headers):
    """TC-T05: 查询不存在模板返回 404。"""

    response = client.get("/api/v1/admin/templates/tpl-missing", headers=admin_headers)

    assert response.status_code == 404
