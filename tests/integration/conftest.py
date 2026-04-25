from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from infra.config.settings import Environment, Settings
from presentation.main import create_app
from tests.fixtures.test_data import VALID_SECRET


@pytest.fixture
def settings() -> Settings:
    return Settings(
        x_internal_secret=VALID_SECRET,
        log_level="DEBUG",
        app_name="InterasisAI-Engine-Test",
        environment=Environment.TESTING,
    )


@pytest.fixture
def client(settings: Settings, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setenv("X_INTERNAL_SECRET", settings.x_internal_secret)
    monkeypatch.setenv("LOG_LEVEL", settings.log_level)
    monkeypatch.setenv("APP_NAME", settings.app_name)
    monkeypatch.setenv("ENVIRONMENT", settings.environment.value)

    app = create_app(settings_override=settings)
    with TestClient(app) as test_client:
        yield test_client
