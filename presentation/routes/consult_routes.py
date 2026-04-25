from fastapi import APIRouter, Depends, Request

from application.services.consult_service import ConsultService
from domain.models import ConsultRequest
from presentation.openapi import TAG_AI, require_internal_secret
from presentation.schemas import ConsultRequestSchema, ConsultResponseSchema

router = APIRouter(
    prefix="/api/v1/ai",
    tags=[TAG_AI],
    dependencies=[Depends(require_internal_secret)],
    responses={
        403: {"description": "Bloqueio do Gatekeeper: cabecalho `X-Internal-Secret` ausente ou invalido."},
    },
)


async def get_consult_service(request: Request) -> ConsultService:
    return request.app.state.consult_service


@router.post(
    "/consult",
    response_model=ConsultResponseSchema,
    summary="Consulta deterministica do motor de IA",
    description=(
        "Endpoint interno para consulta deterministica baseada em mensagem textual. "
        "Requer cabecalho `X-Internal-Secret`."
    ),
)
async def consult(
    payload: ConsultRequestSchema,
    request: Request,
    service: ConsultService = Depends(get_consult_service),
) -> ConsultResponseSchema:
    security_context = getattr(request.state, "security_context", None)
    if not security_context or not security_context.is_authorized:
        # Defense in depth. Middleware already blocks unauthorized requests.
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Forbidden")

    response = await service.process_consult(ConsultRequest(message=payload.message))
    return ConsultResponseSchema(message=response.message, timestamp=response.timestamp)
