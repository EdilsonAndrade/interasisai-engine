# Research: Cache Semantico e Resposta em Audio (EDI-26)

**Feature**: 003-semantic-cache-tts  
**Date**: 2026-04-25  
**Status**: Complete (Phase 0)

## Decisao 1 - Estrategia de matching semantico

- **Decisao**: Usar comparacao vetorial com cosseno e limiar configuravel (`SEMANTIC_MATCH_THRESHOLD`, default 0.85).
- **Rationale**: Mantem a regra de negocio explicita (FR-002) e permite calibracao progressiva sem alterar o fluxo da API.
- **Alternativas consideradas**:
  - Distancia euclidiana pura: menos interpretavel para embeddings normalizados.
  - Matching lexical por palavras-chave: nao cobre equivalencia semantica em parafrases.

## Decisao 2 - Persistencia do cache semantico na fase inicial

- **Decisao**: Introduzir `SemanticCacheRepository` como interface no dominio com implementacao inicial em memoria no `infra/semantic/`.
- **Rationale**: Cumpre Clean Architecture e prepara evolucao para Redis/PostgreSQL sem alterar use cases.
- **Alternativas consideradas**:
  - Persistencia direta em rota/servico de aplicacao: viola inversao de dependencia.
  - Ja iniciar com banco externo: aumenta complexidade para a primeira entrega da feature.

## Decisao 3 - Pipeline de entrada multimodal

- **Decisao**: Tratar `text` e `audio` no mesmo endpoint; quando `audio` existir, executar STT antes do matching; quando ambos existirem, priorizar `text` como fonte principal e registrar transcricao como metadado.
- **Rationale**: Preserva contrato unico (FR-006/FR-007/FR-012) e reduz ambiguidade de processamento.
- **Alternativas consideradas**:
  - Endpoints separados para texto e audio: aumenta superficie de API e duplicacao de logica.
  - Priorizar sempre audio quando presente: pode degradar qualidade quando texto ja foi validado no cliente.

## Decisao 4 - Contrato de audio na resposta

- **Decisao**: Retornar audio em objeto estruturado (`mime_type`, `encoding`, `content`) com `encoding=base64` para previsibilidade imediata.
- **Rationale**: Garante acessibilidade imediata no cliente, sem dependencia de armazenamento externo temporario nesta fase.
- **Alternativas consideradas**:
  - URL assinada temporaria: reduz payload, mas exige storage e ciclo de expiracao fora do escopo.
  - Audio opcional em endpoint separado: quebra requisito de retorno multimodal unico.

## Decisao 5 - Tratamento de falhas em STT/TTS

- **Decisao**: Em falha de STT, responder erro controlado com mensagem orientativa ao usuario. Em falha de TTS apos texto valido, retornar texto com indicador de `audio_unavailable` mantendo contrato consistente.
- **Rationale**: Atende FR-011 e edge cases sem quebrar usabilidade.
- **Alternativas consideradas**:
  - Falhar toda requisicao em qualquer erro de audio: experiencia pior para usuario e baixa resiliencia.
  - Silenciar erro de STT: mascara problema operacional.

## Decisao 6 - Observabilidade operacional

- **Decisao**: Registrar eventos estruturados com `event_type` (`cache_hit`, `cache_miss`, `stt_failed`, `tts_failed`), `request_id`, `latency_ms`, sem payload sensivel.
- **Rationale**: Atende FR-010 e facilita monitoramento dos criterios SC-001 e SC-004.
- **Alternativas consideradas**:
  - Logs livres sem padrao: dificulta metricas e auditoria.

## Decisao 7 - Integracao com LangChain sem lock-in

- **Decisao**: Manter uso de LangChain restrito a adaptadores de `infra/` e manter interfaces de negocio em `domain/interfaces.py`.
- **Rationale**: Cumpre constituicao (no framework lock-in) e simplifica troca futura de provider.
- **Alternativas consideradas**:
  - Uso direto de classes LangChain na camada de aplicacao: acoplamento elevado.

## Decisao 8 - Estrategia de testes

- **Decisao**:
  - Unit: similaridade e threshold, validadores de entrada multimodal, orquestracao hit/miss, serializacao de audio.
  - Integration: endpoint com segredo valido/invalido, hit com audio reutilizado, miss com nova geracao, falhas STT/TTS.
  - Contrato: validacao de consistencia de payload entre hit e miss.
- **Rationale**: Mantem cobertura >= 80% com foco em regressao de comportamento e seguranca.
- **Alternativas consideradas**:
  - Apenas testes e2e: custo alto e baixa capacidade de diagnostico.

## Resumo de NEEDS CLARIFICATION

Nenhum item pendente. Todos os pontos do contexto tecnico e requisitos foram resolvidos nesta pesquisa.
