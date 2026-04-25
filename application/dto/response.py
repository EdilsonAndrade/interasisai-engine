from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class ConsultResponseDTO:
    message: str
    timestamp: datetime


@dataclass(slots=True)
class ChatProcessResponseDTO:
    status: str
    source: str
    message: dict
    transcription: str | None = None
    audio_unavailable: bool = False
    metadata: dict = field(default_factory=dict)
