# Implementation Plan: Recepcao Segura de Input de Chat

**Branch**: `002-init-ai-engine-security` | **Date**: 2026-04-25 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/002-secure-chat-intake/spec.md`  
**Related Issue**: EDI-24

## Summary

Habilitar o motor FastAPI a receber chamadas internas do BFF com seguranca rigida e preparar o ecossistema LangChain para futura orquestracao conversacional. Esta fase entrega: (1) endpoint `POST /api/v1/chat/process` com aceite de texto e audio via `multipart/form-data`; (2) Gatekeeper de seguranca via middleware existente, garantindo 403 para requisicoes sem `X-Internal-Secret` valido; (3) caso de uso `LangChainChatUseCase` com resposta simulada e sem chamadas reais a LLM; (4) inclusao das bibliotecas `langchain`, `langchain-core`, `langchain-community` e `langchain-google-genai` em `requirements.txt`.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, Uvicorn, Pydantic v2, python-dotenv, python-multipart, langchain, langchain-core, langchain-community, langchain-google-genai  
**Storage**: N/A (sem persistencia nesta fase)  
**Testing**: pytest, pytest-cov, pytest-asyncio, httpx (TestClient assincrono)  
**Target Platform**: Linux container (homologacao/producao); Windows/Mac/Linux (dev local)  
**Project Type**: web-service (API interna)  
**Performance Goals**: latencia p95 < 2s para fluxo simulado em homologacao (SC-003)  
**Constraints**: zero chamadas externas para concluir fluxo principal; complexidade ciclomatica < 5 por funcao; cobertura >= 80%  
**Scale/Scope**: trafego baixo (BFF interno); 1 endpoint novo, 1 caso de uso, schemas Pydantic, ajustes em `requirements.txt`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Verificacao | Resultado |
|-----------|-------------|-----------|
| I. Clean Architecture | Endpoint em `presentation/routes/`, caso de uso em `application/services/`, schemas em `presentation/schemas.py` (ou `application/dto`), seguranca em `infra/security/` + middleware em `presentation/middleware/` | PASS |
| II. Cobertura de testes >= 80% (unit + integration + mocks) | Plano de testes cobre middleware, caso de uso, schemas e fluxo end-to-end com mocks de I/O e ambiente | PASS |
| III. SOLID + complexidade ciclomatica < 5 | Caso de uso isolado, validacao decomposta em metodos pequenos, sem branches excessivas | PASS |
| IV. Security First (segredos em ambiente, .env no .gitignore, 403 sem vazar motivo) | Reutiliza `X_INTERNAL_SECRET` via `infra/config/settings.py`; resposta 403 generica; logs internos contem motivo | PASS |
| V. Abstracao + Injecao de Dependencia | Caso de uso recebido via `Depends`; logger e settings injetaveis; preparado para substituir mock por chain real | PASS |
| LLM Integration Readiness | LangChain instalado e importavel; caso de uso ja reside na camada de aplicacao para receber chains futuras sem refactor | PASS |

Sem violacoes. Tabela de complexidade nao se aplica.

## Project Structure

### Documentation (this feature)

```text
specs/002-secure-chat-intake/
├── plan.md                       # Este arquivo
├── research.md                   # Decisoes tecnicas (Phase 0)
├── data-model.md                 # Entidades e contratos internos (Phase 1)
├── quickstart.md                 # Setup e verificacao (Phase 1)
├── contracts/
│   └── chat-process-api.md       # Contrato do endpoint (Phase 1)
├── checklists/
│   └── requirements.md           # Checklist de qualidade da spec
└── tasks.md                      # Phase 2 (gerado por /speckit.tasks)
```

### Source Code (repository root)

```text
application/
├── dto/
│   ├── request.py                # + ChatProcessRequest (form bindings)
│   └── response.py               # + ChatProcessResponse
└── services/
    └── langchain_chat_use_case.py  # NOVO: caso de uso simulado

domain/
├── exceptions.py                 # + EmptyChatInputError (se necessario)
├── interfaces.py                 # + IChatUseCase (preparacao)
└── models.py                     # + entidades efemeras de chat

infra/
├── config/settings.py            # Reuso (sem mudanca estrutural)
├── logging/logger.py             # Reuso para logar negacoes/sucessos
└── security/
    ├── secret_loader.py          # Reuso
    └── secret_validator.py       # Reuso

presentation/
├── main.py                       # Registro do novo router
├── middleware/security_middleware.py  # Reuso (cobre nova rota)
├── routes/
│   └── chat_routes.py            # NOVO: POST /api/v1/chat/process
└── schemas.py                    # + schemas de chat

tests/
├── unit/
│   ├── test_langchain_chat_use_case.py   # NOVO
│   ├── test_chat_schemas.py              # NOVO
│   └── test_security_validator.py        # Reuso (eventual ajuste)
└── integration/
    ├── test_chat_endpoint.py             # NOVO (texto, audio, sem conteudo)
    ├── test_chat_security_flow.py        # NOVO (sem segredo / segredo invalido)
    └── test_langchain_imports.py         # NOVO (smoke test de imports)

requirements.txt                  # + langchain, langchain-core, langchain-community, langchain-google-genai
```

**Structure Decision**: manter o layout Clean Architecture ja consolidado pela feature 001 (sem prefixo `src/`). O novo router de chat fica em `presentation/routes/chat_routes.py`, o caso de uso em `application/services/langchain_chat_use_case.py`, e os schemas Pydantic em `presentation/schemas.py` (ou em `application/dto/` quando usados como contrato de aplicacao).

## Phase 0: Outline & Research

Concluida. Ver [research.md](./research.md). Todos os pontos de NEEDS CLARIFICATION foram resolvidos. Decisoes principais:

1. LangChain como framework de orquestracao (instalacao apenas; uso real fica para fase futura).
2. Reuso do middleware existente para `X-Internal-Secret`.
3. Endpoint multimodal via `multipart/form-data` com `text` e `audio` opcionais (ao menos um obrigatorio).
4. `LangChainChatUseCase` retornando payload simulado padronizado.
5. Estrutura mantida sem prefixo `src/`.
6. Logging de negacoes via logger central existente.
7. Estrategia de testes unit + integration + smoke do import LangChain.

## Phase 1: Design & Contracts

Concluida. Artefatos gerados:

- [data-model.md](./data-model.md): entidades `ChatProcessRequest`, `ChatProcessResponse`, `SecurityContext`, `AccessDenialEvent`.
- [contracts/chat-process-api.md](./contracts/chat-process-api.md): contrato HTTP do endpoint, headers, body multipart, respostas 200/403/422/500, exemplos curl.
- [quickstart.md](./quickstart.md): setup local, comandos curl de validacao e checklist de prontidao.
- Atualizacao do agent context: `.github/copilot-instructions.md` aponta para este plano (entre marcadores SPECKIT).

### Re-avaliacao da Constitution Check (pos-design)

Apos detalhar contratos e camadas, todas as gates continuam **PASS**. Os schemas e o caso de uso preservam SOLID, a seguranca e mantida no middleware central, e a estrutura de pastas respeita Clean Architecture. Nenhuma justificativa de complexidade adicional necessaria.

## Complexity Tracking

> Sem violacoes da constituicao. Tabela nao preenchida.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | (n/a) | (n/a) |
