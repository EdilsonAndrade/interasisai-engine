# Tasks: Cache Semantico e Resposta em Audio

**Input**: Design documents from `/specs/003-semantic-cache-tts/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chat-process-api.md, quickstart.md

**Tests**: Incluidos porque a feature exige cobertura minima de 80% e validacao independente por historia.

**Organization**: Tasks agrupadas por user story para implementacao e validacao independentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode executar em paralelo (arquivos diferentes, sem dependencia de tarefa incompleta)
- **[Story]**: Mapeamento da tarefa para a user story (US1, US2, US3)
- Cada tarefa inclui caminho de arquivo alvo

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar configuracoes e estrutura minima da feature.

- [X] T001 Atualizar dependencias e pins de bibliotecas multimodais em requirements.txt
- [X] T002 Atualizar configuracoes da feature (`SEMANTIC_MATCH_THRESHOLD`, `STT_MIN_CONFIDENCE`) em infra/config/settings.py
- [X] T003 [P] Criar pacote de provedores semanticos em infra/semantic/__init__.py
- [X] T004 [P] Criar pacote de provedores de speech em infra/speech/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Base arquitetural obrigatoria antes de qualquer user story.

**⚠️ CRITICAL**: Nenhuma user story deve comecar antes do fim desta fase.

- [X] T005 Definir interfaces `SemanticCacheRepository`, `EmbeddingProvider`, `STTProvider`, `TTSProvider` em domain/interfaces.py
- [X] T006 [P] Adicionar modelos de dominio `AudioPayload`, `RespostaMultimodal`, `RegistroSemantico`, `EventoProcessamento` em domain/models.py
- [X] T007 [P] Adicionar excecoes controladas de pipeline multimodal em domain/exceptions.py
- [X] T008 Implementar repositorio de cache semantico em memoria em infra/semantic/in_memory_semantic_cache.py
- [X] T009 [P] Implementar provider stub de embeddings em infra/semantic/embedding_provider_stub.py
- [X] T010 [P] Implementar provider stub de transcricao STT em infra/speech/stt_provider_stub.py
- [X] T011 [P] Implementar provider stub de sintese TTS em infra/speech/tts_provider_stub.py
- [X] T012 Configurar injecao de dependencias dos novos providers/servicos em presentation/main.py

**Checkpoint**: Fundacao pronta para iniciar user stories em paralelo por capacidade do time.

---

## Phase 3: User Story 1 - Reutilizar resposta semantica (Priority: P1) 🎯 MVP

**Goal**: Reaproveitar respostas semanticamente equivalentes para reduzir latencia e custo.

**Independent Test**: Duas perguntas equivalentes devem resultar em `cache_miss` na primeira chamada e `cache_hit` na segunda, com contrato consistente.

### Tests for User Story 1

- [X] T013 [P] [US1] Criar testes unitarios de similaridade e threshold em tests/unit/test_semantic_cache_service.py
- [X] T014 [P] [US1] Criar teste de integracao de fluxo cache hit/miss em tests/integration/test_chat_cache_flow.py

### Implementation for User Story 1

- [X] T015 [US1] Implementar servico de matching semantico e decisao hit/miss em application/services/semantic_cache_service.py
- [X] T016 [US1] Orquestrar consulta ao cache antes do provider LLM e persistencia de miss em application/services/langchain_chat_use_case.py
- [X] T017 [US1] Ajustar endpoint para retornar `source`, `similarity_score` e `threshold` em presentation/routes/chat_routes.py
- [X] T018 [US1] Registrar eventos operacionais `cache_hit` e `cache_miss` com `request_id` e `latency_ms` em infra/logging/logger.py

**Checkpoint**: US1 funcional e testavel de forma independente (MVP).

---

## Phase 4: User Story 2 - Receber resposta em texto e audio (Priority: P2)

**Goal**: Entregar payload multimodal completo (texto + audio) tanto em hit quanto em miss.

**Independent Test**: Uma requisicao valida deve retornar `message.text`, `message.audio` e `audio_unavailable` com shape consistente.

### Tests for User Story 2

- [X] T019 [P] [US2] Criar testes unitarios de serializacao do payload de audio em tests/unit/test_chat_response_schema.py
- [X] T020 [P] [US2] Criar teste de integracao para consistencia do retorno multimodal em tests/integration/test_chat_multimodal_response.py

### Implementation for User Story 2

- [X] T021 [P] [US2] Estender DTO de resposta multimodal (`message.audio`, `audio_unavailable`, `metadata`) em application/dto/response.py
- [X] T022 [P] [US2] Atualizar schemas de API para resposta multimodal consistente em presentation/schemas.py
- [X] T023 [US2] Integrar geracao/reuso de audio via TTS no fluxo principal em application/services/langchain_chat_use_case.py
- [X] T024 [US2] Garantir reutilizacao de audio existente em cache hit em application/services/semantic_cache_service.py
- [X] T025 [US2] Implementar fallback `partial_success` quando TTS falhar em presentation/routes/chat_routes.py

**Checkpoint**: US2 funcional e testavel sem regressao de US1.

---

## Phase 5: User Story 3 - Processar entrada por voz (Priority: P3)

**Goal**: Aceitar audio como entrada, transcrever e seguir o mesmo fluxo semantico multimodal.

**Independent Test**: Requisicao com `audio` deve retornar `transcription` e resposta multimodal; em baixa confianca STT deve retornar erro controlado 422.

### Tests for User Story 3

- [X] T026 [P] [US3] Criar testes unitarios de validacao de entrada audio e confianca STT em tests/unit/test_speech_pipeline.py
- [X] T027 [P] [US3] Criar teste de integracao para fluxo de entrada por voz em tests/integration/test_chat_voice_input_flow.py

### Implementation for User Story 3

- [X] T028 [P] [US3] Estender DTO de entrada para suportar `text`, `audio` e modo hibrido em application/dto/request.py
- [X] T029 [US3] Implementar parsing multipart e normalizacao de entrada multimodal em presentation/routes/chat_routes.py
- [X] T030 [US3] Integrar etapa de transcricao STT e propagacao de `transcription` no caso de uso em application/services/langchain_chat_use_case.py
- [X] T031 [US3] Retornar erro funcional `TRANSCRIPTION_FAILED` (422) sem vazamento sensivel em presentation/routes/chat_routes.py

**Checkpoint**: US3 funcional e testavel sem depender de novos endpoints.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Consolidar qualidade, seguranca e documentacao da feature completa.

- [X] T032 [P] Adicionar regressao de seguranca para multipart com segredo ausente/invalido em tests/integration/test_chat_security_flow.py
- [X] T033 [P] Atualizar contrato final da API com cenarios hit/miss/fallback em specs/003-semantic-cache-tts/contracts/chat-process-api.md
- [X] T034 [P] Atualizar roteiro de validacao e comandos de smoke test em specs/003-semantic-cache-tts/quickstart.md
- [X] T035 Ajustar criterios de cobertura e execucao de testes em pytest.ini
- [X] T036 Executar suite completa e registrar ajustes finais de wiring da feature em presentation/main.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: sem dependencias
- **Phase 2 (Foundational)**: depende da Phase 1 e bloqueia todas as user stories
- **Phase 3-5 (User Stories)**: dependem da Phase 2
- **Phase 6 (Polish)**: depende das historias selecionadas para entrega

### User Story Dependencies

- **US1 (P1)**: inicia apos Foundational e entrega o MVP
- **US2 (P2)**: inicia apos Foundational; integra com artefatos de US1 para reuso de audio
- **US3 (P3)**: inicia apos Foundational; reutiliza contrato multimodal consolidado em US2

### Recommended Delivery Order

1. US1 (MVP)
2. US2
3. US3

### Within Each User Story

- Testes primeiro (devem falhar antes da implementacao)
- DTOs/modelos antes de servicos
- Servicos antes de rota/endpoint
- Endpoint antes de validacoes de integracao final

### Parallel Opportunities

- Setup: T003-T004 em paralelo
- Foundational: T006-T007 e T009-T011 em paralelo
- US1: T013-T014 em paralelo
- US2: T019-T020 e T021-T022 em paralelo
- US3: T026-T027 em paralelo
- Polish: T032-T034 em paralelo

---

## Parallel Example: User Story 1

```bash
# Executar testes de US1 em paralelo
Task: "T013 [US1] tests/unit/test_semantic_cache_service.py"
Task: "T014 [US1] tests/integration/test_chat_cache_flow.py"

