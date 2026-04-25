from tests.fixtures.test_data import CHAT_PROCESS_PATH, VALID_SECRET



def test_chat_response_returns_text_and_audio_shape(client) -> None:
    response = client.post(
        CHAT_PROCESS_PATH,
        headers={"X-Internal-Secret": VALID_SECRET},
        data={"text": "Preciso de ajuda com meu cadastro"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["message"]["text"]
    assert body["message"]["audio"]["mime_type"] == "audio/mpeg"
    assert body["message"]["audio"]["encoding"] == "base64"
    assert "audio_unavailable" in body
