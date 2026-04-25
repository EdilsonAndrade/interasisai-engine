from tests.fixtures.test_data import CHAT_PROCESS_PATH, VALID_SECRET



def _headers() -> dict[str, str]:
    return {"X-Internal-Secret": VALID_SECRET}



def test_chat_cache_flow_first_call_miss_second_call_hit(client) -> None:
    first = client.post(
        CHAT_PROCESS_PATH,
        headers=_headers(),
        data={"text": "Quais sao os horarios de atendimento?"},
    )
    second = client.post(
        CHAT_PROCESS_PATH,
        headers=_headers(),
        data={"text": "Quais sao os horarios de atendimento?"},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["source"] == "cache_miss"
    assert second.json()["source"] == "cache_hit"
    assert second.json()["metadata"]["similarity_score"] is not None
