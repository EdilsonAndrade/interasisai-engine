from tests.fixtures.test_data import VALID_SECRET


def test_consult_happy_path_returns_echo(client) -> None:
    response = client.post(
        "/api/v1/ai/consult",
        headers={"X-Internal-Secret": VALID_SECRET},
        json={"message": "hello"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "hello"
    assert "timestamp" in payload


def test_consult_forbidden_without_secret(client) -> None:
    response = client.post("/api/v1/ai/consult", json={"message": "hello"})

    assert response.status_code == 403
