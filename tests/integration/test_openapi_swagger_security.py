from presentation.openapi import (
    API_DESCRIPTION,
    API_TITLE,
    API_VERSION,
    INTERNAL_SECRET_HEADER,
    TAG_AI,
    TAG_CHAT,
)


def _openapi(client) -> dict:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    return response.json()


def test_openapi_publishes_api_metadata(client) -> None:
    spec = _openapi(client)
    info = spec["info"]

    assert info["title"] == API_TITLE
    assert info["version"] == API_VERSION
    assert info["description"] == API_DESCRIPTION


def test_openapi_publishes_functional_tags(client) -> None:
    spec = _openapi(client)
    tag_names = {tag["name"] for tag in spec.get("tags", [])}

    assert TAG_CHAT in tag_names
    assert TAG_AI in tag_names


def test_openapi_publishes_internal_secret_security_scheme(client) -> None:
    spec = _openapi(client)
    schemes = spec.get("components", {}).get("securitySchemes", {})

    assert any(
        scheme.get("type") == "apiKey"
        and scheme.get("in") == "header"
        and scheme.get("name") == INTERNAL_SECRET_HEADER
        for scheme in schemes.values()
    ), "Esquema APIKeyHeader X-Internal-Secret deve estar publicado no OpenAPI"


def test_openapi_protected_routes_reference_internal_secret_security(client) -> None:
    spec = _openapi(client)
    chat_op = spec["paths"]["/api/v1/chat/process"]["post"]
    consult_op = spec["paths"]["/api/v1/ai/consult"]["post"]

    chat_security_keys = {key for entry in chat_op.get("security", []) for key in entry.keys()}
    consult_security_keys = {key for entry in consult_op.get("security", []) for key in entry.keys()}

    assert chat_security_keys, "Endpoint de chat protegido deve declarar security no OpenAPI"
    assert consult_security_keys, "Endpoint de consult protegido deve declarar security no OpenAPI"


def test_openapi_protected_routes_use_functional_tags(client) -> None:
    spec = _openapi(client)
    chat_op = spec["paths"]["/api/v1/chat/process"]["post"]
    consult_op = spec["paths"]["/api/v1/ai/consult"]["post"]

    assert TAG_CHAT in chat_op.get("tags", [])
    assert TAG_AI in consult_op.get("tags", [])


def test_swagger_ui_is_accessible(client) -> None:
    response = client.get("/docs")

    assert response.status_code == 200
    assert "swagger" in response.text.lower()
