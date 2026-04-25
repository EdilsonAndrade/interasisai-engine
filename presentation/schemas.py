from datetime import datetime

from pydantic import BaseModel, Field


class ConsultRequestSchema(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ConsultResponseSchema(BaseModel):
    message: str
    timestamp: datetime


class ChatAudioSchema(BaseModel):
    mime_type: str
    encoding: str = Field(pattern=r"^(base64)$")
    content: str
    duration_ms: int | None = None


class ChatMessageSchema(BaseModel):
    text: str = Field(min_length=1)
    audio: ChatAudioSchema


class ChatMetadataSchema(BaseModel):
    request_id: str
    similarity_score: float | None = None
    threshold: float
    latency_ms: int


class ChatProcessResponseSchema(BaseModel):
    status: str = Field(pattern=r"^(success|partial_success|error)$")
    source: str = Field(pattern=r"^(cache_hit|cache_miss)$")
    message: ChatMessageSchema
    transcription: str | None = None
    audio_unavailable: bool
    metadata: ChatMetadataSchema
