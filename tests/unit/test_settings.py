import os

import pytest

from domain.exceptions import ConfigurationError
from infra.config.settings import Environment, load_settings


def test_load_settings_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("X_INTERNAL_SECRET", "abc")
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    monkeypatch.setenv("APP_NAME", "Test")
    monkeypatch.setenv("ENVIRONMENT", "testing")

    settings = load_settings()

    assert settings.x_internal_secret == "abc"
    assert settings.environment == Environment.TESTING


def test_load_settings_fails_without_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("X_INTERNAL_SECRET", raising=False)

    with pytest.raises(ConfigurationError):
        load_settings()


def test_load_settings_fails_with_invalid_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("X_INTERNAL_SECRET", "abc")
    monkeypatch.setenv("ENVIRONMENT", "invalid")

    with pytest.raises(ConfigurationError):
        load_settings()


def test_load_settings_fails_with_invalid_log_level(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("X_INTERNAL_SECRET", "abc")
    monkeypatch.setenv("LOG_LEVEL", "BOGUS")

    with pytest.raises(ConfigurationError):
        load_settings()
