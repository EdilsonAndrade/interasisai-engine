# Data Model: Swagger Security Testing Guide (EDI-29)

**Feature**: 004-swagger-security-testing  
**Date**: 2026-04-25  
**Status**: Phase 1 output

## Visao Geral

Esta feature modela os elementos necessarios para expor e validar, via Swagger, a seguranca por cabecalho interno em endpoints protegidos, com foco em metadados de documentacao, credencial de seguranca e roteiro de homologacao.

## Entidades

### 1. ApiDocumentationProfile

Representa a configuracao publica da documentacao interativa.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `title` | string | Sim | Nome exibido da API |
| `description` | string | Sim | Resumo de objetivo e escopo da API |
| `version` | string | Sim | Versao funcional publicada |
| `tags` | list[ApiTag] | Sim | Categorias de organizacao de endpoints |
| `docs_url` | string | Sim | URL da interface Swagger |

### 2. ApiTag

Representa uma categoria funcional de endpoints.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `name` | string | Sim | Nome da categoria (ex.: Chat, Consult, Internal) |
| `description` | string | Sim | Contexto de uso da categoria |

### 3. InternalSecurityCredential

Representa credencial necessaria para acesso a endpoints protegidos.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `header_name` | string | Sim | Nome do cabecalho de seguranca (`X-Internal-Secret`) |
| `value` | string | Sim | Valor informado para autorizacao |
| `environment` | enum (`local`, `hml`, `prod`) | Sim | Ambiente ao qual a chave pertence |
| `is_valid` | bool | Sim | Resultado esperado de validacao no ambiente |

### 4. SwaggerTestPrerequisite

Representa itens minimos para iniciar o teste manual.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `api_base_url` | string | Sim | URL base da API |
| `docs_url` | string | Sim | URL do Swagger |
| `protected_endpoint` | string | Sim | Endpoint de referencia para validacao |
| `internal_secret_available` | bool | Sim | Indica se a chave esta disponivel para o teste |

### 5. SwaggerManualTestCase

Representa cada passo do roteiro de teste manual.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `step_number` | int | Sim | Ordem do passo |
| `action` | string | Sim | Acao a ser executada na UI |
| `input` | string \| null | Nao | Dado informado no passo |
| `expected_result` | string | Sim | Resultado esperado |
| `evidence_required` | string \| null | Nao | Evidencia que deve ser registrada |

### 6. SwaggerExecutionResult

Representa resultado observado em uma execucao do roteiro.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `scenario` | enum (`without_key`, `invalid_key`, `valid_key`) | Sim | Cenario executado |
| `status_code` | int | Sim | Codigo retornado na chamada |
| `outcome` | enum (`blocked`, `authorized`) | Sim | Comportamento observado |
| `notes` | string \| null | Nao | Observacoes de homologacao |

## Relacionamentos

- `ApiDocumentationProfile` -> `ApiTag`: 1:N (uma documentacao contem varias tags).
- `SwaggerTestPrerequisite` -> `SwaggerManualTestCase`: 1:N (um conjunto de pre-requisitos habilita varios passos).
- `SwaggerManualTestCase` -> `SwaggerExecutionResult`: 1:1 por cenario validado.
- `InternalSecurityCredential` participa dos cenarios `invalid_key` e `valid_key` nos resultados.

## Regras de Validacao

- `header_name` deve permanecer fixo como `X-Internal-Secret` para interoperabilidade com middleware atual.
- O cenario `without_key` deve resultar em `outcome=blocked`.
- O cenario `invalid_key` deve resultar em `outcome=blocked`.
- O cenario `valid_key` deve resultar em `outcome=authorized` no endpoint protegido alvo.
- Toda execucao deve registrar ao menos status e evidencia minima (codigo de resposta e trecho da resposta).
