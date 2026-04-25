# Quickstart: Cache Semantico e Resposta em Audio (EDI-26)

**Feature**: 003-semantic-cache-tts  
**Branch**: `003-before-specify`

## Pre-requisitos

- Python 3.11+
- Repositorio em `c:\projects\interasisai-engine`
- Ambiente virtual `.venv` ativo
- `.env` com `X_INTERNAL_SECRET` definido

Variaveis recomendadas para esta feature:

```env
X_INTERNAL_SECRET=<segredo-interno>
SEMANTIC_MATCH_THRESHOLD=0.85
STT_MIN_CONFIDENCE=0.70
```

## 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 2. Subir a API

```bash
uvicorn presentation.main:app --reload --port 8000
```

## 3. Validacoes rapidas de contrato

### 3.1 Requisicao sem segredo (deve falhar)

```bash
curl -i -X POST http://localhost:8000/api/v1/chat/process \
  -F "text=Qual o status da minha solicitacao?"
```

Esperado: `HTTP/1.1 403 Forbidden`.

### 3.2 Requisicao texto (primeira chamada, tende a miss)

```bash
curl -i -X POST http://localhost:8000/api/v1/chat/process \
  -H "X-Internal-Secret: <segredo>" \
  -F "text=Quais sao meus horarios de atendimento?"
```

Esperado: `200 OK` com `source=cache_miss`, `message.text` preenchido e `message.audio` acessivel.

### 3.3 Requisicao texto semantica equivalente (tende a hit)

```bash
curl -i -X POST http://localhost:8000/api/v1/chat/process \
  -H "X-Internal-Secret: <segredo>" \
  -F "text=Quero saber meus horarios de atendimento"
```

Esperado: `200 OK` com `source=cache_hit` e latencia menor que a chamada anterior.

### 3.4 Requisicao com audio

```bash
curl -i -X POST http://localhost:8000/api/v1/chat/process \
  -H "X-Internal-Secret: <segredo>" \
  -F "audio=@./sample.wav;type=audio/wav"
```

Esperado: `200 OK` com `transcription` preenchida e retorno multimodal.

### 3.5 Requisicao vazia (validacao)

```bash
curl -i -X POST http://localhost:8000/api/v1/chat/process \
  -H "X-Internal-Secret: <segredo>"
```

Esperado: `422 Unprocessable Entity` por ausencia de `text` e `audio`.

## 4. Rodar testes

```bash
pytest --cov=. --cov-report=term-missing
```

Esperado:
- Todos os testes passando
- Cobertura total >= 80%
- Casos contemplando: seguranca, cache hit/miss, STT/TTS, consistencia de contrato

## 5. Checklist de prontidao

- [ ] Seguranca por `X-Internal-Secret` ativa para o endpoint
- [ ] Fluxo de texto e audio funcionando no mesmo contrato
- [ ] `source` diferencia corretamente `cache_hit` e `cache_miss`
- [ ] `transcription` presente quando entrada for audio
- [ ] Fallback de audio nao quebra resposta textual
- [ ] Logs operacionais sem dados sensiveis
