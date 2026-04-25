from infra.config.settings import Settings


def get_expected_secret(settings: Settings) -> str:
    return settings.x_internal_secret
