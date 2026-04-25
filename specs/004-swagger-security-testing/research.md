# Research: Swagger Security Header e Guia de Teste (EDI-29)

**Feature**: 004-swagger-security-testing  
**Date**: 2026-04-25  
**Status**: Complete (Phase 0)

## Decisao 1 - Expor autenticacao por API key header no Swagger

- **Decisao**: Configurar esquema de seguranca no OpenAPI para aceitar `X-Internal-Secret` via fluxo de autorizacao da UI.
- **Rationale**: Permite validar endpoints protegidos diretamente na interface interativa, alinhado ao criterio de aceite da EDI-29.
- **Alternativas consideradas**:
  - Informar cabecalho manual por endpoint em cada teste: maior risco de erro humano.
  - Nao expor autenticacao no Swagger: inviabiliza homologacao guiada pela UI.

## Decisao 2 - Organizar documentacao por tags funcionais

- **Decisao**: Categorizar endpoints em grupos funcionais consistentes (ex.: Chat, Consult, Internal).
- **Rationale**: Aumenta descobribilidade de rotas e reduz tempo de onboarding.
- **Alternativas consideradas**:
  - Lista unica sem agrupamento: pior navegacao para times de QA e integracao.

## Decisao 3 - Definir metadados claros na API

- **Decisao**: Publicar nome, descricao e versao da API na documentacao interativa.
- **Rationale**: Clarifica contexto de uso e evita ambiguidades entre ambientes/versoes.
- **Alternativas consideradas**:
  - Usar metadados default: baixa clareza para consumidores internos.

## Decisao 4 - Reforcar descricoes dos schemas

- **Decisao**: Garantir que campos de request/response relevantes tenham descricoes legiveis para consumo no Swagger.
- **Rationale**: Facilita entendimento do contrato sem depender de leitura de codigo.
- **Alternativas consideradas**:
  - Manter schemas sem descricao: aumenta chance de uso incorreto dos endpoints.

## Decisao 5 - Roteiro padrao de teste manual via Swagger

- **Decisao**: Fornecer quickstart com passo a passo unico cobrindo pre-requisitos, autorizacao, chamada protegida e verificacao de cenarios com chave valida/invalida/ausente.
- **Rationale**: Padroniza homologacao e garante repetibilidade de resultados.
- **Alternativas consideradas**:
  - Testes ad-hoc por pessoa: baixa consistencia e dificuldade de auditoria.

## Decisao 6 - Estrategia de testes automatizados de suporte

- **Decisao**: Cobrir com testes de integracao o comportamento de seguranca em endpoints protegidos e manter testes unitarios para validadores/schemas.
- **Rationale**: Evita regressao da regra de segredo interno ao ajustar documentacao OpenAPI.
- **Alternativas consideradas**:
  - Apenas validacao manual: insuficiente para prevenir regressao continua.

## Resumo de NEEDS CLARIFICATION

Nenhum item pendente. A especificacao define escopo, fluxo esperado e criterios mensuraveis para documentacao e testes via Swagger.
