from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(slots=True)
class ConsultRequest:
    message: str


@dataclass(slots=True)
class ConsultResponse:
    message: str
    timestamp: datetime

    @staticmethod
    def now(message: str) -> "ConsultResponse":
        return ConsultResponse(message=message, timestamp=datetime.now(timezone.utc))


@dataclass(slots=True)
class SecurityContext:
    is_authorized: bool
    source: str = "internal"


@dataclass(slots=True)
class ChatInput:
    text: str | None = None
    audio_filename: str | None = None
    audio_content_type: str | None = None
    session_id: str | None = None

    @property
    def has_text(self) -> bool:
        return bool(self.text and self.text.strip())

    @property
    def has_audio(self) -> bool:
        return self.audio_filename is not None


@dataclass(slots=True)
class ChatResult:
    status: str
    agent_reply: str
    received: dict = field(default_factory=dict)


@dataclass(slots=True)
class AccessDenialEvent:
    timestamp: datetime
    path: str
    reason: str
    client_host: str | None = None

    @staticmethod
    def create(path: str, reason: str, client_host: str | None = None) -> "AccessDenialEvent":
        return AccessDenialEvent(
            timestamp=datetime.now(timezone.utc),
            path=path,
            reason=reason,
            client_host=client_host,
        )
