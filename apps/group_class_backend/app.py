from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import replace
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.group_class_backend.audit.interface import InMemoryAuditLog
from apps.group_class_backend.classes.repository import InMemoryClassRepository
from apps.group_class_backend.common.enums import ClassStatus
from apps.group_class_backend.models.group_class import GroupClass
from apps.group_class_backend.registrations.repository import InMemoryRegistrationRepository
from apps.group_class_backend.templates.repository import InMemoryTemplateRepository


class AppState:
    def __init__(self) -> None:
        self.class_repository = InMemoryClassRepository()
        self.registration_repository = InMemoryRegistrationRepository()
        self.template_repository = InMemoryTemplateRepository()
        self.audit_writer = InMemoryAuditLog()
        _seed_classes(self.class_repository)


_state: AppState | None = None


def get_state() -> AppState:
    assert _state is not None, "AppState not initialized"
    return _state


def new_request_id() -> str:
    return f"req-{uuid4().hex[:12]}"


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
        start_date=datetime(2026, 6, 20, tzinfo=timezone.utc),
        end_date=datetime(2026, 8, 20, tzinfo=timezone.utc),
        signup_deadline=datetime(2026, 6, 18, 23, 59, tzinfo=timezone.utc),
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
        start_date=datetime(2026, 6, 25, tzinfo=timezone.utc),
        end_date=datetime(2026, 9, 25, tzinfo=timezone.utc),
        signup_deadline=datetime(2026, 6, 23, 23, 59, tzinfo=timezone.utc),
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _state
    _state = AppState()
    yield
    _state = None


app = FastAPI(
    title="拼课课程系统",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}


from apps.group_class_backend.routers import classes as classes_router
from apps.group_class_backend.routers import dashboard as dashboard_router
from apps.group_class_backend.routers import registrations as registrations_router
from apps.group_class_backend.routers import templates as templates_router

app.include_router(classes_router.router)
app.include_router(dashboard_router.router)
app.include_router(registrations_router.router)
app.include_router(templates_router.router)
