import pytest
from pydantic import ValidationError

from presentation.schemas import ChatProcessReceivedSchema, ChatProcessResponseSchema


def test_response_schema_accepts_success_payload() -> None:
    schema = ChatProcessResponseSchema(
        status="success",
        agent_reply="ok",
        received=ChatProcessReceivedSchema(has_text=True, has_audio=False),
    )

    assert schema.status == "success"
    assert schema.received.has_audio is False


def test_response_schema_rejects_unknown_status() -> None:
    with pytest.raises(ValidationError):
        ChatProcessResponseSchema(
            status="weird",
            agent_reply="ok",
            received=ChatProcessReceivedSchema(has_text=True, has_audio=False),
        )


def test_response_schema_rejects_empty_agent_reply() -> None:
    with pytest.raises(ValidationError):
        ChatProcessResponseSchema(
            status="success",
            agent_reply="",
            received=ChatProcessReceivedSchema(has_text=True, has_audio=False),
        )


def test_received_schema_defaults_optional_fields_to_none() -> None:
    received = ChatProcessReceivedSchema(has_text=True, has_audio=False)

    assert received.audio_filename is None
    assert received.session_id is None
