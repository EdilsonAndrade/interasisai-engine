# Quickstart: Recepcao Segura de Input de Chat (EDI-24)

**Feature**: 002-secure-chat-intake  
**Branch**: `002-init-ai-engine-security`

## Pre-requisitos

- Python 3.11+
- Repositorio clonado em `c:\projects\interasisai-engine`
- Ambiente virtual `.venv` criado e ativado
- Arquivo `.env` configurado com `X_INTERNAL_SECRET` definido

## 1. Instalar dependencias

Adicione (caso ainda nao estejam) ao `requirements.txt`:

```text
langchain
langchain-core
langchain-community
langchain-google-genai
```

E rode:

```bash
pip install -r requirements.txt
```

## 2. Variavel de ambiente

`.env` deve conter ao menos:

```env
X_INTERNAL_SECRET=<segredo-de-desenvolvimento>
```

## 3. Subir o servidor localmente

```bash
uvicorn presentation.main:app --reload --port 8000
```

## 4. Validar o endpoint

### 4.1 Acesso negado (sem segredo)

```bash
curl -i -X POST http://localhost:8000/api/v1/chat/process \
  -F "text=Ola"
```

Esperado: `HTTP/1.1 403 Forbidden`.

### 4.2 Acesso autorizado com texto

```bash
curl -i -X POST http://localhost:8000/api/v1/chat/process \
  -H "X-Internal-Secret: <segredo>" \
  -F "text=Ola, motor!"
```

Esperado: `HTTP/1.1 200 OK` com corpo:

```json
{
  "status": "success",
  "agent_reply": "Conexao segura estabelecida. Motor LangChain pronto.",
  "received": { "has_text": true, "has_audio": false, "audio_filename": null, "session_id": null }
}
```

### 4.3 Acesso autorizado com audio

```bash
curl -i -X POST http://localhost:8000/api/v1/chat/process \
  -H "X-Internal-Secret: <segredo>" \
  -F "audio=@./sample.wav;type=audio/wav"
```

Esperado: `200 OK` com `has_audio: true` e `audio_filename` preenchido.

### 4.4 Validacao de entrada vazia

```bash
curl -i -X POST http://localhost:8000/api/v1/chat/process \
  -H "X-Internal-Secret: <segredo>"
```

Esperado: `422 Unprocessable Entity` informando que ao menos um entre `text` e `audio` e obrigatorio.

## 5. Rodar testes

```bash
pytest --cov=. --cov-report=term-missing
```

Esperado:
- Todos os testes passando.
- Cobertura total >= 80%.
- Casos cobertos: import LangChain, middleware com/sem segredo, endpoint com texto, com audio, sem conteudo, com segredo invalido.

## 6. Checklist de prontidao

- [ ] `import langchain` funciona em `main.py` sem erro.
- [ ] Endpoint `/api/v1/chat/process` retorna 403 sem segredo.
- [ ] Endpoint aceita `UploadFile` e devolve mock JSON estruturado.
- [ ] Estrutura de pastas Clean Architecture mantida (`domain/`, `application/`, `infra/`, `presentation/`).
- [ ] Cobertura de testes >= 80%.
