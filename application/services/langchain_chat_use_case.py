from domain.exceptions import EmptyChatInputError, InvalidChatInputError
from domain.interfaces import IChatUseCase, ILogger
from domain.models import ChatInput, ChatResult


_AGENT_REPLY = "Conexao segura estabelecida. Motor LangChain pronto."
_MAX_TEXT_LENGTH = 8000


class LangChainChatUseCase(IChatUseCase):
    """First-phase chat use case.

    Validates input contract and returns a simulated response. No external LLM
    calls are issued in this phase to avoid token cost while the LangChain
    ecosystem is bootstrapped.
    """

    def __init__(self, logger: ILogger | None = None) -> None:
        self._logger = logger

    async def execute(self, chat_input: ChatInput) -> ChatResult:
        self._validate(chat_input)
        result = ChatResult(
            status="success",
            agent_reply=_AGENT_REPLY,
            received={
                "has_text": chat_input.has_text,
                "has_audio": chat_input.has_audio,
                "audio_filename": chat_input.audio_filename,
                "session_id": chat_input.session_id,
            },
        )
        self._log_success(chat_input)
        return result

    def _validate(self, chat_input: ChatInput) -> None:
        if not chat_input.has_text and not chat_input.has_audio:
            raise EmptyChatInputError("At least one of 'text' or 'audio' must be provided.")
        if chat_input.has_text and len(chat_input.text or "") > _MAX_TEXT_LENGTH:
            raise InvalidChatInputError(
                f"'text' exceeds maximum length of {_MAX_TEXT_LENGTH} characters."
            )
        if chat_input.has_audio and not _is_audio_content_type(chat_input.audio_content_type):
            raise InvalidChatInputError("'audio' must have a content-type starting with 'audio/'.")

    def _log_success(self, chat_input: ChatInput) -> None:
        if self._logger is None:
            return
        self._logger.info(
            "chat_process success has_text={has_text} has_audio={has_audio} session_id={session_id}".format(
                has_text=chat_input.has_text,
                has_audio=chat_input.has_audio,
                session_id=chat_input.session_id,
            )
        )


def _is_audio_content_type(content_type: str | None) -> bool:
    return bool(content_type) and content_type.lower().startswith("audio/")
