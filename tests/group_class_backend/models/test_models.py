from datetime import datetime, timedelta, timezone

import pytest

from apps.group_class_backend.common.enums import ClassStatus
from apps.group_class_backend.models.class_template import ClassTemplate
from apps.group_class_backend.models.group_class import GroupClass
from apps.group_class_backend.models.registration import Registration, RegistrationStatus, RegistrationType


def test_group_class_defaults_to_draft_with_version_one() -> None:
    now = datetime.now(timezone.utc)

    group_class = GroupClass.create_draft(
        class_name="周末拼课",
        creator_id="initiator-001",
        created_at=now,
    )

    assert group_class.status == ClassStatus.DRAFT
    assert group_class.version == 1
    assert group_class.current_students == 0
    assert group_class.waitlist_count == 0


@pytest.mark.parametrize(
    ("payload", "field"),
    [
        ({"class_name": None, "template_id": None}, "className"),
        ({"class_name": "周末拼课", "min_students": 0}, "minStudents"),
        ({"class_name": "周末拼课", "min_students": 5, "max_students": 3}, "maxStudents"),
        ({"class_name": "周末拼课", "price_amount": 100, "deposit_amount": 101}, "depositAmount"),
    ],
)
def test_group_class_create_draft_validates_frozen_constraints(payload: dict, field: str) -> None:
    now = datetime.now(timezone.utc)

    with pytest.raises(ValueError) as exc:
        GroupClass.create_draft(created_at=now, creator_id="initiator-001", **payload)

    assert field in str(exc.value)



def test_group_class_validates_temporal_constraints() -> None:
    now = datetime.now(timezone.utc)

    with pytest.raises(ValueError, match="endDate"):
        GroupClass.create_draft(
            class_name="晚课",
            creator_id="initiator-001",
            created_at=now,
            start_date=now + timedelta(days=2),
            end_date=now + timedelta(days=1),
        )

    with pytest.raises(ValueError, match="signupDeadline"):
        GroupClass.create_draft(
            class_name="晚课",
            creator_id="initiator-001",
            created_at=now,
            start_date=now + timedelta(days=2),
            signup_deadline=now + timedelta(days=3),
        )



def test_registration_supports_batch1_foundation_fields() -> None:
    now = datetime.now(timezone.utc)

    registration = Registration(
        registration_id="reg-001",
        class_id="cls-001",
        user_id="usr-001",
        registration_type=RegistrationType.ENROLLMENT,
        status=RegistrationStatus.SUBMITTED,
        submitted_at=now,
    )

    assert registration.registration_id == "reg-001"
    assert registration.registration_type == RegistrationType.ENROLLMENT
    assert registration.status == RegistrationStatus.SUBMITTED
    assert registration.notes is None



def test_registration_supports_batch4_enrollment_and_waitlist_fields() -> None:
    now = datetime.now(timezone.utc)

    enrollment = Registration.create(
        registration_id="reg-002",
        class_id="cls-001",
        user_id="usr-001",
        registration_type=RegistrationType.ENROLLMENT,
        submitted_at=now,
        parent_name="张女士",
        contact_info="13800000000",
        student_name="张三",
        student_grade="三年级",
        english_level="基础一般",
        accept_transfer=True,
        accept_waitlist=True,
        wants_trial=False,
        remark="希望同校同学一起",
    )
    waitlist = Registration.create(
        registration_id="reg-003",
        class_id="cls-001",
        user_id="usr-002",
        registration_type=RegistrationType.WAITLIST,
        submitted_at=now,
        parent_name="李女士",
        contact_info="13900000000",
        student_grade="四年级",
        accept_similar_recommendation=True,
        remark="可接受相近时间段",
    )

    assert enrollment.parent_name == "张女士"
    assert enrollment.contact_info == "13800000000"
    assert enrollment.student_name == "张三"
    assert enrollment.student_grade == "三年级"
    assert enrollment.english_level == "基础一般"
    assert enrollment.accept_transfer is True
    assert enrollment.accept_waitlist is True
    assert enrollment.wants_trial is False
    assert enrollment.accept_similar_recommendation is None
    assert waitlist.registration_type == RegistrationType.WAITLIST
    assert waitlist.status == RegistrationStatus.WAITLISTED
    assert waitlist.parent_name == "李女士"
    assert waitlist.student_name is None
    assert waitlist.accept_similar_recommendation is True


@pytest.mark.parametrize(
    ("registration_type", "payload", "field"),
    [
        (
            RegistrationType.ENROLLMENT,
            {
                "parent_name": "张女士",
                "contact_info": "13800000000",
                "student_grade": "三年级",
            },
            "studentName",
        ),
        (
            RegistrationType.ENROLLMENT,
            {
                "parent_name": "张女士",
                "contact_info": "13800000000",
                "student_name": "张三",
            },
            "studentGrade",
        ),
        (
            RegistrationType.WAITLIST,
            {
                "contact_info": "13900000000",
                "student_grade": "四年级",
            },
            "parentName",
        ),
    ],
)
def test_registration_create_validates_batch4_required_fields(
    registration_type: RegistrationType, payload: dict[str, object], field: str
) -> None:
    now = datetime.now(timezone.utc)

    with pytest.raises(ValueError, match=field):
        Registration.create(
            registration_id="reg-invalid",
            class_id="cls-001",
            user_id="usr-001",
            registration_type=registration_type,
            submitted_at=now,
            **payload,
        )



def test_class_template_supports_batch1_foundation_fields() -> None:
    now = datetime.now(timezone.utc)

    template = ClassTemplate(
        template_id="tpl-001",
        template_name="瑜伽基础模板",
        class_type="YOGA",
        default_price_amount=199,
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    assert template.template_id == "tpl-001"
    assert template.template_name == "瑜伽基础模板"
    assert template.default_price_amount == 199
    assert template.is_active is True
