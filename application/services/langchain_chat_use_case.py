from time import perf_counter
from uuid import uuid4

from application.services.semantic_cache_service import SemanticCacheService
from domain.exceptions import EmptyChatInputError, InvalidChatInputError, TranscriptionFailedError
from domain.interfaces import IChatUseCase, ILLMProvider, ILogger, STTProvider, TTSProvider
from domain.models import AudioPayload, ChatInput, ChatResult, ResponseMetadata
from infra.config.settings import Settings
from infra.llm.provider_stub import LLMProviderStub
from infra.speech.stt_provider_stub import STTProviderStub
from infra.speech.tts_provider_stub import TTSProviderStub


_MAX_TEXT_LENGTH = 8000
_TRANSCRIPTION_ERROR = "Nao foi possivel transcrever o audio com confianca minima. Reenvie o audio."


class LangChainChatUseCase(IChatUseCase):
    def __init__(
        self,
        *,
        semantic_cache_service: SemanticCacheService,
        settings: Settings,
        llm_provider: ILLMProvider | None = None,
        stt_provider: STTProvider | None = None,
        tts_provider: TTSProvider | None = None,
        logger: ILogger | None = None,
    ) -> None:
        self._semantic_cache_service = semantic_cache_service
        self._settings = settings
        self._llm_provider = llm_provider or LLMProviderStub()
        self._stt_provider = stt_provider or STTProviderStub()
        self._tts_provider = tts_provider or TTSProviderStub()
        self._logger = logger

    async def execute(self, chat_input: ChatInput) -> ChatResult:
        started = perf_counter()
        request_id = str(uuid4())
        self._validate(chat_input)
        transcription = self._resolve_transcription(chat_input)
        normalized_query = self._resolve_normalized_query(chat_input, transcription)

        match = self._semantic_cache_service.find_match(normalized_query)
        similarity_score: float | None = None
        status = "success"
        source = "cache_miss"

        if match is not None:
            record, similarity_score = match
            source = "cache_hit"
            response_text = record.response_text
            response_audio = record.response_audio
            self._semantic_cache_service.register_hit(record.semantic_id)
        else:
            response_text = await self._llm_provider.generate(normalized_query)
            response_audio, status = self._generate_audio_with_fallback(response_text)
            self._semantic_cache_service.save_response(
                query=normalized_query,
                response_text=response_text,
                response_audio=response_audio,
            )

        latency_ms = int((perf_counter() - started) * 1000)
        metadata = ResponseMetadata(
            request_id=request_id,
            similarity_score=similarity_score,
            threshold=self._semantic_cache_service.threshold,
            latency_ms=latency_ms,
        )
        self._log_event(
            event_type=source,
            request_id=request_id,
            latency_ms=latency_ms,
            similarity_score=similarity_score,
        )

        return ChatResult(
            status=status,
            source=source,
            message_text=response_text,
            message_audio=response_audio,
            transcription=transcription,
            audio_unavailable=status == "partial_success",
            metadata=metadata,
        )

    def _validate(self, chat_input: ChatInput) -> None:
        if not chat_input.has_text and not chat_input.has_audio:
            raise EmptyChatInputError("At least one of 'text' or 'audio' must be provided.")
        if chat_input.has_text and len(chat_input.text or "") > _MAX_TEXT_LENGTH:
            raise InvalidChatInputError(
                f"'text' exceeds maximum length of {_MAX_TEXT_LENGTH} characters."
            )
        if chat_input.has_audio and not _is_audio_content_type(chat_input.audio_content_type):
            raise InvalidChatInputError("'audio' must have a content-type starting with 'audio/'.")

    def _resolve_transcription(self, chat_input: ChatInput) -> str | None:
        if not chat_input.has_audio:
            return None
        transcription, confidence = self._stt_provider.transcribe(
            chat_input.audio_bytes or b"",
            chat_input.audio_content_type,
        )
        if confidence < self._settings.stt_min_confidence and not chat_input.has_text:
            self._log_event(event_type="stt_failed", request_id="n/a", latency_ms=0)
            raise TranscriptionFailedError(_TRANSCRIPTION_ERROR)
        return transcription or None

    def _resolve_normalized_query(self, chat_input: ChatInput, transcription: str | None) -> str:
        if chat_input.has_text:
            return (chat_input.text or "").strip()
        return (transcription or "").strip()

    def _generate_audio_with_fallback(self, response_text: str) -> tuple[AudioPayload, str]:
        try:
            return self._tts_provider.synthesize(response_text), "success"
        except Exception:
            return (
                AudioPayload(
                    mime_type="audio/mpeg",
                    encoding="base64",
                    content="",
                    duration_ms=None,
                ),
                "partial_success",
            )

    def _log_event(
        self,
        *,
        event_type: str,
        request_id: str,
        latency_ms: int,
        similarity_score: float | None = None,
    ) -> None:
        if self._logger is None:
            return
        if hasattr(self._logger, "event"):
            self._logger.event(
                event_type=event_type,
                request_id=request_id,
                latency_ms=latency_ms,
                similarity_score=similarity_score,
            )
            return
        self._logger.info(
            "event={event} request_id={request_id} latency_ms={latency_ms} similarity_score={score}".format(
                event=event_type,
                request_id=request_id,
                latency_ms=latency_ms,
                score=similarity_score,
            )
        )


def _is_audio_content_type(content_type: str | None) -> bool:
    return bool(content_type) and content_type.lower().startswith("audio/")
