from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class ClassTemplate:
    template_id: str
    template_name: str
    class_type: str | None
    default_price_amount: float | None
    default_deposit_amount: float | None = None
    default_min_students: int | None = None
    default_max_students: int | None = None
    default_course_subtitle: str | None = None
    default_target_audience: str | None = None
    default_unsuitable_audience: str | None = None
    default_course_goal: str | None = None
    default_schedule_summary: str | None = None
    default_session_count: int | None = None
    default_group_rule: str | None = None
    default_absence_rule: str | None = None
    default_waitlist_rule: str | None = None
    default_failure_rule: str | None = None
    default_faq_summary: str | None = None
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
