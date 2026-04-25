from abc import ABC, abstractmethod
from typing import Protocol

from domain.models import AudioPayload, ChatInput, ChatResult, RegistroSemantico


class ISecretValidator(Protocol):
    def is_valid(self, provided_secret: str | None) -> bool:
        ...


class ILogger(Protocol):
    def info(self, message: str) -> None:
        ...

    def warning(self, message: str) -> None:
        ...

    def error(self, message: str) -> None:
        ...


class ILLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate a model response for a prompt."""


class SemanticCacheRepository(ABC):
    @abstractmethod
    def find_best_match(
        self, embedding_vector: list[float], threshold: float
    ) -> tuple[RegistroSemantico, float] | None:
        """Return the best semantic match above threshold, if any."""

    @abstractmethod
    def save(
        self,
        *,
        query_canonical: str,
        embedding_vector: list[float],
        response_text: str,
        response_audio: AudioPayload,
    ) -> RegistroSemantico:
        """Persist a semantic record and return it."""

    @abstractmethod
    def register_hit(self, semantic_id: str) -> None:
        """Increment usage counters for a semantic record."""


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Build a deterministic embedding vector for text."""


class STTProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_bytes: bytes, mime_type: str | None) -> tuple[str, float]:
        """Return transcription text and confidence for provided audio."""


class TTSProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str) -> AudioPayload:
        """Generate an audio payload for a response text."""


class IChatUseCase(ABC):
    @abstractmethod
    async def execute(self, chat_input: ChatInput) -> ChatResult:
        """Process a chat input and return a structured chat result."""
