from tests.fixtures.test_data import VALID_SECRET


def test_api_still_works_with_di_wiring(client) -> None:
    response = client.post(
        "/api/v1/ai/consult",
        headers={"X-Internal-Secret": VALID_SECRET},
        json={"message": "wired"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "wired"
