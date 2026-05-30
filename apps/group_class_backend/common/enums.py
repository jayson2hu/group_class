from __future__ import annotations

from enum import StrEnum


class ClassStatus(StrEnum):
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    OPEN_FOR_ENROLLMENT = "OPEN_FOR_ENROLLMENT"
    ALMOST_CONFIRMED = "ALMOST_CONFIRMED"
    CONFIRMED = "CONFIRMED"
    FULL = "FULL"
    WAITLIST_OPEN = "WAITLIST_OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    ENDED = "ENDED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class Action(StrEnum):
    VIEW = "view"
    EDIT = "edit"
    SUBMIT_REVIEW = "submit_review"
    APPROVE = "approve"
    REJECT = "reject"
    PUBLISH = "publish"
    CANCEL = "cancel"


_DEFAULT_ACTIONS_BY_STATUS: dict[ClassStatus, list[Action]] = {
    ClassStatus.DRAFT: [
        Action.VIEW,
        Action.EDIT,
        Action.SUBMIT_REVIEW,
    ],
    ClassStatus.PENDING_REVIEW: [
        Action.VIEW,
    ],
    ClassStatus.REJECTED: [
        Action.VIEW,
        Action.EDIT,
        Action.SUBMIT_REVIEW,
    ],
    ClassStatus.OPEN_FOR_ENROLLMENT: [
        Action.VIEW,
        Action.CANCEL,
    ],
    ClassStatus.ALMOST_CONFIRMED: [
        Action.VIEW,
        Action.CANCEL,
    ],
    ClassStatus.CONFIRMED: [
        Action.VIEW,
        Action.CANCEL,
    ],
    ClassStatus.FULL: [
        Action.VIEW,
        Action.CANCEL,
    ],
    ClassStatus.WAITLIST_OPEN: [
        Action.VIEW,
        Action.CANCEL,
    ],
    ClassStatus.IN_PROGRESS: [
        Action.VIEW,
        Action.CANCEL,
    ],
}


def default_actions_for_status(status: ClassStatus) -> list[Action]:
    return list(_DEFAULT_ACTIONS_BY_STATUS.get(status, [Action.VIEW]))
