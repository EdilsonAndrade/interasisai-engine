import pytest
from pydantic import ValidationError

from presentation.schemas import ChatProcessResponseSchema


def test_response_schema_accepts_success_payload() -> None:
    schema = ChatProcessResponseSchema.model_validate(
        {
            "status": "success",
            "source": "cache_miss",
            "message": {
                "text": "ok",
                "audio": {
                    "mime_type": "audio/mpeg",
                    "encoding": "base64",
                    "content": "abc",
                },
            },
            "transcription": None,
            "audio_unavailable": False,
            "metadata": {
                "request_id": "rid-123",
                "similarity_score": None,
                "threshold": 0.85,
                "latency_ms": 10,
            },
        }
    )

    assert schema.status == "success"
    assert schema.message.audio.encoding == "base64"


def test_response_schema_rejects_unknown_status() -> None:
    with pytest.raises(ValidationError):
        ChatProcessResponseSchema.model_validate(
            {
                "status": "weird",
                "source": "cache_miss",
                "message": {
                    "text": "ok",
                    "audio": {
                        "mime_type": "audio/mpeg",
                        "encoding": "base64",
                        "content": "abc",
                    },
                },
                "audio_unavailable": False,
                "metadata": {
                    "request_id": "rid-123",
                    "threshold": 0.85,
                    "latency_ms": 10,
                },
            }
        )


def test_response_schema_rejects_empty_message_text() -> None:
    with pytest.raises(ValidationError):
        ChatProcessResponseSchema.model_validate(
            {
                "status": "success",
                "source": "cache_miss",
                "message": {
                    "text": "",
                    "audio": {
                        "mime_type": "audio/mpeg",
                        "encoding": "base64",
                        "content": "abc",
                    },
                },
                "audio_unavailable": False,
                "metadata": {
                    "request_id": "rid-123",
                    "threshold": 0.85,
                    "latency_ms": 10,
                },
            }
        )


def test_response_schema_rejects_unknown_source() -> None:
    with pytest.raises(ValidationError):
        ChatProcessResponseSchema.model_validate(
            {
                "status": "success",
                "source": "external_provider",
                "message": {
                    "text": "ok",
                    "audio": {
                        "mime_type": "audio/mpeg",
                        "encoding": "base64",
                        "content": "abc",
                    },
                },
                "audio_unavailable": False,
                "metadata": {
                    "request_id": "rid-123",
                    "threshold": 0.85,
                    "latency_ms": 10,
                },
            }
        )
