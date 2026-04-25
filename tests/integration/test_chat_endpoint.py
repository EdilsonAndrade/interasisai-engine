from tests.fixtures.test_data import (
    CHAT_PROCESS_PATH,
    EXPECTED_AGENT_REPLY,
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
    assert body["agent_reply"] == EXPECTED_AGENT_REPLY
    assert body["received"] == {
        "has_text": True,
        "has_audio": False,
        "audio_filename": None,
        "session_id": "session-1",
    }


def test_chat_process_with_audio_only_returns_simulated_success(client) -> None:
    response = client.post(
        CHAT_PROCESS_PATH,
        headers=_auth_headers(),
        files={"audio": (SAMPLE_AUDIO_FILENAME, SAMPLE_AUDIO_BYTES, SAMPLE_AUDIO_CONTENT_TYPE)},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["received"]["has_text"] is False
    assert body["received"]["has_audio"] is True
    assert body["received"]["audio_filename"] == SAMPLE_AUDIO_FILENAME


def test_chat_process_with_text_and_audio_returns_success(client) -> None:
    response = client.post(
        CHAT_PROCESS_PATH,
        headers=_auth_headers(),
        data={"text": SAMPLE_CHAT_TEXT},
        files={"audio": (SAMPLE_AUDIO_FILENAME, SAMPLE_AUDIO_BYTES, SAMPLE_AUDIO_CONTENT_TYPE)},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["received"]["has_text"] is True
    assert body["received"]["has_audio"] is True


def test_chat_process_without_text_or_audio_returns_422(client) -> None:
    response = client.post(CHAT_PROCESS_PATH, headers=_auth_headers(), data={})

    assert response.status_code == 422
    assert "text" in response.json()["detail"].lower()


def test_chat_process_rejects_non_audio_content_type(client) -> None:
    response = client.post(
        CHAT_PROCESS_PATH,
        headers=_auth_headers(),
        files={"audio": ("not-audio.txt", b"plain", "text/plain")},
    )

    assert response.status_code == 422
    assert "audio" in response.json()["detail"].lower()
