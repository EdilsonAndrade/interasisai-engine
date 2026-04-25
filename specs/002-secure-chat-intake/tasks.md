---
description: "Task list for Recepcao Segura de Input de Chat (EDI-24)"
---

# Tasks: Recepcao Segura de Input de Chat

**Input**: Design documents from `/specs/002-secure-chat-intake/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chat-process-api.md, quickstart.md  
**Branch**: `002-init-ai-engine-security`  
**Related Issue**: EDI-24

**Tests**: Incluidos. A constituicao exige cobertura >= 80% com unit + integration + mocks; tests sao MANDATORY nesta feature.

**Organization**: Tarefas agrupadas por user story (US1, US2, US3) para entrega incremental e validacao independente.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependencia)
- **[Story]**: User story alvo (US1, US2, US3)
- Caminhos absolutos a partir da raiz do repositorio

## Path Conventions

Projeto Python single-root, Clean Architecture sem prefixo `src/`:
- Codigo em `domain/`, `application/`, `infra/`, `presentation/`
- Testes em `tests/unit/`, `tests/integration/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Atualizar o ambiente para LangChain e garantir que o motor pode importar as bibliotecas exigidas pela EDI-24.

- [X] T001 Adicionar `langchain`, `langchain-core`, `langchain-community` e `langchain-google-genai` ao `requirements.txt`
- [X] T002 Instalar dependencias atualizadas executando `pip install -r requirements.txt` no `.venv`
- [X] T003 [P] Atualizar `presentation/main.py` para importar `langchain` no boot e expor falha clara se a importacao falhar (smoke import)

**Checkpoint**: Dependencias LangChain instaladas e importaveis no boot da aplicacao.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Estrutura base compartilhada por todas as user stories (modelos de dominio, schemas, ponto de injecao do router).

**CRITICAL**: Nenhuma user story pode comecar antes da conclusao desta fase.

- [X] T004 [P] Criar entidades efemeras de chat (`ChatInput`, `ChatResult`, `AccessDenialEvent`) em `domain/models.py`
- [X] T005 [P] Adicionar excecao `EmptyChatInputError` em `domain/exceptions.py`
- [X] T006 [P] Definir interface `IChatUseCase` em `domain/interfaces.py` (contrato para o caso de uso de chat)
- [X] T007 [P] Adicionar schema Pydantic `ChatProcessResponseSchema` (com sub-objeto `received`) em `presentation/schemas.py`
- [X] T008 [P] Adicionar DTOs `ChatProcessRequestDTO` em `application/dto/request.py` e `ChatProcessResponseDTO` em `application/dto/response.py`
- [X] T009 Criar arquivo vazio `presentation/routes/chat_routes.py` com `APIRouter` e registra-lo em `presentation/main.py` sob o prefixo `/api/v1/chat`
- [X] T010 Garantir que o middleware existente em `presentation/middleware/security_middleware.py` cobre o novo prefixo `/api/v1/chat` (ajustar lista de rotas protegidas se necessario)
- [X] T011 Estender `infra/logging/logger.py` (ou helpers existentes) para emitir log estruturado de `AccessDenialEvent` (`reason`, `path`, `client_host`) em nivel `warning`

**Checkpoint**: Estrutura, schemas, DTOs, router stub, middleware e logging prontos. User stories podem comecar.

---

## Phase 3: User Story 1 - Bloquear acessos nao autorizados (Priority: P1) - MVP

**Goal**: Garantir que toda chamada ao endpoint de chat sem `X-Internal-Secret` valido seja bloqueada com 403, antes de qualquer processamento, e registrada em log.

**Independent Test**: enviar requisicao sem header e com header invalido para `/api/v1/chat/process` e validar resposta 403 + log de negacao; enviar com segredo valido e confirmar que a requisicao chega ao handler.

### Tests for User Story 1

- [X] T012 [P] [US1] Criar teste de integracao para 403 sem header em `tests/integration/test_chat_security_flow.py`
- [X] T013 [P] [US1] Adicionar caso de teste para 403 com `X-Internal-Secret` invalido em `tests/integration/test_chat_security_flow.py`
- [X] T014 [P] [US1] Adicionar teste unitario verificando que negacoes geram log `warning` com `reason` em `tests/unit/test_security_validator.py`
- [X] T015 [P] [US1] Adicionar teste de integracao confirmando que requisicao com segredo valido passa pelo middleware e atinge o handler em `tests/integration/test_chat_security_flow.py`

### Implementation for User Story 1

