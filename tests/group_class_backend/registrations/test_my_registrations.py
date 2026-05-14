from datetime import datetime, timezone

from apps.group_class_backend.classes.repository import InMemoryClassRepository
from apps.group_class_backend.models.group_class import GroupClass
from apps.group_class_backend.models.registration import Registration, RegistrationType
from apps.group_class_backend.registrations.controller import cancel_my_registration, list_my_registrations, update_my_registration
from apps.group_class_backend.registrations.repository import InMemoryRegistrationRepository


def test_list_my_registrations_only_returns_current_actor_items() -> None:
    class_repository = InMemoryClassRepository()
    registration_repository = InMemoryRegistrationRepository()
    now = datetime(2026, 5, 14, 12, 0, tzinfo=timezone.utc)
    group_class = GroupClass.create_draft(
        created_at=now,
        creator_id="u_admin",
        class_name="My Class",
        class_type="GROUP_CLASS",
        min_students=2,
        max_students=6,
    )
    class_repository.save(group_class)
    registration_repository.save(
        Registration.create(
            registration_id="reg-mine",
            class_id=group_class.class_id,
            user_id="u_parent",
            registration_type=RegistrationType.ENROLLMENT,
            submitted_at=now,
            parent_name="Parent",
            contact_info="13800138000",
            student_name="Student",
            student_grade="三年级",
        )
    )
    registration_repository.save(
        Registration.create(
            registration_id="reg-other",
            class_id=group_class.class_id,
            user_id="u_other",
            registration_type=RegistrationType.ENROLLMENT,
            submitted_at=now,
            parent_name="Other",
            contact_info="13900139000",
            student_name="Other Student",
            student_grade="四年级",
        )
    )

    result = list_my_registrations(
        class_repository=class_repository,
        registration_repository=registration_repository,
        request_id="req-test",
        actor_id="u_parent",
    )

    assert result["code"] == "OK"
    assert [item["registrationId"] for item in result["data"]["items"]] == ["reg-mine"]


def test_update_and_cancel_my_registration_require_owner() -> None:
    class_repository = InMemoryClassRepository()
    registration_repository = InMemoryRegistrationRepository()
    now = datetime(2026, 5, 14, 12, 0, tzinfo=timezone.utc)
    group_class = GroupClass.create_draft(
        created_at=now,
        creator_id="u_admin",
        class_name="My Class",
        class_type="GROUP_CLASS",
        min_students=2,
        max_students=6,
    )
    class_repository.save(group_class)
    registration_repository.save(
        Registration.create(
            registration_id="reg-mine",
            class_id=group_class.class_id,
            user_id="u_parent",
            registration_type=RegistrationType.ENROLLMENT,
            submitted_at=now,
            parent_name="Parent",
            contact_info="13800138000",
            student_name="Student",
            student_grade="三年级",
        )
    )

    updated = update_my_registration(
        registration_id="reg-mine",
        payload={"parentName": "Updated Parent", "studentName": "Updated Student"},
        class_repository=class_repository,
        registration_repository=registration_repository,
        request_id="req-update",
        actor_id="u_parent",
        now=now,
    )
    denied = cancel_my_registration(
        registration_id="reg-mine",
        class_repository=class_repository,
        registration_repository=registration_repository,
        request_id="req-denied",
        actor_id="u_other",
        now=now,
    )
    cancelled = cancel_my_registration(
        registration_id="reg-mine",
        class_repository=class_repository,
        registration_repository=registration_repository,
        request_id="req-cancel",
        actor_id="u_parent",
        now=now,
    )

    assert updated["data"]["parentName"] == "Updated Parent"
    assert updated["data"]["studentName"] == "Updated Student"
    assert denied["code"] == "CLASS_NOT_FOUND"
    assert cancelled["data"]["registrationStatus"] == "CANCELLED"
