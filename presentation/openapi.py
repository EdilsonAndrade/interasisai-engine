from fastapi import Depends
from fastapi.security import APIKeyHeader

API_TITLE = "InterasisAI Engine"
API_VERSION = "1.0.0"
API_DESCRIPTION = (
    "Motor de IA da plataforma InterasisAI. Expoe endpoints internos para "
    "consulta determinista, chat multimodal com cache semantico e suporte a "
    "respostas em texto e audio. Todas as rotas internas exigem o cabecalho "
    "`X-Internal-Secret` para autorizacao do Gatekeeper."
)

INTERNAL_SECRET_HEADER = "X-Internal-Secret"

TAG_CHAT = "Chat"
TAG_AI = "AI"

OPENAPI_TAGS = [
    {
        "name": TAG_CHAT,
        "description": (
            "Fluxo multimodal de chat com cache semantico, transcricao de audio "
            "e geracao de resposta em texto e audio."
        ),
    },
    {
        "name": TAG_AI,
        "description": (
            "Endpoints internos de orquestracao de IA, incluindo consulta "
            "deterministica e operacoes utilitarias do motor."
        ),
    },
]

internal_secret_scheme = APIKeyHeader(
    name=INTERNAL_SECRET_HEADER,
    scheme_name="InternalSecretHeader",
    description=(
        "Cabecalho de autorizacao interno. Use o botao Authorize para informar "
        "o segredo do ambiente. O middleware Gatekeeper valida o valor antes "
        "de despachar a chamada para a rota."
    ),
    auto_error=False,
)


def require_internal_secret(
    _: str | None = Depends(internal_secret_scheme),
) -> None:
    """Dependencia de documentacao para expor o esquema de seguranca no Swagger.

    A validacao real e feita pelo middleware de seguranca; esta dependencia
    apenas registra o requerimento de cabecalho no OpenAPI para permitir o
    uso do Authorize na UI do Swagger.
    """
    return None
