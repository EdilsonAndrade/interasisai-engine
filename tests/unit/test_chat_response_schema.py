import pytest
from pydantic import ValidationError

from presentation.schemas import ChatProcessResponseSchema



def test_chat_response_schema_accepts_multimodal_success() -> None:
    payload = ChatProcessResponseSchema.model_validate(
        {
            "status": "success",
            "source": "cache_hit",
            "message": {
                "text": "Resposta em texto",
                "audio": {
                    "mime_type": "audio/mpeg",
                    "encoding": "base64",
                    "content": "YWJj",
                    "duration_ms": 1000,
                },
            },
            "transcription": None,
            "audio_unavailable": False,
            "metadata": {
                "request_id": "rid-1",
                "similarity_score": 0.9,
                "threshold": 0.85,
                "latency_ms": 120,
            },
        }
    )

    assert payload.source == "cache_hit"
    assert payload.message.audio.encoding == "base64"


def test_chat_response_schema_rejects_invalid_source() -> None:
    with pytest.raises(ValidationError):
        ChatProcessResponseSchema.model_validate(
            {
                "status": "success",
                "source": "llm",
                "message": {
                    "text": "Resposta em texto",
                    "audio": {
                        "mime_type": "audio/mpeg",
                        "encoding": "base64",
                        "content": "YWJj",
                    },
                },
                "audio_unavailable": False,
                "metadata": {
                    "request_id": "rid-1",
                    "threshold": 0.85,
                    "latency_ms": 120,
                },
            }
        )
