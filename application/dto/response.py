from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class ConsultResponseDTO:
    message: str
    timestamp: datetime


@dataclass(slots=True)
class ChatProcessResponseDTO:
    status: str
    agent_reply: str
    received: dict = field(default_factory=dict)
