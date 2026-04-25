from domain.interfaces import ISecretValidator
from infra.config.settings import Settings
from infra.security.secret_loader import get_expected_secret


class SecretValidator(ISecretValidator):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def is_valid(self, provided_secret: str | None) -> bool:
        if not provided_secret:
            return False
        return provided_secret == get_expected_secret(self._settings)
