import pytest

from domain.exceptions import ConfigurationError
from infra.config.settings import load_settings


def test_settings_loads_with_valid_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("X_INTERNAL_SECRET", "abc")
    monkeypatch.setenv("ENVIRONMENT", "testing")

    settings = load_settings()
    assert settings.x_internal_secret == "abc"


def test_settings_fails_when_secret_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("X_INTERNAL_SECRET", raising=False)

    with pytest.raises(ConfigurationError):
        load_settings()
