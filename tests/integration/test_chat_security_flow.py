from tests.fixtures.test_data import (
    CHAT_PROCESS_PATH,
    INVALID_SECRET,
    SAMPLE_AUDIO_BYTES,
    SAMPLE_AUDIO_CONTENT_TYPE,
    SAMPLE_AUDIO_FILENAME,
    SAMPLE_CHAT_TEXT,
    VALID_SECRET,
)


def test_chat_process_forbidden_without_secret(client) -> None:
    response = client.post(CHAT_PROCESS_PATH, data={"text": SAMPLE_CHAT_TEXT})

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}


def test_chat_process_forbidden_with_invalid_secret(client) -> None:
    response = client.post(
        CHAT_PROCESS_PATH,
        headers={"X-Internal-Secret": INVALID_SECRET},
        data={"text": SAMPLE_CHAT_TEXT},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}


def test_chat_process_authorized_request_reaches_handler(client) -> None:
    response = client.post(
        CHAT_PROCESS_PATH,
        headers={"X-Internal-Secret": VALID_SECRET},
        data={"text": SAMPLE_CHAT_TEXT},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["message"]["text"]
    assert body["source"] in {"cache_hit", "cache_miss"}


def test_chat_process_forbidden_when_audio_only_without_secret(client) -> None:
    response = client.post(
        CHAT_PROCESS_PATH,
        files={"audio": (SAMPLE_AUDIO_FILENAME, SAMPLE_AUDIO_BYTES, SAMPLE_AUDIO_CONTENT_TYPE)},
    )

    assert response.status_code == 403


def test_chat_process_forbidden_when_multipart_text_without_secret(client) -> None:
    response = client.post(
        CHAT_PROCESS_PATH,
        files={"text": (None, "pergunta sem segredo")},
    )

    assert response.status_code == 403


def test_chat_process_forbidden_when_multipart_audio_with_invalid_secret(client) -> None:
    response = client.post(
        CHAT_PROCESS_PATH,
        headers={"X-Internal-Secret": INVALID_SECRET},
        files={"audio": (SAMPLE_AUDIO_FILENAME, SAMPLE_AUDIO_BYTES, SAMPLE_AUDIO_CONTENT_TYPE)},
    )

    assert response.status_code == 403
