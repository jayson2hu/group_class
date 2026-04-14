from __future__ import annotations

import json
import os
from dataclasses import replace
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from apps.group_class_backend.audit.interface import NullAuditWriter
from apps.group_class_backend.classes.controller import (
    approve_class_review,
    create_class_draft,
    get_class_detail,
    list_classes,
    reject_class_review,
    submit_class_review,
    update_class_draft,
)
from apps.group_class_backend.classes.repository import InMemoryClassRepository
from apps.group_class_backend.common.error_codes import ErrorCode
from apps.group_class_backend.common.responses import error_response
from apps.group_class_backend.common.enums import ClassStatus
from apps.group_class_backend.models.group_class import GroupClass
from apps.group_class_backend.registrations.controller import (
    get_registration_detail,
    list_registrations,
    submit_registration,
    update_registration_notes,
    update_registration_status,
)
from apps.group_class_backend.registrations.repository import InMemoryRegistrationRepository


def _seed_classes(class_repository: InMemoryClassRepository) -> None:
    now = datetime.now(timezone.utc)
    class_open = GroupClass.create_draft(
        created_at=now,
        creator_id="u_demo_creator",
        class_name="三年级英语拼课班",
        class_type="GROUP_CLASS",
        price_amount=1999,
        min_students=6,
        max_students=8,
        course_subtitle="晚间启蒙小班",
        target_audience="三年级英语基础薄弱学生",
        unsuitable_audience="高阶语法强化学生",
        course_goal="提升阅读与口语基础",
        schedule_summary="每周三 19:00-20:30",
        session_count=12,
        waitlist_rule="满员后可加入候补",
        absence_rule="缺课支持一次补录",
        failure_rule="不成班将统一转班/退款",
        faq_summary="报名后老师/运营会联系确认",
    )
    class_open = replace(
        class_open,
        status=ClassStatus.OPEN_FOR_ENROLLMENT,
        current_students=4,
        start_date=datetime(2026, 4, 20, tzinfo=timezone.utc),
        end_date=datetime(2026, 6, 20, tzinfo=timezone.utc),
        signup_deadline=datetime(2026, 4, 18, 23, 59, tzinfo=timezone.utc),
        updated_at=now,
    )
    class_repository.save(class_open)

    class_full = GroupClass.create_draft(
        created_at=now,
        creator_id="u_demo_creator",
        class_name="四年级阅读强化班",
        class_type="GROUP_CLASS",
        price_amount=2399,
        min_students=6,
        max_students=8,
        course_subtitle="周末进阶",
        target_audience="四年级阅读提升学生",
        unsuitable_audience="零基础学员",
        course_goal="阅读理解与表达",
        schedule_summary="每周六 10:00-11:30",
        session_count=12,
        waitlist_rule="按候补顺序补位",
        absence_rule="支持一次请假",
        failure_rule="不成班转推荐课程",
        faq_summary="候补后运营会通知结果",
    )
    class_full = replace(
        class_full,
        status=ClassStatus.FULL,
        current_students=8,
        waitlist_count=2,
        start_date=datetime(2026, 4, 25, tzinfo=timezone.utc),
        end_date=datetime(2026, 7, 25, tzinfo=timezone.utc),
        signup_deadline=datetime(2026, 4, 23, 23, 59, tzinfo=timezone.utc),
        updated_at=now,
    )
    class_repository.save(class_full)

    class_draft = GroupClass.create_draft(
        created_at=now,
        creator_id="u_demo_creator",
        class_name="后台草稿示例班",
        class_type="GROUP_CLASS",
        price_amount=1888,
        min_students=5,
        max_students=10,
        schedule_summary="每周日 15:00-16:30",
    )
    class_repository.save(class_draft)


class AppState:
    def __init__(self) -> None:
        self.class_repository = InMemoryClassRepository()
        self.registration_repository = InMemoryRegistrationRepository()
        self.audit_writer = NullAuditWriter()
        _seed_classes(self.class_repository)


