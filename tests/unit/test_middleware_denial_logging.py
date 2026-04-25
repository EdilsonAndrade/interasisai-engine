from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import Request

from infra.config.settings import Environment, Settings
from infra.security.secret_validator import SecretValidator
from presentation.middleware.security_middleware import SecurityMiddleware


def _build_request(secret_header: bytes | None) -> Request:
    headers = []
    if secret_header is not None:
        headers.append((b"x-internal-secret", secret_header))
    return Request(
        scope={
            "type": "http",
            "method": "POST",
            "path": "/api/v1/chat/process",
            "headers": headers,
            "query_string": b"",
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
            "scheme": "http",
            "http_version": "1.1",
            "app": SimpleNamespace(state=SimpleNamespace()),
        }
    )


class _Logger:
    def __init__(self) -> None:
        self.warnings: list[str] = []

    def info(self, message: str) -> None:  # pragma: no cover - not exercised here
        pass

    def warning(self, message: str) -> None:
        self.warnings.append(message)

    def error(self, message: str) -> None:  # pragma: no cover - not exercised here
        pass


def _settings() -> Settings:
    return Settings(
        x_internal_secret="valid",
        log_level="INFO",
        app_name="test",
        environment=Environment.TESTING,
    )


@pytest.mark.asyncio
async def test_middleware_logs_missing_header_denial() -> None:
    logger = _Logger()
    middleware = SecurityMiddleware(validator=SecretValidator(_settings()), logger=logger)

    response = await middleware(_build_request(None), AsyncMock())

    assert response.status_code == 403
    assert any("reason=missing_header" in msg for msg in logger.warnings)
    assert any("path=/api/v1/chat/process" in msg for msg in logger.warnings)


@pytest.mark.asyncio
async def test_middleware_logs_invalid_secret_denial() -> None:
    logger = _Logger()
    middleware = SecurityMiddleware(validator=SecretValidator(_settings()), logger=logger)

    response = await middleware(_build_request(b"wrong"), AsyncMock())

    assert response.status_code == 403
    assert any("reason=invalid_secret" in msg for msg in logger.warnings)


@pytest.mark.asyncio
async def test_middleware_does_not_log_when_authorized() -> None:
    logger = _Logger()
    middleware = SecurityMiddleware(validator=SecretValidator(_settings()), logger=logger)

    call_next = AsyncMock(return_value=SimpleNamespace(status_code=200))
    response = await middleware(_build_request(b"valid"), call_next)

    assert response.status_code == 200
    assert logger.warnings == []
