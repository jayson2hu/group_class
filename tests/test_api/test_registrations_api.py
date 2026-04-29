from __future__ import annotations

import pytest


def _public_class_id(client, status: str) -> str:
    response = client.get("/api/v1/public/classes")
    items = response.json()["data"]["items"]
    return next(item["classId"] for item in items if item["status"] == status)


@pytest.fixture
def approved_class_id(client, initiator_headers, admin_headers) -> str:
    """创建并审核通过一个课程，返回其 classId。"""

    created = client.post(
        "/api/v1/admin/classes",
        json={"className": "报名测试课", "minStudents": 3, "maxStudents": 10},
        headers=initiator_headers,
    ).json()["data"]
    submitted = client.post(
        f"/api/v1/admin/classes/{created['classId']}/submit-review",
        json={"version": created["version"]},
        headers=initiator_headers,
    ).json()["data"]
    client.post(
        f"/api/v1/admin/classes/{created['classId']}/approve",
        json={"version": submitted["version"]},
        headers=admin_headers,
    )
    return created["classId"]


def _submit_enrollment(client, class_id: str, public_headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/v1/public/registrations",
        json={
            "classId": class_id,
            "registerType": "ENROLLMENT",
            "parentName": "张三",
            "contactInfo": "13800138000",
            "studentName": "小明",
            "studentGrade": "三年级",
        },
        headers=public_headers,
    )
    assert response.status_code == 200
    return response.json()["data"]


def test_enrollment_registration_success(client, approved_class_id, public_headers):
    """TC-R01: ENROLLMENT 报名成功，registrationId 以 reg- 开头。"""

    data = _submit_enrollment(client, approved_class_id, public_headers)

    assert data["registrationId"].startswith("reg-")
    assert data["registrationStatus"] == "SUBMITTED"


def test_enrollment_increments_current_students(client, approved_class_id, public_headers):
    """TC-R02: ENROLLMENT 报名后课程 currentStudents +1。"""

    before = client.get(f"/api/v1/admin/classes/{approved_class_id}").json()["data"]["currentStudents"]
    _submit_enrollment(client, approved_class_id, public_headers)
    after = client.get(f"/api/v1/admin/classes/{approved_class_id}").json()["data"]["currentStudents"]

    assert after == before + 1


def test_waitlist_registration_success(client, public_headers):
    """TC-R03: WAITLIST 报名成功，status=WAITLISTED。"""

    class_id = _public_class_id(client, "FULL")
    response = client.post(
        "/api/v1/public/registrations",
        json={
            "classId": class_id,
            "registerType": "WAITLIST",
            "parentName": "李四",
            "contactInfo": "13900139000",
            "studentGrade": "四年级",
        },
        headers=public_headers,
    )

    assert response.status_code == 200
    assert response.json()["data"]["registrationStatus"] == "WAITLISTED"


def test_waitlist_increments_waitlist_count(client, public_headers):
    """TC-R04: WAITLIST 报名后课程 waitlistCount +1。"""

    class_id = _public_class_id(client, "FULL")
    before = client.get(f"/api/v1/admin/classes/{class_id}").json()["data"]["waitlistCount"]
    client.post(
        "/api/v1/public/registrations",
        json={
            "classId": class_id,
            "registerType": "WAITLIST",
            "parentName": "李四",
            "contactInfo": "13900139000",
            "studentGrade": "四年级",
        },
        headers=public_headers,
    )
    after = client.get(f"/api/v1/admin/classes/{class_id}").json()["data"]["waitlistCount"]

    assert after == before + 1


def test_registration_unknown_class_returns_400(client, public_headers):
    """TC-R05: 报名到不存在的课程返回 400。"""

    response = client.post(
        "/api/v1/public/registrations",
        json={
            "classId": "cls-notexist",
            "registerType": "ENROLLMENT",
            "parentName": "张三",
            "contactInfo": "13800138000",
            "studentName": "小明",
            "studentGrade": "三年级",
        },
        headers=public_headers,
    )

    assert response.status_code == 400


