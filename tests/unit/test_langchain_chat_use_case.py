import pytest

from application.services.langchain_chat_use_case import LangChainChatUseCase
from domain.exceptions import EmptyChatInputError, InvalidChatInputError
from domain.models import ChatInput


@pytest.mark.asyncio
async def test_use_case_returns_simulated_success_for_text_only() -> None:
    use_case = LangChainChatUseCase()

    result = await use_case.execute(ChatInput(text="hello", session_id="s1"))

    assert result.status == "success"
    assert result.agent_reply == "Conexao segura estabelecida. Motor LangChain pronto."
    assert result.received == {
        "has_text": True,
        "has_audio": False,
        "audio_filename": None,
        "session_id": "s1",
    }


@pytest.mark.asyncio
async def test_use_case_returns_simulated_success_for_audio_only() -> None:
    use_case = LangChainChatUseCase()

    result = await use_case.execute(
        ChatInput(audio_filename="msg.wav", audio_content_type="audio/wav")
    )

    assert result.status == "success"
    assert result.received["has_audio"] is True
    assert result.received["audio_filename"] == "msg.wav"
    assert result.received["has_text"] is False


@pytest.mark.asyncio
async def test_use_case_raises_empty_input_when_neither_text_nor_audio() -> None:
    use_case = LangChainChatUseCase()

    with pytest.raises(EmptyChatInputError):
        await use_case.execute(ChatInput())


@pytest.mark.asyncio
async def test_use_case_raises_empty_input_when_text_is_blank() -> None:
    use_case = LangChainChatUseCase()

    with pytest.raises(EmptyChatInputError):
        await use_case.execute(ChatInput(text="   "))


@pytest.mark.asyncio
async def test_use_case_rejects_non_audio_content_type() -> None:
    use_case = LangChainChatUseCase()

    with pytest.raises(InvalidChatInputError):
        await use_case.execute(
            ChatInput(audio_filename="img.png", audio_content_type="image/png")
        )


@pytest.mark.asyncio
async def test_use_case_rejects_text_above_max_length() -> None:
    use_case = LangChainChatUseCase()

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

    use_case = LangChainChatUseCase(logger=_Logger())
    await use_case.execute(ChatInput(text="hello"))

    assert any(level == "info" and "chat_process success" in msg for level, msg in logged)


@pytest.mark.asyncio
async def test_use_case_does_not_invoke_external_clients(monkeypatch) -> None:
    """Smoke check that no HTTP/network library is invoked during the simulated flow."""
    import httpx

    def _boom(*_args, **_kwargs):  # pragma: no cover - guard only
        raise AssertionError("httpx must not be called in the simulated chat flow")

    monkeypatch.setattr(httpx.Client, "send", _boom, raising=True)
    monkeypatch.setattr(httpx.AsyncClient, "send", _boom, raising=True)

    use_case = LangChainChatUseCase()
    result = await use_case.execute(ChatInput(text="hello"))

    assert result.status == "success"
