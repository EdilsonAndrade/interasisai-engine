from tests.fixtures.test_data import (
    CHAT_PROCESS_PATH,
    SAMPLE_AUDIO_CONTENT_TYPE,
    SAMPLE_AUDIO_FILENAME,
    VALID_SECRET,
)



def test_chat_voice_input_returns_transcription_and_multimodal_payload(client) -> None:
    response = client.post(
        CHAT_PROCESS_PATH,
        headers={"X-Internal-Secret": VALID_SECRET},
        files={"audio": (SAMPLE_AUDIO_FILENAME, b"TEXT: preciso consultar meu plano", SAMPLE_AUDIO_CONTENT_TYPE)},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["transcription"] == "preciso consultar meu plano"
    assert body["message"]["text"]
    assert body["message"]["audio"]["encoding"] == "base64"


def test_chat_voice_input_returns_422_when_transcription_confidence_is_low(client) -> None:
    response = client.post(
        CHAT_PROCESS_PATH,
        headers={"X-Internal-Secret": VALID_SECRET},
        files={"audio": (SAMPLE_AUDIO_FILENAME, b"LOW_CONF ruido", SAMPLE_AUDIO_CONTENT_TYPE)},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["status"] == "error"
    assert body["code"] == "TRANSCRIPTION_FAILED"
