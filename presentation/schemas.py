from datetime import datetime

from pydantic import BaseModel, Field


class ConsultRequestSchema(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ConsultResponseSchema(BaseModel):
    message: str
    timestamp: datetime


class ChatProcessReceivedSchema(BaseModel):
    has_text: bool
    has_audio: bool
    audio_filename: str | None = None
    session_id: str | None = None


class ChatProcessResponseSchema(BaseModel):
    status: str = Field(pattern=r"^(success|validation_error|unauthorized)$")
    agent_reply: str = Field(min_length=1)
    received: ChatProcessReceivedSchema
