from dataclasses import dataclass


@dataclass(slots=True)
class ConsultRequestDTO:
    message: str


@dataclass(slots=True)
class ChatProcessRequestDTO:
    text: str | None = None
    audio_bytes: bytes | None = None
    audio_filename: str | None = None
    audio_content_type: str | None = None
    session_id: str | None = None
