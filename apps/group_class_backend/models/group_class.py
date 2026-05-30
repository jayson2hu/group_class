from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from apps.group_class_backend.common.enums import ClassStatus


@dataclass(slots=True)
class GroupClass:
    class_id: str
    version: int
    creator_id: str
    class_name: str | None
    template_id: str | None
    status: ClassStatus
    reviewer_id: str | None
    class_type: str | None
    price_amount: float | None
    deposit_amount: float | None
    min_students: int | None
    max_students: int | None
    current_students: int
    waitlist_count: int
    course_subtitle: str | None
    opening_level: str | None
    level_marker: str | None
    display_color: str | None
    wechat_contact: str | None
    phone_contact: str | None
    cover_image_url: str | None
    highlights: str | None
    owner_id: str | None
    target_audience: str | None
    unsuitable_audience: str | None
    course_goal: str | None
    schedule_summary: str | None
    session_count: int | None
    group_rule: str | None
    absence_rule: str | None
    waitlist_rule: str | None
    failure_rule: str | None
    faq_summary: str | None
    start_date: datetime | None
    end_date: datetime | None
    signup_deadline: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create_draft(
        cls,
        *,
        created_at: datetime,
        creator_id: str,
        class_name: str | None = None,
        template_id: str | None = None,
        class_type: str | None = None,
        price_amount: float | None = None,
        deposit_amount: float | None = None,
        min_students: int | None = None,
        max_students: int | None = None,
        course_subtitle: str | None = None,
        opening_level: str | None = None,
        level_marker: str | None = None,
        display_color: str | None = None,
        wechat_contact: str | None = None,
        phone_contact: str | None = None,
        cover_image_url: str | None = None,
        highlights: str | None = None,
        owner_id: str | None = None,
        target_audience: str | None = None,
        unsuitable_audience: str | None = None,
        course_goal: str | None = None,
        schedule_summary: str | None = None,
        session_count: int | None = None,
        group_rule: str | None = None,
        absence_rule: str | None = None,
        waitlist_rule: str | None = None,
        failure_rule: str | None = None,
        faq_summary: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        signup_deadline: datetime | None = None,
    ) -> "GroupClass":
        if not class_name and not template_id:
            raise ValueError("className or templateId is required")
        if min_students is not None and min_students <= 0:
            raise ValueError("minStudents must be greater than 0")
        if session_count is not None and session_count <= 0:
            raise ValueError("sessionCount must be greater than 0")
        if min_students is not None and max_students is not None and max_students < min_students:
            raise ValueError("maxStudents must be greater than or equal to minStudents")
        if start_date is not None and end_date is not None and end_date < start_date:
            raise ValueError("endDate must be greater than or equal to startDate")
        if signup_deadline is not None and start_date is not None and signup_deadline > start_date:
            raise ValueError("signupDeadline must be less than or equal to startDate")
        if price_amount is not None and deposit_amount is not None and deposit_amount > price_amount:
            raise ValueError("depositAmount must be less than or equal to priceAmount")

        return cls(
            class_id=f"cls-{uuid4().hex[:12]}",
            version=1,
            creator_id=creator_id,
            class_name=class_name,
            template_id=template_id,
            status=ClassStatus.DRAFT,
            reviewer_id=None,
            class_type=class_type,
            price_amount=price_amount,
            deposit_amount=deposit_amount,
            min_students=min_students,
            max_students=max_students,
            current_students=0,
            waitlist_count=0,
            course_subtitle=course_subtitle,
            opening_level=opening_level,
            level_marker=level_marker,
            display_color=display_color,
            wechat_contact=wechat_contact,
            phone_contact=phone_contact,
            cover_image_url=cover_image_url,
            highlights=highlights,
            owner_id=owner_id,
            target_audience=target_audience,
            unsuitable_audience=unsuitable_audience,
            course_goal=course_goal,
            schedule_summary=schedule_summary,
            session_count=session_count,
            group_rule=group_rule,
            absence_rule=absence_rule,
            waitlist_rule=waitlist_rule,
            failure_rule=failure_rule,
            faq_summary=faq_summary,
            start_date=start_date,
            end_date=end_date,
            signup_deadline=signup_deadline,
            created_at=created_at,
            updated_at=created_at,
        )
