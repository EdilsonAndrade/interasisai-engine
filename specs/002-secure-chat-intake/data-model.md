# Data Model: Recepcao Segura de Input de Chat (EDI-24)

**Feature**: 002-secure-chat-intake  
**Date**: 2026-04-25  
**Status**: Phase 1 output

## Visao Geral

Os dados desta feature sao efemeros: nao ha persistencia. As entidades modelam o contrato de entrada/saida do endpoint `POST /api/v1/chat/process` e o estado de seguranca da requisicao.

## Entidades

### 1. ChatProcessRequest (entrada)

Representa a requisicao recebida do BFF pelo endpoint de chat.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `text` | string \| null | Nao (mas pelo menos um entre `text` e `audio` e obrigatorio) | Texto enviado pelo usuario |
| `audio` | binario (UploadFile) \| null | Nao (mas pelo menos um entre `text` e `audio` e obrigatorio) | Arquivo de audio vindo do BFF |
| `session_id` | string \| null | Nao | Identificador da conversa (preparacao para memoria LangChain) |

**Regras de validacao**:
- Pelo menos um dos campos `text` ou `audio` deve estar presente e nao vazio.
- `text`, quando presente, deve ter tamanho maximo configuravel (default 8.000 caracteres).
- `audio`, quando presente, deve ter content-type iniciando em `audio/`.

**Transicoes de estado**: nao se aplica (entidade transiente por requisicao).

### 2. ChatProcessResponse (saida simulada)

Resposta padronizada retornada nesta fase, antes da integracao real com LangChain.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `status` | string | Sim | Sempre `"success"` em respostas validas desta fase |
| `agent_reply` | string | Sim | Mensagem fixa simulando a resposta da chain |
| `received` | objeto | Sim | Eco resumido do que foi recebido (`has_text`, `has_audio`, `audio_filename`, `session_id`) |

**Regras de validacao**:
- `status` deve ser um valor controlado (`success`, `validation_error`, `unauthorized`).
- `agent_reply` nao pode ser vazio.

### 3. SecurityContext (estado interno)

Representa o resultado da validacao do segredo interno na camada de middleware.

| Campo | Tipo | Descricao |
|-------|------|-----------|
| `is_authorized` | boolean | Indica se o segredo recebido bate com o valor de ambiente |
| `denial_reason` | string \| null | `missing_header`, `invalid_secret` ou `null` quando autorizado |

**Regras**:
- Quando `is_authorized` e `false`, a resposta HTTP e sempre 403, sem expor `denial_reason` ao cliente.
- `denial_reason` e usado apenas em logs internos.

### 4. AccessDenialEvent (log)

Registro de auditoria gerado em cada negacao de acesso.

| Campo | Tipo | Descricao |
|-------|------|-----------|
| `timestamp` | datetime ISO-8601 | Momento da negacao |
| `path` | string | Caminho da requisicao |
| `reason` | string | `missing_header` ou `invalid_secret` |
| `client_host` | string \| null | IP de origem quando disponivel |

**Regras**:
- Nao registra valor do segredo recebido.
- Nivel de log: `warning`.

## Relacionamentos

- `ChatProcessRequest` -> `ChatProcessResponse`: 1:1 por requisicao processada com sucesso.
- `SecurityContext` aplica-se a todas as rotas protegidas; quando negado, gera `AccessDenialEvent` e impede a criacao do `ChatProcessResponse`.

## Volume e Performance

- Throughput esperado nesta fase: baixo (BFF interno em homologacao).
- Sem persistencia, nao ha consideracoes de indexacao ou particionamento.
