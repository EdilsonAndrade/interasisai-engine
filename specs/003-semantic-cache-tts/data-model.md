# Data Model: Cache Semantico e Resposta em Audio (EDI-26)

**Feature**: 003-semantic-cache-tts  
**Date**: 2026-04-25  
**Status**: Phase 1 output

## Visao Geral

Esta feature introduz entidades de processamento multimodal e reuso semantico, mantendo contrato consistente para cache hit e cache miss. O modelo inclui entrada textual/audio, registro semantico reutilizavel, resposta multimodal e eventos operacionais.

## Entidades

### 1. SolicitacaoChat

Representa a entrada recebida no endpoint de chat.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `request_id` | string (uuid) | Sim | Correlacao de logs e eventos |
| `input_type` | enum (`text`, `audio`, `hybrid`) | Sim | Tipo detectado da entrada |
| `text` | string \| null | Condicional | Conteudo textual bruto enviado |
| `audio_file_name` | string \| null | Condicional | Nome do arquivo de audio quando presente |
| `audio_content_type` | string \| null | Condicional | MIME do audio (`audio/*`) |
| `transcription` | string \| null | Nao | Texto resultante de STT |
| `normalized_query` | string | Sim | Pergunta final usada para embedding/matching |
| `created_at` | datetime ISO-8601 | Sim | Timestamp de recebimento |

**Regras de validacao**:
- Pelo menos um entre `text` e `audio` deve estar presente.
- `normalized_query` nao pode ser vazio apos pipeline de normalizacao.
- Quando `audio` for fornecido, transcricao deve atender criterio minimo de confianca.

### 2. RegistroSemantico

Item reutilizavel para cache semantico.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `semantic_id` | string (uuid) | Sim | Identificador unico |
| `query_canonical` | string | Sim | Pergunta canonica registrada |
| `embedding_vector` | list[float] | Sim | Vetor semantico da pergunta |
| `response_text` | string | Sim | Resposta textual reutilizavel |
| `response_audio` | AudioPayload | Sim | Audio associado a resposta |
| `created_at` | datetime ISO-8601 | Sim | Data de criacao |
| `updated_at` | datetime ISO-8601 | Sim | Ultima atualizacao |
| `hit_count` | int | Sim | Numero de reutilizacoes |

**Regras de validacao**:
- `embedding_vector` deve ter dimensao consistente com provider configurado.
- `response_text` e `response_audio` devem existir juntos para manter contrato multimodal.

### 3. RespostaMultimodal

Resposta final entregue ao cliente.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `status` | enum (`success`, `partial_success`, `error`) | Sim | Estado do processamento |
| `source` | enum (`cache_hit`, `cache_miss`) | Sim | Origem da resposta |
| `message_text` | string | Sim | Conteudo textual principal |
| `message_audio` | AudioPayload | Sim | Audio retornado ao cliente |
| `transcription` | string \| null | Nao | Transcricao da entrada em audio |
| `audio_unavailable` | bool | Sim | Marca fallback quando TTS falha |
| `metadata` | ResponseMetadata | Sim | Similaridade, latencia, tracking |

### 4. AudioPayload

Representacao transportavel do audio na resposta.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `mime_type` | string | Sim | Ex.: `audio/mpeg` |
| `encoding` | enum (`base64`) | Sim | Estrategia de codificacao |
| `content` | string | Sim | Conteudo codificado |
| `duration_ms` | int \| null | Nao | Duracao estimada do audio |

### 5. EventoProcessamento

Rastro operacional para observabilidade e auditoria funcional.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `event_id` | string (uuid) | Sim | Identificador do evento |
| `request_id` | string (uuid) | Sim | Relacao com SolicitacaoChat |
| `event_type` | enum (`cache_hit`, `cache_miss`, `stt_failed`, `tts_failed`) | Sim | Tipo de evento |
| `similarity_score` | float \| null | Nao | Similaridade da correspondencia |
| `latency_ms` | int | Sim | Tempo observado da etapa |
| `created_at` | datetime ISO-8601 | Sim | Momento do evento |
| `details` | object | Nao | Metadados nao sensiveis |

## Relacionamentos

- `SolicitacaoChat` -> `RespostaMultimodal`: 1:1 por requisicao bem processada.
- `SolicitacaoChat` -> `EventoProcessamento`: 1:N para rastrear etapas/falhas.
- `RegistroSemantico` -> `RespostaMultimodal`: 1:N ao longo de reutilizacoes (quando `source=cache_hit`).

## Transicoes de Estado

1. `SolicitacaoChat.received` -> `transcribed` (quando `input_type` inclui audio).
2. `transcribed/normalized` -> `matched` (cache hit) ou `unmatched` (cache miss).
3. `matched/unmatched` -> `responded` (sucesso multimodal) ou `partial_responded` (texto sem audio por fallback).
4. Em falhas de STT sem confianca minima: `received` -> `failed_with_recoverable_error`.

## Consideracoes de Performance

- Similaridade deve ser calculada em tempo compativel com meta de latencia para cache hit.
- Reuso de audio evita custo de nova sintese em cache hit.
- Eventos coletados devem permitir medicao de SC-001 ate SC-005.
