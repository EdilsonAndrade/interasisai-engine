# Research: Recepcao Segura de Input de Chat (EDI-24)

**Feature**: 002-secure-chat-intake  
**Date**: 2026-04-25  
**Status**: Complete (Phase 0)

## Decisao 1 - Framework de orquestracao de IA

- **Decisao**: Adotar LangChain como framework principal (`langchain`, `langchain-core`, `langchain-community`, `langchain-google-genai`).
- **Rationale**: EDI-24 exige preparacao do ecossistema LangChain para gerenciar contexto, orquestrar LLMs e extrair dados estruturados. Pacotes core/community oferecem abstracoes de chains, memoria e prompts; `langchain-google-genai` antecipa o provider Gemini previsto para o produto.
- **Alternativas consideradas**:
  - LlamaIndex: forte em RAG, porem menor cobertura de orquestracao multi-agente; rejeitado pela diretriz da issue.
  - Implementacao manual com chamadas diretas ao SDK do provedor: aumenta acoplamento e contraria o objetivo de neutralidade de provider definido na constituicao.

## Decisao 2 - Mecanismo de Gatekeeper de Seguranca

- **Decisao**: Reaproveitar a infraestrutura existente (`presentation/middleware/security_middleware.py` + `infra/security/secret_loader.py`) e estender a aplicacao para cobrir o novo router de chat.
- **Rationale**: A camada de seguranca da feature 001 ja valida `X-Internal-Secret` no nivel de middleware ASGI; reutiliza-la mantem coerencia, evita duplicacao e cumpre o principio DRY. A constituicao exige validacao de segredo em toda requisicao via middleware.
- **Alternativas consideradas**:
  - Implementar `Depends()` por rota: viola DRY e exige replicacao em cada endpoint novo.
  - Reescrever middleware: rejeitado por gerar retrabalho sem valor adicional.

## Decisao 3 - Contrato de entrada multimodal (texto + audio)

- **Decisao**: Endpoint `POST /api/v1/chat/process` aceita `multipart/form-data` com campos opcionais `text` (string) e `audio` (UploadFile). Pelo menos um dos dois deve estar presente.
- **Rationale**: EDI-24 exige `UploadFile` para audio vindo do BFF; form-data permite combinar texto e arquivo na mesma chamada e e o formato natural de FastAPI para upload. Validacao de "ao menos um" garante FR-005.
- **Alternativas consideradas**:
  - JSON puro com base64 do audio: simplifica parsing mas degrada performance e tamanho de payload.
  - Endpoints separados para texto e audio: aumenta superficie de API e contraria o ponto unico definido na issue.

## Decisao 4 - Caso de uso `LangChainChatUseCase` simulado

- **Decisao**: Criar em `application/services/langchain_chat_use_case.py` uma classe que valida entrada e retorna payload simulado `{"status": "success", "agent_reply": "Conexao segura estabelecida. Motor LangChain pronto."}`. Sem chamadas reais a LLM nesta fase.
- **Rationale**: A issue determina retorno mock para nao consumir tokens; manter a classe ja na camada de aplicacao prepara o ponto de extensao para chains reais sem refactor (FR-007, SC-005).
- **Alternativas consideradas**:
  - Colocar o mock direto no router: viola Clean Architecture (logica de aplicacao em presentation).
  - Implementar chain real com modelo local: fora de escopo da issue e consome esforco desnecessario.

## Decisao 5 - Validacao de presenca de conteudo

- **Decisao**: O caso de uso rejeita explicitamente requisicoes sem texto e sem audio com erro de validacao 422 e mensagem clara.
- **Rationale**: Atende FR-005 e SC-004; protege a futura chain de receber entrada vazia.
- **Alternativas consideradas**:
  - Aceitar entrada vazia e responder mensagem padrao: mascara erro do cliente e degrada observabilidade.

## Decisao 6 - Estrutura de pastas

- **Decisao**: Manter a estrutura existente (`domain/`, `application/`, `infra/`, `presentation/` na raiz). Criar `presentation/routes/chat_routes.py` em vez de `src/presentation/routers/` mencionado textualmente na issue.
- **Rationale**: A constituicao e a feature 001 ja consolidaram a convencao de pastas; nao introduzir prefixo `src/` mantem coerencia. A intencao da issue (Clean Architecture) e respeitada.
- **Alternativas consideradas**:
  - Migrar para `src/`: mudanca estrutural ampla, fora de escopo desta feature.

## Decisao 7 - Logging de tentativas negadas

- **Decisao**: Reutilizar `infra/logging/logger.py` para registrar warnings em cada negacao do middleware, incluindo motivo (`missing_header`, `invalid_secret`).
- **Rationale**: Atende FR-009 sem expor detalhes ao cliente (resposta 403 generica), preservando rastreabilidade interna.
- **Alternativas consideradas**:
  - Logar apenas em nivel debug: insuficiente para auditoria de seguranca.

## Decisao 8 - Estrategia de testes

- **Decisao**:
  - Unit: validar `LangChainChatUseCase` (entrada vazia, texto, audio, ambos), schemas Pydantic, e logging de negacao.
  - Integration: validar fluxo completo do endpoint (sem segredo, com segredo invalido, com segredo valido + texto, com segredo valido + audio, autorizado sem conteudo).
  - Importacao do LangChain: teste de smoke garantindo que `import langchain` e pacotes acessorios funcionam.
- **Rationale**: Cobre criterios de aceite da issue, mantem cobertura >=80% e atende a constituicao.
- **Alternativas consideradas**:
  - Testar somente integracao: insuficiente para isolar logica de validacao.

## Resumo de NEEDS CLARIFICATION

Nenhum item NEEDS CLARIFICATION pendente. Todos os pontos da especificacao foram resolvidos com base na issue EDI-24 e na constituicao do projeto.
