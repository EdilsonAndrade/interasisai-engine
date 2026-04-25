# API Contract: POST /api/v1/chat/process

**Feature**: 003-semantic-cache-tts (EDI-26)  
**Status**: Phase 1 contract

## Visao Geral

Endpoint interno consumido pelo BFF para fluxo multimodal de chat com cache semantico. O endpoint aceita texto e/ou audio, pode transcrever entrada em audio, aplica matching semantico com threshold configuravel e retorna resposta com texto e audio em contrato consistente para cache hit e cache miss.

## Endpoint

```http
POST /api/v1/chat/process
```

## Headers

| Header | Obrigatorio | Descricao |
|--------|-------------|-----------|
| `X-Internal-Secret` | Sim | Segredo compartilhado para autorizacao de requisicoes internas |
| `Content-Type` | Sim | `multipart/form-data` |

## Body (multipart/form-data)

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `text` | string | Condicional | Pergunta textual |
| `audio` | file | Condicional | Arquivo de audio (`audio/*`) |
| `session_id` | string | Nao | Identificador opcional da sessao |
| `client_request_ts` | string (ISO-8601) | Nao | Timestamp enviado pelo cliente |

Regra: ao menos um entre `text` e `audio` deve existir e ser valido.

## Respostas

### 200 OK - Cache Hit

```json
{
  "status": "success",
  "source": "cache_hit",
  "message": {
    "text": "Resposta previamente validada para a pergunta equivalente.",
    "audio": {
      "mime_type": "audio/mpeg",
      "encoding": "base64",
      "content": "<base64-audio>",
      "duration_ms": 4210
    }
  },
  "transcription": null,
  "audio_unavailable": false,
  "metadata": {
    "request_id": "45f649db-bf7f-4a2d-9ca8-4d7f2e046b46",
    "similarity_score": 0.92,
    "threshold": 0.85,
    "latency_ms": 320
  }
}
```

### 200 OK - Cache Miss

```json
{
  "status": "success",
  "source": "cache_miss",
  "message": {
    "text": "Nova resposta gerada para sua solicitacao.",
    "audio": {
      "mime_type": "audio/mpeg",
      "encoding": "base64",
      "content": "<base64-audio>",
      "duration_ms": 5370
    }
  },
  "transcription": "preciso consultar meus horarios",
  "audio_unavailable": false,
  "metadata": {
    "request_id": "d1d5f4e8-9dde-460b-aa11-b06910a42a6f",
    "similarity_score": 0.62,
    "threshold": 0.85,
    "latency_ms": 980
  }
}
```

### 200 OK - Fallback de audio

```json
{
  "status": "partial_success",
  "source": "cache_miss",
  "message": {
    "text": "Nova resposta gerada, mas o audio esta indisponivel no momento.",
    "audio": {
      "mime_type": "audio/mpeg",
      "encoding": "base64",
      "content": "",
      "duration_ms": null
    }
  },
  "transcription": null,
  "audio_unavailable": true,
  "metadata": {
    "request_id": "17bb8b44-b1e7-4824-850f-3b00a5ac940d",
    "similarity_score": null,
    "threshold": 0.85,
    "latency_ms": 1110
  }
}
```

### 403 Forbidden

```json
{
  "detail": "Forbidden"
}
```

### 422 Unprocessable Entity

```json
{
  "status": "error",
  "code": "INVALID_INPUT",
  "detail": "At least one of 'text' or 'audio' must be provided."
}
```

### 422 Unprocessable Entity - STT invalido

```json
{
  "status": "error",
  "code": "TRANSCRIPTION_FAILED",
  "detail": "Nao foi possivel transcrever o audio com confianca minima. Reenvie o audio."
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal Server Error"
}
```

## Regras Funcionais de Contrato

- O shape de `message.text`, `message.audio`, `audio_unavailable` e `metadata` deve ser mantido em cache hit e cache miss.
- `transcription` deve ser retornada quando houver entrada em audio processada com sucesso.
- Em erro de autorizacao, nao incluir detalhes sobre segredo ausente/invalido.
- Em erro operacional interno, nao expor stack trace ou dados sensiveis.

## Observabilidade

- Eventos minimos esperados: `cache_hit`, `cache_miss`, `stt_failed`, `tts_failed`.
- Logs devem incluir `request_id`, `latency_ms` e tipo de evento, sem payload de texto integral e sem segredos.

## Compatibilidade Futura

- Campos opcionais adicionais podem ser introduzidos em `metadata` sem quebra retroativa.
- O campo `message.audio.encoding` pode aceitar novos valores no futuro (`url`, `binary_ref`) mantendo backward compatibility para clientes que suportam `base64`.
