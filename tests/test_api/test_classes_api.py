from __future__ import annotations


def _create_class(client, headers: dict[str, str], class_name: str = "API 测试课") -> dict:
    response = client.post(
        "/api/v1/admin/classes",
        json={"className": class_name, "minStudents": 3, "maxStudents": 10},
        headers=headers,
    )
    assert response.status_code == 200
    return response.json()["data"]


def _submit_review(client, class_id: str, version: int, headers: dict[str, str]) -> dict:
    response = client.post(
        f"/api/v1/admin/classes/{class_id}/submit-review",
        json={"version": version},
        headers=headers,
    )
    assert response.status_code == 200
    return response.json()["data"]


def _approve_review(client, class_id: str, version: int, headers: dict[str, str]) -> dict:
    response = client.post(
        f"/api/v1/admin/classes/{class_id}/approve",
        json={"version": version},
        headers=headers,
    )
    assert response.status_code == 200
    return response.json()["data"]


def test_public_list_returns_standard_response(client):
    """TC-C01: 前台列表返回 200，格式正确。"""

    response = client.get("/api/v1/public/classes")

    assert response.status_code == 200
    payload = response.json()
    assert {"requestId", "code", "data"} <= set(payload)
    assert payload["code"] == "OK"


def test_public_list_hides_draft_classes(client):
    """TC-C02: 前台列表不含 DRAFT 课程。"""

    response = client.get("/api/v1/public/classes")

    statuses = {item["status"] for item in response.json()["data"]["items"]}
    assert "DRAFT" not in statuses


def test_public_list_contains_pagination_fields(client):
    """TC-C03: 前台列表含分页字段。"""

    response = client.get("/api/v1/public/classes?page=1&page_size=1")

    data = response.json()["data"]
    assert data["page"] == 1
    assert data["pageSize"] == 1
    assert data["total"] >= 2
    assert len(data["items"]) == 1


def test_admin_list_contains_draft_class(client):
    """TC-C04: 后台列表含 DRAFT 课程。"""

    response = client.get("/api/v1/admin/classes")

    statuses = {item["status"] for item in response.json()["data"]["items"]}
    assert "DRAFT" in statuses


def test_create_class_returns_draft_version_one(client, initiator_headers):
    """TC-C05: 创建课程成功，返回 DRAFT 状态，version=1。"""

    data = _create_class(client, initiator_headers)

    assert data["status"] == "DRAFT"
    assert data["version"] == 1
    assert data["classId"].startswith("cls-")


def test_create_class_uses_actor_id_header(client, initiator_headers):
    """TC-C06: 创建课程，creatorId 来自 X-Actor-Id Header。"""

    data = _create_class(client, initiator_headers)

    assert data["creatorId"] == initiator_headers["X-Actor-Id"]


def test_create_class_missing_name_returns_400(client, initiator_headers):
    """TC-C07: 创建课程缺少 className 返回 400。"""

    response = client.post("/api/v1/admin/classes", json={"minStudents": 3}, headers=initiator_headers)

    assert response.status_code == 400
    assert response.json()["code"] == "VALIDATION_INVALID_ARGUMENT"


def test_update_class_changes_name_and_bumps_version(client, initiator_headers):
    """TC-C08: 更新课程成功，className 改变，version 递增。"""

    created = _create_class(client, initiator_headers, "更新前")
    response = client.post(
        f"/api/v1/admin/classes/{created['classId']}/update",
        json={"version": created["version"], "className": "更新后"},
        headers=initiator_headers,
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["className"] == "更新后"
    assert data["version"] == created["version"] + 1


def test_update_class_version_conflict_returns_409(client, initiator_headers):
    """TC-C09: 更新课程 version 冲突返回 409。"""

    created = _create_class(client, initiator_headers)
    client.post(
        f"/api/v1/admin/classes/{created['classId']}/update",
        json={"version": created["version"], "className": "第一次更新"},
        headers=initiator_headers,
    )
    response = client.post(
        f"/api/v1/admin/classes/{created['classId']}/update",
        json={"version": created["version"], "className": "冲突更新"},
        headers=initiator_headers,
    )

    assert response.status_code == 409
    assert response.json()["code"] == "CLASS_VERSION_CONFLICT"


def test_update_missing_class_returns_404(client, initiator_headers):
    """TC-C10: 更新不存在的课程返回 404。"""

    response = client.post(
        "/api/v1/admin/classes/cls-notexist/update",
        json={"version": 1, "className": "不存在"},
        headers=initiator_headers,
    )

    assert response.status_code == 404


def test_full_review_workflow(client, initiator_headers, admin_headers):
    """TC-C11: 审核流 DRAFT -> PENDING_REVIEW -> OPEN_FOR_ENROLLMENT。"""

    created = _create_class(client, initiator_headers, "审核流测试")
    submitted = _submit_review(client, created["classId"], created["version"], initiator_headers)
    approved = _approve_review(client, created["classId"], submitted["version"], admin_headers)

    assert submitted["status"] == "PENDING_REVIEW"
    assert approved["status"] == "OPEN_FOR_ENROLLMENT"
    assert approved["reviewerId"] == admin_headers["X-Actor-Id"]


def test_approved_class_is_visible_publicly(client, initiator_headers, admin_headers):
    """TC-C12: 审核通过后课程出现在前台列表。"""

    created = _create_class(client, initiator_headers, "前台可见测试")
    submitted = _submit_review(client, created["classId"], created["version"], initiator_headers)
    _approve_review(client, created["classId"], submitted["version"], admin_headers)

    response = client.get("/api/v1/public/classes")

    ids = {item["classId"] for item in response.json()["data"]["items"]}
    assert created["classId"] in ids


def test_initiator_approve_returns_403(client, initiator_headers):
    """TC-C13: INITIATOR 角色调用 approve 返回 403。"""

    created = _create_class(client, initiator_headers)
    submitted = _submit_review(client, created["classId"], created["version"], initiator_headers)
    response = client.post(
        f"/api/v1/admin/classes/{created['classId']}/approve",
        json={"version": submitted["version"]},
        headers=initiator_headers,
    )

    assert response.status_code == 403


def test_reject_review_transitions_to_rejected(client, initiator_headers, admin_headers):
    """TC-C14: 审核驳回 PENDING_REVIEW -> REJECTED。"""

    created = _create_class(client, initiator_headers, "驳回测试")
    submitted = _submit_review(client, created["classId"], created["version"], initiator_headers)
    response = client.post(
        f"/api/v1/admin/classes/{created['classId']}/reject",
        json={"version": submitted["version"]},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "REJECTED"


def test_rejected_class_is_hidden_publicly(client, initiator_headers, admin_headers):
    """TC-C15: REJECTED 课程不在前台列表中。"""

    created = _create_class(client, initiator_headers, "驳回隐藏测试")
    submitted = _submit_review(client, created["classId"], created["version"], initiator_headers)
    client.post(
        f"/api/v1/admin/classes/{created['classId']}/reject",
        json={"version": submitted["version"]},
        headers=admin_headers,
    )

    response = client.get("/api/v1/public/classes")

    ids = {item["classId"] for item in response.json()["data"]["items"]}
    assert created["classId"] not in ids
