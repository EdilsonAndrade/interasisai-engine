# Data Model: FastAPI AI Engine

**Date**: 2026-04-24  
**Feature**: 001-ai-engine-initialization  
**Layer**: Domain (business logic entities)

## Entity Definitions

### ConsultRequest

**Purpose**: Represents a consultation query from the NestJS server to the AI engine

**Location**: `domain/models.py`

**Attributes**:

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `message` | string | 1-2000 chars, required | The consultation query/prompt for the LLM |

**Validation Rules**:
- Message MUST NOT be empty (min_length=1)
- Message MUST NOT exceed 2000 characters (max_length=2000)
- Message validation happens in Pydantic schema layer

**Relationships**: None (MVP - no persistence)

**State Transitions**: None (stateless)

**Serialization**:
- From JSON: `{"message": "user query"}`
- To JSON: Same format (Pydantic serialization)

**Future Expansion** (Phase 2+):
- `model_name: str` - LLM model selection (e.g., "gpt-4", "claude-3")
- `temperature: float` - LLM parameter (0.0-1.0)
- `max_tokens: int` - Response length limit
- `chain_type: str` - Langchain chain selection
- `context_ids: List[str]` - Vector store references
- `tools: List[str]` - Available tools for agent

---

### ConsultResponse

**Purpose**: Represents the response from the AI engine back to the NestJS server

**Location**: `domain/models.py`

**Attributes**:

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `message` | string | required | Echoed request message (MVP); future: LLM response |
| `timestamp` | datetime | ISO8601, UTC | Server response timestamp |

**Validation Rules**:
- `message` MUST be non-empty
- `timestamp` MUST be set at response generation time
- `timestamp` MUST be in UTC timezone

**Relationships**: None (MVP - no persistence)

**State Transitions**: None (stateless - request → response → discard)

**Serialization**:
- To JSON: `{"message": "...", "timestamp": "2026-04-24T12:34:56.789Z"}`

**Future Expansion** (Phase 2+):
- `llm_response: str` - Actual LLM output
- `token_usage: Dict[str, int]` - {"prompt_tokens": X, "completion_tokens": Y, "total": Z}
- `execution_trace: List[Dict]` - Chain execution steps
- `source_references: List[str]` - Retrieved document IDs
- `error: Optional[str]` - Error message if processing failed

---

### SecurityContext

**Purpose**: Represents the validated security context for authorized requests

**Location**: `domain/models.py`

**Attributes**:

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `is_authorized` | boolean | required | Whether X-Internal-Secret matched |
| `source` | string | enum: ["internal", "unknown"] | Request source classification |

**Validation Rules**:
- `is_authorized` MUST be set by middleware before routing
- `source` MUST be one of defined enum values

**Usage**:
- Set by middleware in `request.state.security_context`
- Accessible in route handlers via `request.state.security_context`
- Routes MUST check `is_authorized` (defense in depth, even though middleware already rejected unauthorized)

**Relationships**: None (metadata only)

**State Transitions**: None (immutable during request)

**Future Expansion** (Phase 2+):
- `origin_ip: str` - Client IP address
- `request_id: str` - UUID for tracing
- `rate_limit_key: str` - For future rate limiting
- `permissions: List[str]` - Fine-grained access control

---

### Config

**Purpose**: Application configuration loaded from environment variables

**Location**: `infra/config/settings.py`

**Attributes**:

| Attribute | Env Var | Type | Required | Default | Description |
|-----------|---------|------|----------|---------|-------------|
| `x_internal_secret` | `X_INTERNAL_SECRET` | string | YES | None | Secret for middleware validation |
| `log_level` | `LOG_LEVEL` | string | NO | "INFO" | Python logging level |
| `app_name` | `APP_NAME` | string | NO | "InterasisAI-Engine" | Application name |
| `environment` | `ENVIRONMENT` | string | NO | "development" | Deployment environment |

**Validation Rules**:
- `x_internal_secret` MUST NOT be empty
- `x_internal_secret` SHOULD be ≥ 32 characters (in docs)
- `log_level` MUST be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL
- `environment` MUST be one of: development, testing, production

