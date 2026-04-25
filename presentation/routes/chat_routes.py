from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile

from application.services.langchain_chat_use_case import LangChainChatUseCase
from domain.exceptions import EmptyChatInputError, InvalidChatInputError
from domain.models import ChatInput
from presentation.schemas import ChatProcessReceivedSchema, ChatProcessResponseSchema

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


async def get_chat_use_case(request: Request) -> LangChainChatUseCase:
    use_case = getattr(request.app.state, "chat_use_case", None)
    if use_case is None:
        use_case = LangChainChatUseCase(logger=getattr(request.app.state, "logger", None))
        request.app.state.chat_use_case = use_case
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

    chat_input = ChatInput(
        text=text,
        audio_filename=audio.filename if audio is not None else None,
        audio_content_type=audio.content_type if audio is not None else None,
        session_id=session_id,
    )

    try:
        result = await use_case.execute(chat_input)
    except EmptyChatInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except InvalidChatInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return ChatProcessResponseSchema(
        status=result.status,
        agent_reply=result.agent_reply,
        received=ChatProcessReceivedSchema(**result.received),
    )


def _ensure_authorized(request: Request) -> None:
    security_context = getattr(request.state, "security_context", None)
    if not security_context or not security_context.is_authorized:
        raise HTTPException(status_code=403, detail="Forbidden")
