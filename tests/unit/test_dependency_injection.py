from unittest.mock import patch

from infra.config.settings import Environment, Settings
from presentation.main import create_app


def test_create_app_wires_dependency_injection_with_override() -> None:
    settings = Settings(
        x_internal_secret="abc",
        log_level="INFO",
        app_name="test-app",
        environment=Environment.TESTING,
    )

    app = create_app(settings_override=settings)

    assert app.state.settings.x_internal_secret == "abc"
    assert app.state.secret_validator is not None
    assert app.state.consult_service is not None


def test_create_app_uses_logger_injection_path() -> None:
    settings = Settings(
        x_internal_secret="abc",
        log_level="INFO",
        app_name="test-app",
        environment=Environment.TESTING,
    )

    with patch("presentation.main.AppLogger") as logger_mock:
        create_app(settings_override=settings)
        logger_mock.assert_called()