**Loading Strategy**:
```python
from dotenv import load_dotenv
import os

load_dotenv()  # Load from .env file
x_internal_secret = os.getenv("X_INTERNAL_SECRET")
if not x_internal_secret:
    raise ValueError("X_INTERNAL_SECRET environment variable is required")
```

**Security Considerations**:
- Never log the actual secret value
- Never include in error messages
- Only accessible in `infra/` layer
- Injected into middleware and validators via dependency injection

**Future Expansion** (Phase 2+):
- `llm_provider: str` - (e.g., "openai", "anthropic", "local")
- `llm_api_key: str` - LLM provider secret
- `vector_db_url: str` - Langchain vector store connection
- `database_url: str` - PostgreSQL/MongoDB connection
- `cache_ttl: int` - Cache time-to-live in seconds

---

## Entity Relationships Diagram

```
┌──────────────────┐
│  ConsultRequest  │
│                  │
│ - message: str   │
└────────┬─────────┘
         │ 1:1
         │ processed by
         │
┌────────v──────────────────┐
│ ConsultService (app)       │
│                            │
│ - process_consult()        │
│ - validate_input()         │
└────────┬───────────────────┘
         │ 1:1
         │ returns
         │
┌────────v────────────────┐
│ ConsultResponse          │
│                          │
│ - message: str           │
│ - timestamp: datetime    │
└──────────────────────────┘


┌──────────────────────────┐
│ SecurityMiddleware       │
│                          │
│ - validate_header()      │ ←── validates against Config
└────────┬─────────────────┘
         │ 1:1
         │ creates
         │
┌────────v────────────────┐
│ SecurityContext          │
│                          │
│ - is_authorized: bool    │
│ - source: str            │
└──────────────────────────┘
```

---

## Data Flow

### Happy Path: Authorized Consult Request

```
NestJS Server
    │
    ├─ POST /api/v1/ai/consult
    ├─ Header: X-Internal-Secret: correct-value
    ├─ Body: {"message": "hello"}
    │
    ↓
[SecurityMiddleware]
    │
    ├─ Extract X-Internal-Secret header
    ├─ Load Config.x_internal_secret from env
    ├─ Compare: header == config
    ├─ Result: is_authorized = True
    ├─ Store in request.state.security_context
    │
    ↓
[ConsultRoute Handler]
    │
    ├─ Parse body → ConsultRequest
    ├─ Check request.state.security_context.is_authorized
    ├─ Call ConsultService.process_consult(request)
    │
    ↓
[ConsultService]
    │
    ├─ Validate message length
    ├─ Generate current timestamp (UTC)
    ├─ Create ConsultResponse(message=input.message, timestamp=now)
    │
    ↓
[Response Serialization]
    │
    ├─ Pydantic → JSON: {"message": "hello", "timestamp": "..."}
    │
    ↓
NestJS Server receives 200 OK + JSON response
```

### Error Path: Unauthorized Request (Invalid Secret)

```
NestJS Server
    │
    ├─ POST /api/v1/ai/consult
    ├─ Header: X-Internal-Secret: wrong-value
    │
    ↓
[SecurityMiddleware]
    │
    ├─ Extract X-Internal-Secret header
    ├─ Load Config.x_internal_secret from env
    ├─ Compare: header != config
    ├─ Result: is_authorized = False
    ├─ Return 403 Forbidden (STOP - never reaches route)
    │
NestJS Server receives 403 Forbidden (no body)
```

---

## Implementation Checklist

- [ ] Define `ConsultRequest` in `domain/models.py`
- [ ] Define `ConsultResponse` in `domain/models.py`
- [ ] Define `SecurityContext` in `domain/models.py`
- [ ] Define `Config` in `infra/config/settings.py`
- [ ] Create Pydantic schemas in `presentation/schemas.py` (maps to domain models)
- [ ] Create DTOs in `application/dto/` (if needed for transformation)
- [ ] Unit tests for each entity validation
- [ ] Integration tests for full data flow

---

**Status**: ✅ Complete  
**Next**: Create contracts/ and quickstart.md
