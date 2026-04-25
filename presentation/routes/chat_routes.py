from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from application.services.langchain_chat_use_case import LangChainChatUseCase
from domain.exceptions import EmptyChatInputError, InvalidChatInputError, TranscriptionFailedError
from domain.models import ChatInput
from presentation.schemas import (
    ChatAudioSchema,
    ChatMessageSchema,
    ChatMetadataSchema,
    ChatProcessResponseSchema,
)

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


async def get_chat_use_case(request: Request) -> LangChainChatUseCase:
    use_case = getattr(request.app.state, "chat_use_case", None)
    if use_case is None:
        raise HTTPException(status_code=500, detail="Chat use case is not configured")
    return use_case


@router.post("/process", response_model=ChatProcessResponseSchema)
async def process_chat(
    request: Request,
    text: str | None = Form(default=None),
    audio: UploadFile | None = File(default=None),
    session_id: str | None = Form(default=None),
    use_case: LangChainChatUseCase = Depends(get_chat_use_case),
) -> ChatProcessResponseSchema:
    _ensure_authorized(request)

    audio_bytes: bytes | None = None
    if audio is not None:
        audio_bytes = await audio.read()

    chat_input = ChatInput(
        text=text,
        audio_bytes=audio_bytes,
        audio_filename=audio.filename if audio is not None else None,
        audio_content_type=audio.content_type if audio is not None else None,
        session_id=session_id,
    )

    try:
        result = await use_case.execute(chat_input)
    except EmptyChatInputError as exc:
        return JSONResponse(
            status_code=422,
            content={
                "status": "error",
                "code": "INVALID_INPUT",
                "detail": str(exc),
            },
        )
    except InvalidChatInputError as exc:
        return JSONResponse(
            status_code=422,
            content={
                "status": "error",
                "code": "INVALID_INPUT",
                "detail": str(exc),
            },
        )
    except TranscriptionFailedError as exc:
        return JSONResponse(
            status_code=422,
            content={
                "status": "error",
                "code": "TRANSCRIPTION_FAILED",
                "detail": str(exc),
            },
        )

    return ChatProcessResponseSchema(
        status=result.status,
        source=result.source,
        message=ChatMessageSchema(
            text=result.message_text,
            audio=ChatAudioSchema(
                mime_type=result.message_audio.mime_type,
                encoding=result.message_audio.encoding,
                content=result.message_audio.content,
                duration_ms=result.message_audio.duration_ms,
            ),
        ),
        transcription=result.transcription,
        audio_unavailable=result.audio_unavailable,
        metadata=ChatMetadataSchema(
            request_id=result.metadata.request_id,
            similarity_score=result.metadata.similarity_score,
            threshold=result.metadata.threshold,
            latency_ms=result.metadata.latency_ms,
        ),
    )


def _ensure_authorized(request: Request) -> None:
    security_context = getattr(request.state, "security_context", None)
    if not security_context or not security_context.is_authorized:
        raise HTTPException(status_code=403, detail="Forbidden")
