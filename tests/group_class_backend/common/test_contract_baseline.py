from apps.group_class_backend.audit.interface import AuditEvent, NullAuditWriter
from apps.group_class_backend.common.enums import Action, ClassStatus, default_actions_for_status
from apps.group_class_backend.common.error_codes import ErrorCode
from apps.group_class_backend.common.request_context import build_request_context
from apps.group_class_backend.common.responses import error_response, success_response


def test_error_codes_freeze_for_batch1_contract() -> None:
    assert ErrorCode.OK == "OK"
    assert ErrorCode.VALIDATION_INVALID_ARGUMENT == "VALIDATION_INVALID_ARGUMENT"
    assert ErrorCode.VALIDATION_REQUIRED_FIELD_MISSING == "VALIDATION_REQUIRED_FIELD_MISSING"
    assert ErrorCode.CLASS_NOT_FOUND == "CLASS_NOT_FOUND"
    assert ErrorCode.CLASS_VERSION_CONFLICT == "CLASS_VERSION_CONFLICT"
    assert ErrorCode.PERMISSION_DENIED == "PERMISSION_DENIED"
    assert ErrorCode.SYSTEM_INTERNAL_ERROR == "SYSTEM_INTERNAL_ERROR"



def test_success_response_uses_frozen_shape() -> None:
    response = success_response(request_id="req-001", data={"classId": "cls-001"})

    assert response == {
        "requestId": "req-001",
        "code": "OK",
        "data": {"classId": "cls-001"},
    }
    assert "details" not in response



def test_error_response_uses_frozen_shape() -> None:
    response = error_response(
        request_id="req-001",
        code=ErrorCode.VALIDATION_INVALID_ARGUMENT,
        details=[{"field": "minStudents", "message": "must be greater than 0"}],
    )

    assert response == {
        "requestId": "req-001",
        "code": "VALIDATION_INVALID_ARGUMENT",
        "details": [{"field": "minStudents", "message": "must be greater than 0"}],
    }
    assert "data" not in response



def test_request_context_generates_or_preserves_request_id() -> None:
    generated = build_request_context()
    assert generated.request_id.startswith("req-")

    preserved = build_request_context(request_id="req-fixed")
    assert preserved.request_id == "req-fixed"



def test_draft_default_actions_match_contract() -> None:
    assert default_actions_for_status(ClassStatus.DRAFT) == [
        Action.VIEW,
        Action.EDIT,
        Action.SUBMIT_REVIEW,
    ]



def test_null_audit_writer_accepts_event() -> None:
    writer = NullAuditWriter()
    event = AuditEvent(
        request_id="req-001",
        actor_id="system",
        action="class.created",
        resource_type="class",
        resource_id="cls-001",
        metadata={"status": "DRAFT"},
    )

    writer.record(event)
