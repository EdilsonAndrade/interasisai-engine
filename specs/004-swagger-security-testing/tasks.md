# Tasks: Swagger Security Testing Guide

**Input**: Design documents from `/specs/004-swagger-security-testing/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/swagger-security-api.md

**Tests**: Incluidos, pois a feature exige validacao de seguranca e a constituicao do projeto requer cobertura minima de 80%.

**Organization**: Tasks agrupadas por user story para permitir implementacao e validacao independentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependencia direta)
- **[Story]**: US1, US2, US3
- Cada task inclui caminho exato de arquivo

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar base de documentacao e verificacao inicial do estado atual.

- [X] T001 [Setup] Revisar estado atual de OpenAPI e tags em `presentation/main.py`
- [X] T002 [Setup] Revisar documentacao atual das rotas em `presentation/routes/chat_routes.py`
- [X] T003 [Setup] Revisar documentacao atual das rotas em `presentation/routes/consult_routes.py`
- [X] T004 [Setup] Levantar campos sem descricao em `presentation/schemas.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Estrutura base de seguranca OpenAPI e consistencia de documentacao antes das user stories.

**⚠️ CRITICAL**: Nenhuma US comeca antes desta fase.

- [X] T005 [Foundation] Definir metadados globais da API (title, description, version) em `presentation/main.py`
- [X] T006 [Foundation] Definir `openapi_tags` padronizadas em `presentation/main.py`
- [X] T007 [Foundation] Configurar esquema de seguranca por header `X-Internal-Secret` no OpenAPI em `presentation/main.py`
- [X] T008 [Foundation] Garantir aplicacao do esquema de seguranca em rotas protegidas compartilhadas em `presentation/main.py`
- [X] T009 [P] [Foundation] Criar fixture/utilitario de assercao para OpenAPI em `tests/integration/conftest.py`
- [X] T010 [Foundation] Validar que middleware continua retornando bloqueio padrao sem detalhe sensivel em `presentation/middleware/security_middleware.py`

**Checkpoint**: Base de OpenAPI + seguranca pronta para evoluir por user story.

---

## Phase 3: User Story 1 - Autorizar chamadas internas no Swagger (Priority: P1) 🎯 MVP

**Goal**: Permitir que a UI Swagger aceite `X-Internal-Secret` e execute endpoints protegidos com comportamento correto (200 com chave valida, 403 sem/invalid).

**Independent Test**: Abrir `/docs`, executar endpoint protegido sem chave (bloqueia), com chave invalida (bloqueia) e com chave valida (autoriza).

### Tests for User Story 1 ⚠️

- [X] T011 [P] [US1] Adicionar teste de contrato OpenAPI para security scheme em `tests/integration/test_openapi_swagger_security.py`
- [X] T012 [P] [US1] Adicionar teste de integracao para endpoint protegido sem chave em `tests/integration/test_chat_security_flow.py`
- [X] T013 [P] [US1] Adicionar teste de integracao para endpoint protegido com chave invalida em `tests/integration/test_chat_security_flow.py`
- [X] T014 [P] [US1] Adicionar teste de integracao para endpoint protegido com chave valida em `tests/integration/test_chat_security_flow.py`

### Implementation for User Story 1

- [X] T015 [US1] Aplicar dependencias/tag de seguranca nas rotas de chat em `presentation/routes/chat_routes.py`
- [X] T016 [US1] Aplicar dependencias/tag de seguranca nas rotas de consult em `presentation/routes/consult_routes.py`
- [X] T017 [US1] Ajustar docs de erro de autorizacao nas rotas protegidas em `presentation/routes/chat_routes.py`
- [X] T018 [US1] Ajustar docs de erro de autorizacao nas rotas protegidas em `presentation/routes/consult_routes.py`
- [X] T019 [US1] Garantir consistencia do nome do header entre OpenAPI e validacao em `infra/security/secret_validator.py`
- [X] T020 [US1] Rodar subset de testes de seguranca e corrigir regressao em `tests/integration/test_chat_security_flow.py`

**Checkpoint**: US1 funcional e testavel isoladamente.

---

## Phase 4: User Story 2 - Entender rapidamente o contrato da API (Priority: P2)

**Goal**: Exibir metadados claros e organizar endpoints por tags funcionais no Swagger.

**Independent Test**: Conferir no `/docs` titulo, descricao, versao e agrupamento coerente das rotas.

### Tests for User Story 2 ⚠️

- [X] T021 [P] [US2] Adicionar teste de metadata OpenAPI (title/description/version) em `tests/integration/test_openapi_swagger_security.py`
- [X] T022 [P] [US2] Adicionar teste de presenca de tags funcionais no OpenAPI em `tests/integration/test_openapi_swagger_security.py`
- [X] T023 [P] [US2] Adicionar teste unitario para schemas com descricoes minimas em `tests/unit/test_schema_descriptions.py`

### Implementation for User Story 2

