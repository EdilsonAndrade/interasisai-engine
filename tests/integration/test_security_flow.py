from tests.fixtures.test_data import INVALID_SECRET, VALID_MESSAGE, VALID_SECRET


def test_request_without_secret_is_forbidden(client) -> None:
    response = client.post("/api/v1/ai/consult", json={"message": VALID_MESSAGE})
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}


def test_request_with_invalid_secret_is_forbidden(client) -> None:
    response = client.post(
        "/api/v1/ai/consult",
        headers={"X-Internal-Secret": INVALID_SECRET},
        json={"message": VALID_MESSAGE},
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}


def test_request_with_valid_secret_is_allowed(client) -> None:
    response = client.post(
        "/api/v1/ai/consult",
        headers={"X-Internal-Secret": VALID_SECRET},
        json={"message": VALID_MESSAGE},
    )
    assert response.status_code == 200
    assert response.json()["message"] == VALID_MESSAGE
