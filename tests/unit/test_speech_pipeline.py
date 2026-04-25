import pytest

from application.services.langchain_chat_use_case import LangChainChatUseCase
from application.services.semantic_cache_service import SemanticCacheService
from domain.exceptions import TranscriptionFailedError
from domain.models import ChatInput
from infra.config.settings import Environment, Settings
from infra.semantic.embedding_provider_stub import EmbeddingProviderStub
from infra.semantic.in_memory_semantic_cache import InMemorySemanticCacheRepository


class _LLMStub:
    async def generate(self, prompt: str) -> str:
        return f"resposta:{prompt}"


class _TTSStub:
    def synthesize(self, text: str):
        from domain.models import AudioPayload

        return AudioPayload(
            mime_type="audio/mpeg",
            encoding="base64",
            content="audio",
            duration_ms=1000,
        )


class _STTLowConfidenceStub:
    def transcribe(self, audio_bytes: bytes, mime_type: str | None) -> tuple[str, float]:
        return "transcricao ruim", 0.2


@pytest.mark.asyncio
async def test_voice_input_fails_when_stt_confidence_is_below_threshold() -> None:
    settings = Settings(
        x_internal_secret="secret",
        environment=Environment.TESTING,
        stt_min_confidence=0.7,
    )
    use_case = LangChainChatUseCase(
        semantic_cache_service=SemanticCacheService(
            repository=InMemorySemanticCacheRepository(),
            embedding_provider=EmbeddingProviderStub(),
            threshold=0.85,
        ),
        settings=settings,
        llm_provider=_LLMStub(),
        stt_provider=_STTLowConfidenceStub(),
        tts_provider=_TTSStub(),
    )

    with pytest.raises(TranscriptionFailedError):
        await use_case.execute(
            ChatInput(
                audio_bytes=b"LOW_CONF voice",
                audio_filename="voice.wav",
                audio_content_type="audio/wav",
            )
        )