- [X] T016 [US1] Implementar handler stub em `presentation/routes/chat_routes.py` (`POST /process`) que retorna 200 fixo somente para validar passagem pelo middleware
- [X] T017 [US1] Ajustar `presentation/middleware/security_middleware.py` para registrar `AccessDenialEvent` via logger sempre que negar acesso, sem expor motivo no corpo da resposta
- [X] T018 [US1] Garantir resposta 403 padronizada `{"detail": "Forbidden"}` em `presentation/middleware/security_middleware.py`

**Checkpoint**: Endpoint protegido por middleware. Acessos nao autorizados sao bloqueados e logados; acessos autorizados chegam ao handler.

---

## Phase 4: User Story 2 - Receber entrada texto/audio (Priority: P2)

**Goal**: Endpoint `/api/v1/chat/process` aceita `multipart/form-data` com `text` e/ou `audio` (UploadFile), valida que ao menos um conteudo foi enviado e retorna resposta estruturada simulada.

**Independent Test**: enviar requisicao autorizada apenas com `text`, apenas com `audio`, e sem nenhum dos dois, validando 200 nas duas primeiras e 422 na terceira.

### Tests for User Story 2

- [X] T019 [P] [US2] Teste de integracao com payload contendo apenas `text` em `tests/integration/test_chat_endpoint.py`
- [X] T020 [P] [US2] Teste de integracao com payload contendo apenas `audio` (UploadFile) em `tests/integration/test_chat_endpoint.py`
- [X] T021 [P] [US2] Teste de integracao retornando 422 quando nem `text` nem `audio` sao enviados em `tests/integration/test_chat_endpoint.py`
- [X] T022 [P] [US2] Teste unitario do schema `ChatProcessResponseSchema` (campos obrigatorios e tipos) em `tests/unit/test_chat_schemas.py`
- [X] T023 [P] [US2] Teste unitario validando rejeicao de `audio` com content-type que nao inicia em `audio/` em `tests/unit/test_chat_schemas.py`

### Implementation for User Story 2

- [X] T024 [US2] Implementar handler `POST /process` em `presentation/routes/chat_routes.py` aceitando `text: str | None = Form(None)`, `audio: UploadFile | None = File(None)` e `session_id: str | None = Form(None)`, retornando `ChatProcessResponseSchema`
- [X] T025 [US2] Implementar validacao "ao menos um entre text e audio" em `application/services/langchain_chat_use_case.py` e mapear erro para `EmptyChatInputError`
- [X] T026 [US2] Mapear `EmptyChatInputError` para resposta HTTP 422 com payload `{"status": "validation_error", "detail": ...}` em `presentation/routes/chat_routes.py`
- [X] T027 [US2] Validar content-type do `audio` (`audio/...`) em `application/services/langchain_chat_use_case.py`, retornando 422 quando invalido
- [X] T028 [US2] Construir objeto `received` (`has_text`, `has_audio`, `audio_filename`, `session_id`) na resposta de sucesso em `application/services/langchain_chat_use_case.py`

**Checkpoint**: Endpoint aceita texto e audio, valida ausencia de conteudo e responde no formato contratual.

---

## Phase 5: User Story 3 - Prontidao da camada LangChain sem chamadas externas (Priority: P3)

**Goal**: Caso de uso `LangChainChatUseCase` reside na camada de aplicacao, retorna o payload simulado padronizado (`status: success`, `agent_reply: "Conexao segura estabelecida. Motor LangChain pronto."`) e nao realiza chamadas externas, preparando o ponto de extensao para a chain real.

**Independent Test**: instanciar o caso de uso sem rede disponivel e confirmar que retorna o payload simulado para entrada valida.

### Tests for User Story 3

- [X] T029 [P] [US3] Teste unitario do `LangChainChatUseCase` para entrada valida (texto) em `tests/unit/test_langchain_chat_use_case.py`
- [X] T030 [P] [US3] Teste unitario do `LangChainChatUseCase` para entrada valida (audio) em `tests/unit/test_langchain_chat_use_case.py`
- [X] T031 [P] [US3] Teste unitario garantindo que nenhum cliente HTTP/LLM e invocado durante a execucao do caso de uso (mock de rede) em `tests/unit/test_langchain_chat_use_case.py`
- [X] T032 [P] [US3] Teste de integracao smoke validando `import langchain`, `langchain_core`, `langchain_community`, `langchain_google_genai` em `tests/integration/test_langchain_imports.py`

### Implementation for User Story 3

- [X] T033 [US3] Implementar `LangChainChatUseCase` em `application/services/langchain_chat_use_case.py` implementando `IChatUseCase` e retornando o payload simulado fixo
- [X] T034 [US3] Cadastrar provider de injecao de dependencia (`Depends(get_chat_use_case)`) em `presentation/routes/chat_routes.py` referenciando o caso de uso
- [X] T035 [US3] Adicionar logging `info` com `has_text`/`has_audio`/`session_id` (sem conteudo) ao final do caso de uso em `application/services/langchain_chat_use_case.py`

