from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import Request

from infra.config.settings import Environment, Settings
from infra.security.secret_validator import SecretValidator
from presentation.middleware.security_middleware import SecurityMiddleware


@pytest.mark.asyncio
async def test_security_middleware_allows_valid_secret() -> None:
    settings = Settings(
        x_internal_secret="valid",
        log_level="INFO",
        app_name="test",
        environment=Environment.TESTING,
    )
    middleware = SecurityMiddleware(validator=SecretValidator(settings))

    request = Request(
        scope={
            "type": "http",
            "method": "POST",
            "path": "/api/v1/ai/consult",
            "headers": [(b"x-internal-secret", b"valid")],
            "query_string": b"",
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
            "scheme": "http",
            "http_version": "1.1",
            "app": SimpleNamespace(state=SimpleNamespace()),
        }
    )

    call_next = AsyncMock()
    call_next.return_value = SimpleNamespace(status_code=200)

    response = await middleware(request, call_next)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_security_middleware_blocks_invalid_secret() -> None:
    settings = Settings(
        x_internal_secret="valid",
        log_level="INFO",
        app_name="test",
        environment=Environment.TESTING,
    )
    middleware = SecurityMiddleware(validator=SecretValidator(settings))

    request = Request(
        scope={
            "type": "http",
            "method": "POST",
            "path": "/api/v1/ai/consult",
            "headers": [(b"x-internal-secret", b"invalid")],
            "query_string": b"",
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
            "scheme": "http",
            "http_version": "1.1",
            "app": SimpleNamespace(state=SimpleNamespace()),
        }
    )

    call_next = AsyncMock()
    response = await middleware(request, call_next)

    assert response.status_code == 403
    call_next.assert_not_called()