def test_enrollment_missing_student_name_returns_400(client, approved_class_id, public_headers):
    """TC-R06: ENROLLMENT 报名缺少 studentName 返回 400。"""

    response = client.post(
        "/api/v1/public/registrations",
        json={
            "classId": approved_class_id,
            "registerType": "ENROLLMENT",
            "parentName": "张三",
            "contactInfo": "13800138000",
            "studentGrade": "三年级",
        },
        headers=public_headers,
    )

    assert response.status_code == 400


def test_admin_registration_list_without_role_returns_403(client):
    """TC-R07: 后台报名列表无角色返回 403。"""

    response = client.get("/api/v1/admin/registrations", headers={"X-Actor-Id": "u_nobody"})

    assert response.status_code == 403


def test_admin_registration_list_with_admin_returns_200(client, approved_class_id, public_headers, admin_headers):
    """TC-R08: 后台报名列表有 CLASS_ADMIN 角色返回 200。"""

    _submit_enrollment(client, approved_class_id, public_headers)
    response = client.get("/api/v1/admin/registrations", headers=admin_headers)

    assert response.status_code == 200
    assert len(response.json()["data"]["items"]) == 1


def test_admin_registration_list_contains_pagination_fields(client, approved_class_id, public_headers, admin_headers):
    """TC-R09: 后台报名列表含分页字段，支持 pageSize。"""

    _submit_enrollment(client, approved_class_id, public_headers)
    _submit_enrollment(client, approved_class_id, public_headers)
    response = client.get("/api/v1/admin/registrations?page=1&pageSize=1", headers=admin_headers)

    data = response.json()["data"]
    assert response.status_code == 200
    assert data["page"] == 1
    assert data["pageSize"] == 1
    assert data["total"] == 2
    assert len(data["items"]) == 1


def test_registration_detail_contains_core_fields(client, approved_class_id, public_headers, admin_headers):
    """TC-R10: 报名详情字段完整。"""

    registration = _submit_enrollment(client, approved_class_id, public_headers)
    response = client.get(f"/api/v1/admin/registrations/{registration['registrationId']}", headers=admin_headers)

    data = response.json()["data"]
    assert data["parentName"] == "张三"
    assert data["contactInfo"] == "13800138000"
    assert data["studentName"] == "小明"


def test_update_notes_persists(client, approved_class_id, public_headers, admin_headers):
    """TC-R11: 更新备注成功，字段持久化。"""

    registration = _submit_enrollment(client, approved_class_id, public_headers)
    registration_id = registration["registrationId"]
    response = client.post(
        f"/api/v1/admin/registrations/{registration_id}/notes",
        json={"followUpNote": "已电话确认", "notes": "家长希望周三晚"},
        headers=admin_headers,
    )
    detail = client.get(f"/api/v1/admin/registrations/{registration_id}", headers=admin_headers)

    assert response.status_code == 200
    assert detail.json()["data"]["followUpNote"] == "已电话确认"
    assert detail.json()["data"]["notes"] == "家长希望周三晚"


def test_update_status_valid_success(client, approved_class_id, public_headers, admin_headers):
    """TC-R12: 更新状态为 VALID 成功。"""

    registration = _submit_enrollment(client, approved_class_id, public_headers)
    response = client.post(
        f"/api/v1/admin/registrations/{registration['registrationId']}/status",
        json={"registrationStatus": "VALID"},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["data"]["registrationStatus"] == "VALID"


def test_update_status_invalid_value_returns_400(client, approved_class_id, public_headers, admin_headers):
    """TC-R13: 更新状态为非法值返回 400。"""

    registration = _submit_enrollment(client, approved_class_id, public_headers)
    response = client.post(
        f"/api/v1/admin/registrations/{registration['registrationId']}/status",
        json={"registrationStatus": "INVALID_VALUE"},
        headers=admin_headers,
    )

    assert response.status_code == 400


def test_update_notes_without_role_returns_403(client, approved_class_id, public_headers):
    """TC-R14: 无权限更新备注返回 403。"""

    registration = _submit_enrollment(client, approved_class_id, public_headers)
    response = client.post(
        f"/api/v1/admin/registrations/{registration['registrationId']}/notes",
        json={"followUpNote": "无权限测试"},
        headers={"X-Actor-Id": "u_nobody"},
    )

    assert response.status_code == 403
