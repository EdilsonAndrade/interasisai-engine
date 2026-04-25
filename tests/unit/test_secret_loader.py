from infra.config.settings import Environment, Settings
from infra.security.secret_loader import get_expected_secret


def test_secret_loader_returns_expected_secret() -> None:
    settings = Settings(
        x_internal_secret="expected",
        log_level="INFO",
        app_name="test",
        environment=Environment.TESTING,
    )

    assert get_expected_secret(settings) == "expected"
