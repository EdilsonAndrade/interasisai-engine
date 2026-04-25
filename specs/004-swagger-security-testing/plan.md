# Implementation Plan: Swagger Security Testing Guide

**Branch**: `004-create-feature-branch` | **Date**: 2026-04-25 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/004-swagger-security-testing/spec.md`  
**Related Issue**: EDI-29

## Summary

Implementar a melhoria da documentacao interativa para que o Swagger suporte autorizacao por `X-Internal-Secret`, organize endpoints por categorias funcionais e publique metadados claros da API. A entrega tambem inclui reforco documental com roteiro passo a passo de teste manual via Swagger (pre-requisitos, chaves necessarias, cenarios esperado/nao esperado) para homologacao consistente da regra de seguranca.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, Pydantic v2, pytest, pytest-cov, httpx  
**Storage**: N/A (ajuste de documentacao OpenAPI e contratos de API)  
**Testing**: pytest (unit + integration + mocks) com cobertura minima de 80%  
**Target Platform**: Linux container (runtime), desenvolvimento local em Windows/Mac/Linux  
**Project Type**: web-service (API interna)  
**Performance Goals**: acessibilidade da documentacao em ate 2s no ambiente local e execucao completa do roteiro Swagger em ate 5 minutos por pessoa  
**Constraints**: seguranca por segredo interno obrigatoria; sem hardcode de segredos; complexidade ciclomatica < 5 por funcao; sem regressao de middleware  
**Scale/Scope**: 1 servico FastAPI existente, ajustes em metadados OpenAPI, schemas e validacao de fluxo protegido na interface Swagger

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Verificacao | Resultado |
|-----------|-------------|-----------|
| I. Clean Architecture | Ajustes limitados a camada de apresentacao para docs/rotas e schemas, sem violar fronteiras de dominio/aplicacao | PASS |
| II. Cobertura >= 80% | Plano inclui testes unitarios para schema/docs e integracao para fluxo protegido com/sem cabecalho | PASS |
| III. SOLID + baixa complexidade | Configuracoes de OpenAPI encapsuladas com responsabilidades claras, sem funcoes grandes | PASS |
| IV. Security First | `X-Internal-Secret` permanece obrigatorio em rotas protegidas e sem exposicao de detalhes em erro | PASS |
| V. Abstracao + DI | Nao introduz acoplamento adicional; middleware/dependencias existentes preservados | PASS |
| Future-proofing | Metadados e seguranca no OpenAPI estruturados para evolucao sem lock-in | PASS |

Sem violacoes. Tabela de complexidade nao se aplica.

## Project Structure

### Documentation (this feature)

```text
specs/004-swagger-security-testing/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── swagger-security-api.md
├── checklists/
│   └── requirements.md
└── tasks.md                        # gerado depois por /speckit.tasks
```

### Source Code (repository root)

```text
presentation/
├── main.py                         # metadados FastAPI e configuracao de OpenAPI tags
├── routes/
│   ├── chat_routes.py              # tags e documentacao de endpoints protegidos
│   └── consult_routes.py           # tags e documentacao de endpoints protegidos
└── schemas.py                      # descricoes de campos (Field(description=...))

infra/
└── security/
    └── secret_validator.py         # comportamento de validacao reaproveitado nos testes

tests/
├── unit/
│   ├── test_chat_schemas.py
│   ├── test_chat_response_schema.py
│   └── test_security_validator.py
└── integration/
    ├── test_chat_security_flow.py
    ├── test_consult_contract_validation.py
    └── test_chat_endpoint.py
```

**Structure Decision**: manter a estrutura atual em camadas e concentrar mudancas em `presentation/` (documentacao e tags), com cobertura de regressao em `tests/unit` e `tests/integration` para validar o comportamento de seguranca exposto no Swagger.

## Phase 0: Outline & Research

Concluida. Ver [research.md](./research.md). Decisoes tecnicas cobrem: esquema de seguranca por cabecalho no Swagger, organizacao de tags, nivel de detalhamento dos schemas e estrategia de testes manuais e automatizados para validacao de autorizacao.

## Phase 1: Design & Contracts

Concluida. Artefatos gerados:

- [data-model.md](./data-model.md)
- [contracts/swagger-security-api.md](./contracts/swagger-security-api.md)
- [quickstart.md](./quickstart.md)
- Atualizacao de contexto em `.github/copilot-instructions.md` para apontar para a feature 004

### Re-avaliacao da Constitution Check (pos-design)

Apos detalhar entidades, contrato e roteiro de validacao, todas as gates permanecem **PASS**. O plano preserva segregacao por camada, politica de seguranca e estrategia de testes com cobertura minima obrigatoria.

## Complexity Tracking

> Sem violacoes da constituicao. Tabela nao preenchida.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | (n/a) | (n/a) |
