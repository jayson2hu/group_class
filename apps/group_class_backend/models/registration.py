from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class RegistrationType(StrEnum):
    ENROLLMENT = "ENROLLMENT"
    WAITLIST = "WAITLIST"
    TRIAL = "TRIAL"


class RegistrationStatus(StrEnum):
    SUBMITTED = "SUBMITTED"
    VALID = "VALID"
    INVALID = "INVALID"
    WAITLISTED = "WAITLISTED"
    TRANSFERRED = "TRANSFERRED"
    CANCELLED = "CANCELLED"


class PaymentStatus(StrEnum):
    UNPAID = "UNPAID"
    PAID = "PAID"
    PENDING_CONFIRMATION = "PENDING_CONFIRMATION"
    REFUNDED = "REFUNDED"


@dataclass(slots=True)
class Registration:
    registration_id: str
    class_id: str
    user_id: str
    registration_type: RegistrationType
    status: RegistrationStatus
    submitted_at: datetime
    parent_name: str | None = None
    contact_info: str | None = None
    student_name: str | None = None
    student_grade: str | None = None
    english_level: str | None = None
    accept_transfer: bool | None = None
    accept_waitlist: bool | None = None
    wants_trial: bool | None = None
    accept_similar_recommendation: bool | None = None
    remark: str | None = None
    follow_up_note: str | None = None
    notes: str | None = None
    payment_status: PaymentStatus = PaymentStatus.UNPAID
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def create(
        cls,
        *,
        registration_id: str,
        class_id: str,
        user_id: str,
        registration_type: RegistrationType,
        submitted_at: datetime,
        parent_name: str | None = None,
        contact_info: str | None = None,
        student_name: str | None = None,
        student_grade: str | None = None,
        english_level: str | None = None,
        accept_transfer: bool | None = None,
        accept_waitlist: bool | None = None,
        wants_trial: bool | None = None,
        accept_similar_recommendation: bool | None = None,
        remark: str | None = None,
        follow_up_note: str | None = None,
        notes: str | None = None,
    ) -> "Registration":
        if not parent_name:
            raise ValueError("parentName is required")
        if not contact_info:
            raise ValueError("contactInfo is required")
        if registration_type == RegistrationType.ENROLLMENT and not student_name:
            raise ValueError("studentName is required")
        if registration_type == RegistrationType.ENROLLMENT and not student_grade:
            raise ValueError("studentGrade is required")
        if registration_type == RegistrationType.WAITLIST and not student_grade:
            raise ValueError("studentGrade is required")

        status = (
            RegistrationStatus.WAITLISTED
            if registration_type == RegistrationType.WAITLIST
            else RegistrationStatus.SUBMITTED
        )
        return cls(
            registration_id=registration_id,
            class_id=class_id,
            user_id=user_id,
            registration_type=registration_type,
            status=status,
            submitted_at=submitted_at,
            parent_name=parent_name,
            contact_info=contact_info,
            student_name=student_name,
            student_grade=student_grade,
            english_level=english_level,
            accept_transfer=accept_transfer,
            accept_waitlist=accept_waitlist,
            wants_trial=wants_trial,
            accept_similar_recommendation=accept_similar_recommendation,
            remark=remark,
            follow_up_note=follow_up_note,
            notes=notes,
            payment_status=PaymentStatus.UNPAID,
            created_at=submitted_at,
            updated_at=submitted_at,
        )
