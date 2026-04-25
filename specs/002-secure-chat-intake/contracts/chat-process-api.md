# API Contract: POST /api/v1/chat/process

**Feature**: 002-secure-chat-intake (EDI-24)  
**Status**: Phase 1 contract

## Visao geral

Endpoint interno consumido pelo BFF (`interasisai-server`) para enviar mensagens de chat (texto e/ou audio) ao motor de IA. Nesta fase, a resposta e simulada e nao consome tokens de LLM.

## Endpoint

```
POST /api/v1/chat/process
```

## Headers

| Header | Obrigatorio | Descricao |
|--------|-------------|-----------|
| `X-Internal-Secret` | Sim | Segredo compartilhado entre BFF e motor; comparado ao valor de `X_INTERNAL_SECRET` no ambiente |
| `Content-Type` | Sim | `multipart/form-data` |

## Body (`multipart/form-data`)

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `text` | string | Condicional | Mensagem em texto. Obrigatorio se `audio` nao for enviado |
| `audio` | file (UploadFile) | Condicional | Arquivo de audio. Obrigatorio se `text` nao for enviado. Content-type deve iniciar com `audio/` |
| `session_id` | string | Nao | Identificador opcional da conversa |

Regra: `text` ou `audio` (ou ambos) DEVEM estar presentes e nao vazios.

## Respostas

### 200 OK

```json
{
  "status": "success",
  "agent_reply": "Conexao segura estabelecida. Motor LangChain pronto.",
  "received": {
    "has_text": true,
    "has_audio": false,
    "audio_filename": null,
    "session_id": "abc-123"
  }
}
```

### 403 Forbidden

Retornado quando `X-Internal-Secret` esta ausente ou incorreto. Corpo generico, sem detalhes do motivo:

```json
{
  "detail": "Forbidden"
}
```

### 422 Unprocessable Entity

Retornado quando a requisicao e autorizada mas viola regras de validacao (ex.: nem `text` nem `audio` enviados, content-type de audio invalido, texto excede tamanho maximo).

```json
{
  "status": "validation_error",
  "detail": "At least one of 'text' or 'audio' must be provided."
}
```

### 500 Internal Server Error

Retornado em falha interna inesperada. Corpo generico, sem stack trace:

```json
{
  "detail": "Internal Server Error"
}
```

## Exemplos

### Exemplo 1 - Apenas texto

```http
POST /api/v1/chat/process HTTP/1.1
Host: ai-engine.local
X-Internal-Secret: <segredo>
Content-Type: multipart/form-data; boundary=----X

------X
Content-Disposition: form-data; name="text"

Ola, motor!
------X--
```

### Exemplo 2 - Apenas audio

```http
POST /api/v1/chat/process HTTP/1.1
X-Internal-Secret: <segredo>
Content-Type: multipart/form-data; boundary=----X

------X
Content-Disposition: form-data; name="audio"; filename="msg.wav"
Content-Type: audio/wav

<binary>
------X--
```

### Exemplo 3 - Sem segredo (negado)

```http
POST /api/v1/chat/process HTTP/1.1
Content-Type: multipart/form-data; boundary=----X

------X--
```

Resposta: `403 Forbidden`.

## Observabilidade

- Toda negacao 403 gera log `warning` com `reason` (`missing_header` ou `invalid_secret`) e `path`.
- Sucessos geram log `info` com booleanos `has_text` / `has_audio` (sem conteudo).

## Compatibilidade futura

- Campos adicionais opcionais como `model`, `temperature`, `tools` poderao ser introduzidos sem quebra retroativa.
- O formato de `agent_reply` permanecera string; campos como `trace`, `tokens_usage` poderao ser adicionados em `received` ou em chave dedicada.
