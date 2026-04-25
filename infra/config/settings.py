from dataclasses import dataclass
from enum import Enum
import os

from dotenv import load_dotenv

from domain.exceptions import ConfigurationError


class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


@dataclass(slots=True)
class Settings:
    x_internal_secret: str
    log_level: str = "INFO"
    app_name: str = "InterasisAI-Engine"
    environment: Environment = Environment.DEVELOPMENT


_ALLOWED_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def load_settings(dotenv_path: str | None = None) -> Settings:
    load_dotenv(dotenv_path=dotenv_path)

    secret = os.getenv("X_INTERNAL_SECRET")
    if not secret:
        raise ConfigurationError("X_INTERNAL_SECRET environment variable is required")

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    if log_level not in _ALLOWED_LOG_LEVELS:
        raise ConfigurationError("LOG_LEVEL must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL")

    app_name = os.getenv("APP_NAME", "InterasisAI-Engine")
    raw_env = os.getenv("ENVIRONMENT", "development").lower()
    try:
        environment = Environment(raw_env)
    except ValueError as exc:
        raise ConfigurationError("ENVIRONMENT must be development, testing, or production") from exc

    return Settings(
        x_internal_secret=secret,
        log_level=log_level,
        app_name=app_name,
        environment=environment,
    )
