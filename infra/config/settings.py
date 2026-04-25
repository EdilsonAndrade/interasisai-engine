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
    semantic_match_threshold: float = 0.85
    stt_min_confidence: float = 0.7


_ALLOWED_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def load_settings(dotenv_path: str | None = None) -> Settings:
    if dotenv_path is not None:
        load_dotenv(dotenv_path=dotenv_path)

    secret = os.getenv("X_INTERNAL_SECRET")
    if not secret:
        raise ConfigurationError("X_INTERNAL_SECRET environment variable is required")

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    if log_level not in _ALLOWED_LOG_LEVELS:
        raise ConfigurationError("LOG_LEVEL must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL")

    app_name = os.getenv("APP_NAME", "InterasisAI-Engine")
    semantic_match_threshold = _load_float_env(
        env_name="SEMANTIC_MATCH_THRESHOLD",
        default=0.85,
    )
    stt_min_confidence = _load_float_env(
        env_name="STT_MIN_CONFIDENCE",
        default=0.7,
    )
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
        semantic_match_threshold=semantic_match_threshold,
        stt_min_confidence=stt_min_confidence,
    )


def _load_float_env(env_name: str, default: float) -> float:
    raw_value = os.getenv(env_name)
    if raw_value is None:
        return default
    try:
        value = float(raw_value)
    except ValueError as exc:
        raise ConfigurationError(f"{env_name} must be a float between 0 and 1") from exc
    if value < 0 or value > 1:
        raise ConfigurationError(f"{env_name} must be a float between 0 and 1")
    return value
