from tests.fixtures.test_data import (
    CHAT_PROCESS_PATH,
    SAMPLE_AUDIO_BYTES,
    SAMPLE_AUDIO_CONTENT_TYPE,
    SAMPLE_AUDIO_FILENAME,
    SAMPLE_CHAT_TEXT,
    VALID_SECRET,
)


def _auth_headers() -> dict:
    return {"X-Internal-Secret": VALID_SECRET}


def test_chat_process_with_text_only_returns_simulated_success(client) -> None:
    response = client.post(
        CHAT_PROCESS_PATH,
        headers=_auth_headers(),
        data={"text": SAMPLE_CHAT_TEXT, "session_id": "session-1"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["source"] == "cache_miss"
    assert body["message"]["text"]
    assert body["message"]["audio"]["encoding"] == "base64"
    assert body["audio_unavailable"] is False


def test_chat_process_with_audio_only_returns_simulated_success(client) -> None:
    response = client.post(
        CHAT_PROCESS_PATH,
        headers=_auth_headers(),
        files={"audio": (SAMPLE_AUDIO_FILENAME, SAMPLE_AUDIO_BYTES, SAMPLE_AUDIO_CONTENT_TYPE)},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["transcription"] is not None
    assert body["message"]["audio"]["mime_type"] == "audio/mpeg"


def test_chat_process_with_text_and_audio_returns_success(client) -> None:
    response = client.post(
        CHAT_PROCESS_PATH,
        headers=_auth_headers(),
        data={"text": SAMPLE_CHAT_TEXT},
        files={"audio": (SAMPLE_AUDIO_FILENAME, SAMPLE_AUDIO_BYTES, SAMPLE_AUDIO_CONTENT_TYPE)},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["message"]["text"]
    assert body["message"]["audio"]["content"]


def test_chat_process_without_text_or_audio_returns_422(client) -> None:
    response = client.post(CHAT_PROCESS_PATH, headers=_auth_headers(), data={})

    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_INPUT"


def test_chat_process_rejects_non_audio_content_type(client) -> None:
    response = client.post(
        CHAT_PROCESS_PATH,
        headers=_auth_headers(),
        files={"audio": ("not-audio.txt", b"plain", "text/plain")},
    )

    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_INPUT"
