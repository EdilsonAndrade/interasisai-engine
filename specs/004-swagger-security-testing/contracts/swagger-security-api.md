# API Contract: Swagger Security & Documentation Coverage

**Feature**: 004-swagger-security-testing (EDI-29)  
**Status**: Phase 1 contract

## Visao Geral

Este contrato descreve os comportamentos esperados para validacao de endpoints protegidos via Swagger, cobrindo metadados da documentacao, esquema de seguranca por cabecalho e cenarios de autorizacao.

## Documentacao Interativa

- URL esperada: `/docs`
- Metadados obrigatorios:
  - Titulo da API
  - Descricao da API
  - Versao da API
- Organizacao obrigatoria: endpoints agrupados por categorias funcionais (tags)

## Esquema de Seguranca no Swagger

| Campo | Valor esperado |
|-------|----------------|
| Tipo de seguranca | API key em header |
| Header | `X-Internal-Secret` |
| Disponivel em | Fluxo "Authorize" do Swagger |
| Aplicacao | Endpoints protegidos |

## Endpoint de referencia para validacao

```http
POST /api/v1/chat/process
```

## Cenarios de validacao via Swagger

### Cenario A - Sem chave

**Pre-condicao**: Nao informar credencial no fluxo de autorizacao.  
**Acao**: Executar endpoint protegido no Swagger.  
**Resultado esperado**: Bloqueio de acesso (ex.: 403).

### Cenario B - Chave invalida

**Pre-condicao**: Informar valor invalido em `X-Internal-Secret`.  
**Acao**: Executar endpoint protegido no Swagger.  
**Resultado esperado**: Bloqueio de acesso (ex.: 403).

### Cenario C - Chave valida

**Pre-condicao**: Informar valor valido em `X-Internal-Secret`.  
**Acao**: Executar endpoint protegido no Swagger.  
**Resultado esperado**: Sucesso funcional (ex.: 200), sem gatilho de bloqueio do gatekeeper.

## Regras de conformidade

- O comportamento de seguranca no Swagger deve ser consistente com middleware de autenticacao interna.
- Erros de autorizacao nao devem expor detalhes sensiveis sobre segredo.
- O contrato de entrada/saida dos endpoints deve manter descricoes claras para uso no Swagger.

## Evidencias minimas para homologacao

- Print ou registro textual do Authorize com header configurado.
- Status code e resposta dos tres cenarios.
- Identificacao do ambiente em que os testes foram executados.