**Checkpoint**: Camada de aplicacao pronta para receber chains reais sem refactor; fluxo completo passa sem chamadas externas.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T036 [P] Atualizar `presentation/schemas.py` e DTOs com docstrings curtas dos novos contratos
- [ ] T037 [P] Atualizar `README.md` (secao de endpoints) descrevendo `POST /api/v1/chat/process`, headers e formato multipart  *(skipped: o repositorio nao possui README.md ainda; documentacao do endpoint disponivel em [contracts/chat-process-api.md](./contracts/chat-process-api.md) e [quickstart.md](./quickstart.md))*
- [X] T038 [P] Atualizar `.env.example` se algum novo nome de variavel for introduzido (default: nenhum nesta fase, apenas confirmar `X_INTERNAL_SECRET`)
- [X] T039 Rodar `pytest --cov=. --cov-report=term-missing` e garantir cobertura total >= 80% com todos os testes verdes
- [ ] T040 Executar o roteiro do [quickstart.md](./quickstart.md) (4.1 a 4.4) e registrar resultado no checklist da feature  *(deferred: requer servidor live em homologacao; cenarios equivalentes cobertos por testes de integracao automatizados)*
- [ ] T041 Revisar logs de negacao em homologacao para confirmar ausencia de vazamento de segredo (apenas `reason` interno)  *(deferred: requer ambiente de homologacao; coberto por `tests/unit/test_middleware_denial_logging.py`)*

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependencia previa
- **Foundational (Phase 2)**: depende da Phase 1 e BLOQUEIA todas as user stories
- **User Stories (Phase 3-5)**: dependem da Phase 2; podem rodar em paralelo apos a foundational. Ordem por prioridade recomendada: US1 -> US2 -> US3
- **Polish (Phase 6)**: depende das user stories alvo do release

### User Story Dependencies

- **US1**: independente apos Foundational
- **US2**: independente apos Foundational; integra-se ao handler criado em US1 sem quebrar a US1
- **US3**: independente apos Foundational; refina o caso de uso usado pelo handler de US2 (pode ser feita antes de US2 se preferir mockar o handler)

### Within Each User Story

- Tests primeiro (devem falhar antes da implementacao)
- Modelos/DTOs ja prontos na Phase 2
- Caso de uso antes do handler (ou mocks adequados)
- Handler antes da integracao final

### Parallel Opportunities

- T003 paralelo a T001/T002 apos requirements atualizados
- T004-T008 paralelos entre si (arquivos distintos)
- T012-T015 paralelos (mesmo arquivo de testes mas casos independentes; cuidado com merge - se preferir, separe em commits)
- T019-T023 paralelos
- T029-T032 paralelos
- Polish T036-T038 paralelos

---

## Parallel Example: User Story 1

```bash
# Lancar testes da US1 em paralelo (apos Phase 2):
Task: "Teste de integracao 403 sem header em tests/integration/test_chat_security_flow.py" (T012)
Task: "Teste de integracao 403 com header invalido em tests/integration/test_chat_security_flow.py" (T013)
Task: "Teste unitario log de negacao em tests/unit/test_security_validator.py" (T014)
Task: "Teste de integracao acesso autorizado chega ao handler em tests/integration/test_chat_security_flow.py" (T015)
```

---

## Implementation Strategy

### MVP First (US1)

1. Concluir Phase 1 (LangChain instalado)
2. Concluir Phase 2 (estrutura, DTOs, router stub, middleware cobrindo nova rota)
3. Concluir Phase 3 (US1) com handler stub e middleware logando negacoes
4. Validar US1 isoladamente (testes 403 e log)
5. Demo possivel: motor recusa chamadas nao autorizadas e aceita autorizadas com 200 fixo

### Incremental Delivery

1. Setup + Foundational
2. US1 -> validar -> demo
3. US2 -> validar (texto/audio/empty) -> demo
4. US3 -> validar (caso de uso simulado + smoke import) -> demo
5. Polish + cobertura final

### Parallel Team Strategy

- Dev A: Phase 1 + T003
- Dev B/C: Phase 2 (T004-T011 em paralelo)
- Apos Phase 2: Dev A em US1, Dev B em US3 (caso de uso), Dev C em US2 (handler/schemas) com integracao incremental

---

## Notes

- [P] = arquivos distintos sem dependencia
- Manter complexidade ciclomatica < 5 por funcao (constituicao III)
- Nao logar conteudo de `text` ou bytes de `audio`; somente metadados
- Resposta 403 deve ser generica (`{"detail": "Forbidden"}`); detalhes apenas em log
- Apos cada checkpoint, rodar pytest com cobertura para acompanhar a meta de 80%