class GroupClassRequestHandler(BaseHTTPRequestHandler):
    state = AppState()

    def _request_id(self) -> str:
        return f"req-{uuid4().hex[:12]}"

    def _write_json(self, status_code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length) if content_length > 0 else b"{}"
        return json.loads(raw.decode("utf-8"))

    def _http_status_for_result(self, result: dict[str, Any], fallback_status: int = 400) -> int:
        code = result.get("code")
        if code == ErrorCode.OK.value:
            return 200
        if code == ErrorCode.PERMISSION_DENIED.value:
            return 403
        if code == ErrorCode.CLASS_VERSION_CONFLICT.value:
            return 409
        if code == ErrorCode.CLASS_NOT_FOUND.value:
            return 404
        return fallback_status

    def _actor_roles_from_query(self, parsed) -> list[str] | None:
        query_map = parse_qs(parsed.query)
        raw_roles = query_map.get("actorRoles", [])
        if not raw_roles:
            return None
        role_text = raw_roles[0]
        roles = [role.strip() for role in role_text.split(",") if role.strip()]
        return roles or None

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        request_id = self._request_id()
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            if path == "/api/v1/public/classes":
                payload = list_classes(
                    repository=self.state.class_repository,
                    request_id=request_id,
                    page=1,
                    page_size=50,
                    public_only=True,
                )
                self._write_json(200, payload)
                return

            if path.startswith("/api/v1/public/classes/"):
                class_id = path.split("/")[-1]
                payload = get_class_detail(
                    class_id=class_id,
                    repository=self.state.class_repository,
                    request_id=request_id,
                    public_only=True,
                )
                status = 404 if payload.get("code") == ErrorCode.CLASS_NOT_FOUND.value else 200
                self._write_json(status, payload)
                return

            if path == "/api/v1/admin/classes":
                payload = list_classes(
                    repository=self.state.class_repository,
                    request_id=request_id,
                    page=1,
                    page_size=50,
                    public_only=False,
                )
                self._write_json(200, payload)
                return

            if path.startswith("/api/v1/admin/classes/"):
                class_id = path.split("/")[-1]
                payload = get_class_detail(
                    class_id=class_id,
                    repository=self.state.class_repository,
                    request_id=request_id,
                    public_only=False,
                )
                status = 404 if payload.get("code") == ErrorCode.CLASS_NOT_FOUND.value else 200
                self._write_json(status, payload)
                return

            if path == "/api/v1/admin/registrations":
                query_map = parse_qs(parsed.query)
                payload = list_registrations(
                    class_repository=self.state.class_repository,
                    registration_repository=self.state.registration_repository,
                    request_id=request_id,
                    actor_id=str((query_map.get("actorId") or ["u_admin"])[0]),
                    actor_roles=self._actor_roles_from_query(parsed),
                )
                status = self._http_status_for_result(payload)
                self._write_json(status, payload)
                return

            if path.startswith("/api/v1/admin/registrations/"):
                registration_id = path.split("/")[-1]
                query_map = parse_qs(parsed.query)
                payload = get_registration_detail(
                    registration_id=registration_id,
                    class_repository=self.state.class_repository,
                    registration_repository=self.state.registration_repository,
                    request_id=request_id,
                    actor_id=str((query_map.get("actorId") or ["u_admin"])[0]),
                    actor_roles=self._actor_roles_from_query(parsed),
                )
                status = self._http_status_for_result(payload)
                self._write_json(status, payload)
                return

            self._write_json(
                404,
                error_response(
                    request_id=request_id,
                    code=ErrorCode.CLASS_NOT_FOUND,
                    details=[{"field": "path", "message": f"route not found: {path}"}],
                ),
            )
        except Exception as exc:
            self._write_json(
                500,
                error_response(
                    request_id=request_id,
                    code=ErrorCode.SYSTEM_INTERNAL_ERROR,
                    details=[{"field": "server", "message": str(exc)}],
                ),
            )

    def do_POST(self) -> None:
        request_id = self._request_id()
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            if path == "/api/v1/public/registrations":
                payload = self._read_json_body()
                result = submit_registration(
                    payload=payload,
                    class_repository=self.state.class_repository,
                    registration_repository=self.state.registration_repository,
                    audit_writer=self.state.audit_writer,
                    request_id=request_id,
                    actor_id=str(payload.get("actorId") or "u_public_visitor"),
                    now=datetime.now(timezone.utc),
                )
                status = 400 if result.get("code") != ErrorCode.OK.value else 200
                self._write_json(status, result)
                return

            if path == "/api/v1/admin/classes":
                body = self._read_json_body()
                result = create_class_draft(
                    payload=body,
                    repository=self.state.class_repository,
                    audit_writer=self.state.audit_writer,
                    request_id=request_id,
                    actor_id=str(body.get("actorId") or "u_admin"),
                    now=datetime.now(timezone.utc),
                )
                status = self._http_status_for_result(result)
                self._write_json(status, result)
                return

            if path.startswith("/api/v1/admin/classes/") and path.endswith("/update"):
                body = self._read_json_body()
                class_id = path.removeprefix("/api/v1/admin/classes/").removesuffix("/update")
                result = update_class_draft(
                    class_id=class_id.strip("/"),
                    payload=body,
                    repository=self.state.class_repository,
                    audit_writer=self.state.audit_writer,
                    request_id=request_id,
                    actor_id=str(body.get("actorId") or "u_admin"),
                    now=datetime.now(timezone.utc),
                )
                status = self._http_status_for_result(result)
                self._write_json(status, result)
                return

            if path.startswith("/api/v1/admin/classes/") and path.endswith("/submit-review"):
                body = self._read_json_body()
                class_id = path.removeprefix("/api/v1/admin/classes/").removesuffix("/submit-review")
                result = submit_class_review(
                    class_id=class_id.strip("/"),
                    payload=body,
                    repository=self.state.class_repository,
                    audit_writer=self.state.audit_writer,
                    request_id=request_id,
                    actor_id=str(body.get("actorId") or "u_admin"),
                    actor_roles=body.get("actorRoles"),
                    now=datetime.now(timezone.utc),
                )
                status = self._http_status_for_result(result)
                self._write_json(status, result)
                return

            if path.startswith("/api/v1/admin/classes/") and path.endswith("/approve"):
                body = self._read_json_body()
                class_id = path.removeprefix("/api/v1/admin/classes/").removesuffix("/approve")
                result = approve_class_review(
                    class_id=class_id.strip("/"),
                    payload=body,
                    repository=self.state.class_repository,
                    audit_writer=self.state.audit_writer,
                    request_id=request_id,
                    actor_id=str(body.get("actorId") or "u_admin"),
                    actor_roles=body.get("actorRoles"),
                    now=datetime.now(timezone.utc),
                )
                status = self._http_status_for_result(result)
                self._write_json(status, result)
                return

            if path.startswith("/api/v1/admin/classes/") and path.endswith("/reject"):
                body = self._read_json_body()
                class_id = path.removeprefix("/api/v1/admin/classes/").removesuffix("/reject")
                result = reject_class_review(
                    class_id=class_id.strip("/"),
                    payload=body,
                    repository=self.state.class_repository,
                    audit_writer=self.state.audit_writer,
                    request_id=request_id,
                    actor_id=str(body.get("actorId") or "u_admin"),
                    actor_roles=body.get("actorRoles"),
                    now=datetime.now(timezone.utc),
                )
                status = self._http_status_for_result(result)
                self._write_json(status, result)
                return

            if path.startswith("/api/v1/admin/registrations/") and path.endswith("/notes"):
                body = self._read_json_body()
                registration_id = path.removeprefix("/api/v1/admin/registrations/").removesuffix("/notes")
                result = update_registration_notes(
                    registration_id=registration_id.strip("/"),
                    payload=body,
                    class_repository=self.state.class_repository,
                    registration_repository=self.state.registration_repository,
                    request_id=request_id,
                    actor_id=str(body.get("actorId") or "u_admin"),
                    actor_roles=body.get("actorRoles"),
                    now=datetime.now(timezone.utc),
                )
                status = self._http_status_for_result(result)
                self._write_json(status, result)
                return

            if path.startswith("/api/v1/admin/registrations/") and path.endswith("/status"):
                body = self._read_json_body()
                registration_id = path.removeprefix("/api/v1/admin/registrations/").removesuffix("/status")
                result = update_registration_status(
                    registration_id=registration_id.strip("/"),
                    payload=body,
                    class_repository=self.state.class_repository,
                    registration_repository=self.state.registration_repository,
                    audit_writer=self.state.audit_writer,
                    request_id=request_id,
                    actor_id=str(body.get("actorId") or "u_admin"),
                    actor_roles=body.get("actorRoles"),
                    now=datetime.now(timezone.utc),
                )
                status = self._http_status_for_result(result)
                self._write_json(status, result)
                return

            self._write_json(
                404,
                error_response(
                    request_id=request_id,
                    code=ErrorCode.CLASS_NOT_FOUND,
                    details=[{"field": "path", "message": f"route not found: {path}"}],
                ),
            )
        except json.JSONDecodeError:
            self._write_json(
                400,
                error_response(
                    request_id=request_id,
                    code=ErrorCode.VALIDATION_INVALID_ARGUMENT,
                    details=[{"field": "body", "message": "invalid json body"}],
                ),
            )
        except Exception as exc:
            self._write_json(
                500,
                error_response(
                    request_id=request_id,
                    code=ErrorCode.SYSTEM_INTERNAL_ERROR,
                    details=[{"field": "server", "message": str(exc)}],
                ),
            )


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), GroupClassRequestHandler)
    print(f"group_class backend running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    host = os.getenv("GROUP_CLASS_BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("GROUP_CLASS_BACKEND_PORT", "8000"))
    run(host=host, port=port)
