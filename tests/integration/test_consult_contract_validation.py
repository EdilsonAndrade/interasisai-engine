from tests.fixtures.test_data import LONG_MESSAGE, VALID_SECRET


def test_empty_message_returns_422(client) -> None:
    response = client.post(
        "/api/v1/ai/consult",
        headers={"X-Internal-Secret": VALID_SECRET},
        json={"message": ""},
    )

    assert response.status_code == 422


def test_too_long_message_returns_422(client) -> None:
    response = client.post(
        "/api/v1/ai/consult",
        headers={"X-Internal-Secret": VALID_SECRET},
        json={"message": LONG_MESSAGE},
    )

    assert response.status_code == 422


def test_success_response_has_iso_timestamp(client) -> None:
    response = client.post(
        "/api/v1/ai/consult",
        headers={"X-Internal-Secret": VALID_SECRET},
        json={"message": "timestamp-check"},
    )

    assert response.status_code == 200
    assert "T" in response.json()["timestamp"]
