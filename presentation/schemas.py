from datetime import datetime

from pydantic import BaseModel, Field


class ConsultRequestSchema(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=2000,
        description="Mensagem textual enviada para a consulta deterministica do motor.",
        examples=["Quero saber meu saldo de pontos"],
    )


class ConsultResponseSchema(BaseModel):
    message: str = Field(
        description="Resposta processada pelo motor para a mensagem recebida.",
    )
    timestamp: datetime = Field(
        description="Timestamp ISO-8601 (UTC) do processamento da resposta.",
    )


class ChatAudioSchema(BaseModel):
    mime_type: str = Field(
        description="Tipo MIME do conteudo de audio retornado (ex.: audio/mpeg).",
        examples=["audio/mpeg"],
    )
    encoding: str = Field(
        pattern=r"^(base64)$",
        description="Estrategia de codificacao do conteudo de audio. Atualmente apenas base64.",
        examples=["base64"],
    )
    content: str = Field(
        description="Conteudo do audio codificado conforme `encoding`.",
    )
    duration_ms: int | None = Field(
        default=None,
        description="Duracao estimada do audio em milissegundos. Pode ser nulo em fallback.",
    )


class ChatMessageSchema(BaseModel):
    text: str = Field(
        min_length=1,
        description="Texto principal da resposta do chat.",
    )
    audio: ChatAudioSchema = Field(
        description="Representacao em audio da resposta, alinhada ao texto.",
    )


class ChatMetadataSchema(BaseModel):
    request_id: str = Field(
        description="Identificador unico de correlacao entre logs e eventos.",
    )
    similarity_score: float | None = Field(
        default=None,
        description=(
            "Pontuacao de similaridade semantica obtida ao consultar o cache. "
            "Pode ser nulo em fluxos sem comparacao."
        ),
    )
    threshold: float = Field(
        description="Limiar configurado para considerar uma resposta como reutilizavel.",
    )
    latency_ms: int = Field(
        description="Latencia interna observada da etapa de processamento, em milissegundos.",
    )


class ChatProcessResponseSchema(BaseModel):
    status: str = Field(
        pattern=r"^(success|partial_success|error)$",
        description="Estado do processamento: success, partial_success ou error.",
    )
    source: str = Field(
        pattern=r"^(cache_hit|cache_miss)$",
        description="Origem da resposta: cache_hit (reutilizada) ou cache_miss (gerada).",
    )
    message: ChatMessageSchema = Field(
        description="Conteudo final entregue ao cliente em texto e audio.",
    )
    transcription: str | None = Field(
        default=None,
        description="Transcricao da entrada quando a requisicao incluiu audio.",
    )
    audio_unavailable: bool = Field(
        description="Indica fallback quando a sintese de audio nao pode ser concluida.",
    )
    metadata: ChatMetadataSchema = Field(
        description="Metadados operacionais da requisicao, incluindo correlacao e similaridade.",
    )