# Implementacoes desacopladas por arquivo (apos base pronta)
Task: "T015 [US1] application/services/semantic_cache_service.py"
Task: "T018 [US1] infra/logging/logger.py"
```

---

## Parallel Example: User Story 2

```bash
# Contratos e schema podem avancar em paralelo
Task: "T021 [US2] application/dto/response.py"
Task: "T022 [US2] presentation/schemas.py"

# Testes de US2 em paralelo
Task: "T019 [US2] tests/unit/test_chat_response_schema.py"
Task: "T020 [US2] tests/integration/test_chat_multimodal_response.py"
```

---

## Parallel Example: User Story 3

```bash
# Testes de entrada por voz em paralelo
Task: "T026 [US3] tests/unit/test_speech_pipeline.py"
Task: "T027 [US3] tests/integration/test_chat_voice_input_flow.py"

# DTO de entrada e rota podem ocorrer em etapas coordenadas
Task: "T028 [US3] application/dto/request.py"
Task: "T029 [US3] presentation/routes/chat_routes.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Concluir Phase 1 e Phase 2
2. Concluir US1 (T013-T018)
3. Validar criterios independentes de US1
4. Demonstrar/entregar MVP

### Incremental Delivery

1. Base comum (Phase 1-2)
2. Entregar US1 e validar
3. Entregar US2 e validar
4. Entregar US3 e validar
5. Executar polish final sem quebrar contratos

### Parallel Team Strategy

1. Time fecha Setup + Foundational
2. Apos fundacao:
   - Dev A: US1
   - Dev B: US2
   - Dev C: US3
3. Consolidar em Phase 6 com regressao completa

---

## Notes

- Tarefas com `[P]` evitam conflito de arquivo e dependencia de resultado intermediario
- Cada user story possui criterio de teste independente
- Ordem sugerida prioriza ganho de valor rapido (US1) e reduz risco de regressao
- Manter logs sem payload sensivel e sem segredos em todas as fases
