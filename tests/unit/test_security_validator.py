from infra.config.settings import Environment, Settings
from infra.security.secret_validator import SecretValidator


def test_secret_validator_returns_true_for_matching_secret() -> None:
    settings = Settings(
        x_internal_secret="abc",
        log_level="INFO",
        app_name="test",
        environment=Environment.TESTING,
    )
    validator = SecretValidator(settings)

    assert validator.is_valid("abc") is True


def test_secret_validator_returns_false_for_mismatch() -> None:
    settings = Settings(
        x_internal_secret="abc",
        log_level="INFO",
        app_name="test",
        environment=Environment.TESTING,
    )
    validator = SecretValidator(settings)

    assert validator.is_valid("def") is False


def test_secret_validator_returns_false_when_missing_secret() -> None:
    settings = Settings(
        x_internal_secret="abc",
        log_level="INFO",
        app_name="test",
        environment=Environment.TESTING,
    )
    validator = SecretValidator(settings)

    assert validator.is_valid(None) is False
