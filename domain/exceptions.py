class UnauthorizedError(Exception):
    """Raised when an internal request cannot be authenticated."""


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""


class EmptyChatInputError(Exception):
    """Raised when a chat request contains neither text nor audio."""


class InvalidChatInputError(Exception):
    """Raised when a chat request contains invalid content (e.g. wrong audio MIME)."""


class TranscriptionFailedError(Exception):
    """Raised when STT cannot transcribe with minimum confidence."""


class AudioSynthesisError(Exception):
    """Raised when TTS cannot synthesize audio for an otherwise valid response."""
