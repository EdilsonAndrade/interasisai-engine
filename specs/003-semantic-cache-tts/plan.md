# Implementation Plan: Cache Semantico e Resposta em Audio

**Branch**: `003-before-specify` | **Date**: 2026-04-25 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/003-semantic-cache-tts/spec.md`  
**Related Issue**: EDI-26

## Summary

Entregar um fluxo multimodal para o endpoint interno de chat que: (1) aceita entrada por texto ou audio; (2) aplica transcricao para audio; (3) executa busca semantica para decidir entre cache hit e cache miss; (4) retorna texto e audio no mesmo contrato; (5) registra eventos operacionais de reutilizacao, nova geracao e falhas controladas. A implementacao mantera o padrao Clean Architecture existente e adicionara abstracoes para STT, TTS e indexacao semantica sem acoplamento a provider especifico.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, Pydantic v2, python-multipart, langchain, langchain-core, langchain-community, langchain-google-genai, pytest, pytest-cov, pytest-asyncio, pytest-mock, httpx  
**Storage**: Camada de cache semantico abstrata (implementacao inicial em memoria com possibilidade de evolucao para persistencia externa)  
**Testing**: pytest (unit + integration + mocks), cobertura minima de 80%  
**Target Platform**: Linux container (homologacao/producao); Windows/Mac/Linux (desenvolvimento local)  
**Project Type**: web-service (API interna)  
**Performance Goals**: cache hit com latencia percebida ao menos 40% menor que cache miss; 95% de respostas validas com texto+audio no payload  
**Constraints**: seguranca por `X-Internal-Secret` obrigatoria; nao expor detalhes sensiveis em erros; complexidade ciclomatica < 5 por funcao; contrato consistente para hit/miss  
**Scale/Scope**: escopo inicial de 1 endpoint existente com expansao de caso de uso, servicos semanticos e pipeline STT/TTS para processamento de uma solicitacao por vez

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Verificacao | Resultado |
|-----------|-------------|-----------|
| I. Clean Architecture | Casos de uso em `application/services`, interfaces em `domain/interfaces`, integracoes STT/TTS/cache em `infra/`, rotas/schemas em `presentation/` | PASS |
| II. Cobertura de testes >= 80% | Plano de testes inclui unitarios (cache matcher, orchestrator, validacao) e integracao (fluxo endpoint hit/miss/falhas) | PASS |
| III. SOLID + complexidade < 5 | Fluxo dividido em servicos pequenos (transcricao, matching, geracao, serializacao) com injecao de dependencia | PASS |
| IV. Security First | Middleware de segredo permanece gate global antes de qualquer etapa semantica; respostas de erro sem vazamento | PASS |
| V. Abstracao + DI | Providers de embedding/STT/TTS e repositorio de cache dependem de interfaces e factories injetaveis | PASS |
| Future-proofing de framework | Integracoes especificas permanecem em `infra/` e nao vazam para dominio/aplicacao | PASS |

Sem violacoes. Tabela de complexidade nao se aplica.

## Project Structure

### Documentation (this feature)

```text
specs/003-semantic-cache-tts/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── chat-process-api.md
├── checklists/
│   └── requirements.md
└── tasks.md                        # gerado depois por /speckit.tasks
```

### Source Code (repository root)

```text
application/
├── dto/
│   ├── request.py                  # estender contratos de entrada multimodal
│   └── response.py                 # incluir saida com texto+audio+metadados de cache
└── services/
    ├── langchain_chat_use_case.py  # orquestracao principal do fluxo
    └── semantic_cache_service.py    # NOVO: matching semantico e decisao hit/miss

domain/
├── interfaces.py                   # interfaces para SemanticCacheRepository, STTProvider, TTSProvider, EmbeddingProvider
├── models.py                       # modelos de RegistroSemantico e RespostaMultimodal
└── exceptions.py                   # erros de transcricao, audio e fallback controlado

infra/
├── llm/
│   └── provider_stub.py            # reutilizado para geracao de resposta textual quando miss
├── speech/
│   ├── stt_provider_stub.py         # NOVO: transcricao simulada
│   └── tts_provider_stub.py         # NOVO: geracao de audio simulada
├── semantic/
│   ├── embedding_provider_stub.py   # NOVO: vetor semantico simulado
│   └── in_memory_semantic_cache.py  # NOVO: armazenamento/retrieval semantico
└── logging/logger.py               # eventos operacionais (cache_hit, cache_miss, falhas)

presentation/
├── routes/chat_routes.py           # ampliar endpoint para retorno multimodal e transcricao
├── schemas.py                      # schema de resposta estendida
└── middleware/security_middleware.py # gatekeeper existente (sem regressao)

tests/
├── unit/
│   ├── test_semantic_cache_service.py
│   ├── test_speech_pipeline.py
│   └── test_chat_response_schema.py
└── integration/
    ├── test_chat_endpoint.py
    ├── test_chat_cache_flow.py
    └── test_chat_audio_flow.py
```

**Structure Decision**: manter a estrutura Clean Architecture ja consolidada no repositorio (sem prefixo `src/`) e evoluir o endpoint existente em `presentation/routes/chat_routes.py` com novos servicos especializados para cache semantico e pipeline de audio.

## Phase 0: Outline & Research

Concluida. Ver [research.md](./research.md). Todos os pontos de NEEDS CLARIFICATION foram resolvidos, incluindo estrategia de similaridade semantica, representacao de audio no contrato, fallback de falhas de TTS/STT e padrao de observabilidade para cache hit/miss.

## Phase 1: Design & Contracts

Concluida. Artefatos gerados:

- [data-model.md](./data-model.md)
- [contracts/chat-process-api.md](./contracts/chat-process-api.md)
- [quickstart.md](./quickstart.md)
- Atualizacao do contexto do agente em `.github/copilot-instructions.md` para apontar para a feature 003

### Re-avaliacao da Constitution Check (pos-design)

Apos o detalhamento dos contratos e entidades, todas as gates permanecem **PASS**. O desenho preserva separacao por camadas, injecao de dependencia para provedores externos e estrategia de testes com cobertura minima obrigatoria.

## Complexity Tracking

> Sem violacoes da constituicao. Tabela nao preenchida.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | (n/a) | (n/a) |