- [X] T024 [US2] Refinar descricoes das tags e agrupamentos no app FastAPI em `presentation/main.py`
- [X] T025 [US2] Padronizar `tags` nos endpoints de chat em `presentation/routes/chat_routes.py`
- [X] T026 [US2] Padronizar `tags` nos endpoints de consult em `presentation/routes/consult_routes.py`
- [X] T027 [US2] Adicionar/ajustar `Field(description=...)` em request/response models de `presentation/schemas.py`
- [X] T028 [US2] Revisar coerencia textual de summary/description de endpoints em `presentation/routes/chat_routes.py`
- [X] T029 [US2] Revisar coerencia textual de summary/description de endpoints em `presentation/routes/consult_routes.py`

**Checkpoint**: US1 + US2 independentes, com Swagger navegavel e contratos claros.

---

## Phase 5: User Story 3 - Executar roteiro de teste pelo Swagger (Priority: P3)

**Goal**: Consolidar um passo a passo executavel para homologacao via Swagger, com pre-requisitos, chaves e evidencias.

**Independent Test**: Seguir `quickstart.md` do zero e reproduzir os 3 cenarios com resultados esperados.

### Tests for User Story 3 ⚠️

- [X] T030 [P] [US3] Adicionar teste de smoke para endpoint de docs acessivel em `tests/integration/test_openapi_swagger_security.py`
- [X] T031 [P] [US3] Adicionar teste de regressao do fluxo protegido alinhado ao quickstart em `tests/integration/test_chat_security_flow.py`

### Implementation for User Story 3

- [X] T032 [US3] Atualizar roteiro operacional final no artefato de feature em `specs/004-swagger-security-testing/quickstart.md`
- [X] T033 [US3] Validar consistencia entre contrato e roteiro em `specs/004-swagger-security-testing/contracts/swagger-security-api.md`
- [X] T034 [US3] Sincronizar linguagem do passo a passo no contexto de feature em `specs/004-swagger-security-testing/spec.md`
- [ ] T035 [US3] Executar roteiro manual no `/docs` e registrar evidencias no PR/issue da feature

**Checkpoint**: Todas as user stories completas e validadas de forma independente.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Fechamento tecnico e qualidade transversal.

- [X] T036 [P] [Polish] Rodar suite completa de testes com cobertura em `tests/` (`pytest --cov=. --cov-report=term-missing`)
- [X] T037 [Polish] Garantir cobertura minima de 80% e ajustar testes faltantes em `tests/unit/` e `tests/integration/`
- [X] T038 [Polish] Revisar complexidade das funcoes alteradas (< 5) em `presentation/main.py`, `presentation/routes/chat_routes.py`, `presentation/routes/consult_routes.py`
- [X] T039 [Polish] Revisar padroes de seguranca (sem vazamento de segredo) em `presentation/middleware/security_middleware.py`
- [X] T040 [Polish] Atualizar notas de mudanca no contexto Speckit em `.github/copilot-instructions.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: inicia imediatamente
- **Phase 2 (Foundation)**: depende da Setup e bloqueia US1-US3
- **Phases 3-5 (User Stories)**: dependem da Foundation
- **Phase 6 (Polish)**: depende das USs selecionadas concluidas

### User Story Dependencies

- **US1 (P1)**: inicia apos Foundation; entrega MVP da feature
- **US2 (P2)**: inicia apos Foundation; pode acontecer paralelo a US1 por pessoas diferentes
- **US3 (P3)**: inicia apos Foundation e se beneficia de US1/US2 concluidas

### Within Each User Story

- Escrever testes primeiro e validar falha inicial
- Implementar ajustes de codigo
- Rodar testes da US
- Validar criterios de aceite da US

### Parallel Opportunities

- T009 pode ser paralelo a T010
- T011-T014 podem rodar em paralelo
- T021-T023 podem rodar em paralelo
- T030-T031 podem rodar em paralelo
- T036 e verificacoes finais podem rodar junto de revisao documental

---

## Parallel Example: User Story 1

```bash
# Testes de seguranca em paralelo
Task: T011 tests/integration/test_consult_contract_validation.py
Task: T012 tests/integration/test_chat_security_flow.py
Task: T013 tests/integration/test_chat_security_flow.py
Task: T014 tests/integration/test_chat_security_flow.py

# Implementacao em paralelo por arquivo
Task: T015 presentation/routes/chat_routes.py
Task: T016 presentation/routes/consult_routes.py
Task: T019 infra/security/secret_validator.py
```

---

## Implementation Strategy

### MVP First (US1)

1. Concluir Phase 1 + Phase 2
2. Entregar US1 completa
3. Validar os 3 cenarios de autorizacao no Swagger
4. Demonstrar MVP

### Incremental Delivery

1. US1 (autorizacao no Swagger)
2. US2 (metadados/tags/schemas claros)
3. US3 (roteiro operacional completo + evidencias)
4. Polish final com cobertura e seguranca

### Parallel Team Strategy

1. Pessoa A: US1 (seguranca)
2. Pessoa B: US2 (documentacao e schemas)
3. Pessoa C: US3 (quickstart, evidencias e alinhamento contratual)

---

## Notes

- Tarefas com [P] evitam conflito por arquivo e podem ser executadas em paralelo.
- Cada US mantém capacidade de validacao independente.
- Sempre validar que erros de autorizacao nao exponham detalhes sensiveis.
- Em caso de divergencia entre docs e comportamento real, o comportamento real seguro prevalece e a docs deve ser corrigida imediatamente.
