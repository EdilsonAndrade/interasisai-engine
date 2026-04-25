import pytest

from application.services.langchain_chat_use_case import LangChainChatUseCase
from application.services.semantic_cache_service import SemanticCacheService
from domain.exceptions import EmptyChatInputError, InvalidChatInputError
from domain.models import AudioPayload, ChatInput
from infra.config.settings import Environment, Settings
from infra.semantic.embedding_provider_stub import EmbeddingProviderStub
from infra.semantic.in_memory_semantic_cache import InMemorySemanticCacheRepository


class _LLMStub:
    async def generate(self, prompt: str) -> str:
        return f"resposta:{prompt}"


class _TTSStub:
    def __init__(self, should_fail: bool = False) -> None:
        self._should_fail = should_fail

    def synthesize(self, text: str) -> AudioPayload:
        if self._should_fail:
            raise RuntimeError("tts failed")
        return AudioPayload(
            mime_type="audio/mpeg",
            encoding="base64",
            content="abc",
            duration_ms=1000,
        )


def _build_use_case(tts_should_fail: bool = False, logger=None) -> LangChainChatUseCase:
    settings = Settings(
        x_internal_secret="secret",
        environment=Environment.TESTING,
        semantic_match_threshold=0.85,
        stt_min_confidence=0.7,
    )
    semantic_cache_service = SemanticCacheService(
        repository=InMemorySemanticCacheRepository(),
        embedding_provider=EmbeddingProviderStub(),
        threshold=settings.semantic_match_threshold,
    )
    return LangChainChatUseCase(
        semantic_cache_service=semantic_cache_service,
        settings=settings,
        llm_provider=_LLMStub(),
        tts_provider=_TTSStub(should_fail=tts_should_fail),
        logger=logger,
    )


@pytest.mark.asyncio
async def test_use_case_returns_simulated_success_for_text_only() -> None:
    use_case = _build_use_case()

    result = await use_case.execute(ChatInput(text="hello", session_id="s1"))

    assert result.status == "success"
    assert result.source == "cache_miss"
    assert result.message_text == "resposta:hello"
    assert result.message_audio.encoding == "base64"


@pytest.mark.asyncio
async def test_use_case_returns_simulated_success_for_audio_only() -> None:
    use_case = _build_use_case()

    result = await use_case.execute(
        ChatInput(audio_filename="msg.wav", audio_content_type="audio/wav")
    )

    assert result.status == "success"
    assert result.transcription is not None
    assert result.message_audio.encoding == "base64"


@pytest.mark.asyncio
async def test_use_case_raises_empty_input_when_neither_text_nor_audio() -> None:
    use_case = _build_use_case()

    with pytest.raises(EmptyChatInputError):
        await use_case.execute(ChatInput())


@pytest.mark.asyncio
async def test_use_case_raises_empty_input_when_text_is_blank() -> None:
    use_case = _build_use_case()

    with pytest.raises(EmptyChatInputError):
        await use_case.execute(ChatInput(text="   "))


@pytest.mark.asyncio
async def test_use_case_rejects_non_audio_content_type() -> None:
    use_case = _build_use_case()

    with pytest.raises(InvalidChatInputError):
        await use_case.execute(
            ChatInput(audio_filename="img.png", audio_content_type="image/png")
        )


@pytest.mark.asyncio
async def test_use_case_rejects_text_above_max_length() -> None:
    use_case = _build_use_case()

    with pytest.raises(InvalidChatInputError):
        await use_case.execute(ChatInput(text="x" * 8001))


@pytest.mark.asyncio
async def test_use_case_logs_success_when_logger_provided() -> None:
    logged = []

    class _Logger:
        def info(self, message: str) -> None:
            logged.append(("info", message))

        def warning(self, message: str) -> None:  # pragma: no cover - not used
            logged.append(("warning", message))

        def error(self, message: str) -> None:  # pragma: no cover - not used
            logged.append(("error", message))

    use_case = _build_use_case(logger=_Logger())
    await use_case.execute(ChatInput(text="hello"))

    assert any(level == "info" and "event=cache_miss" in msg for level, msg in logged)


@pytest.mark.asyncio
async def test_use_case_does_not_invoke_external_clients(monkeypatch) -> None:
    """Smoke check that no HTTP/network library is invoked during the simulated flow."""
    import httpx

    def _boom(*_args, **_kwargs):  # pragma: no cover - guard only
        raise AssertionError("httpx must not be called in the simulated chat flow")

    monkeypatch.setattr(httpx.Client, "send", _boom, raising=True)
    monkeypatch.setattr(httpx.AsyncClient, "send", _boom, raising=True)

    use_case = _build_use_case()
    result = await use_case.execute(ChatInput(text="hello"))

    assert result.status == "success"


@pytest.mark.asyncio
async def test_use_case_returns_partial_success_when_tts_fails() -> None:
    use_case = _build_use_case(tts_should_fail=True)

    result = await use_case.execute(ChatInput(text="gera resposta"))

    assert result.status == "partial_success"
    assert result.audio_unavailable is True
    assert result.message_audio.content == ""


@pytest.mark.asyncio
async def test_use_case_returns_cache_hit_on_repeated_query() -> None:
    use_case = _build_use_case()

    first = await use_case.execute(ChatInput(text="status da solicitacao"))
    second = await use_case.execute(ChatInput(text="status da solicitacao"))

    assert first.source == "cache_miss"
    assert second.source == "cache_hit"
    assert second.metadata.similarity_score is not None
