# Implementation Plan: FastAPI AI Engine Initialization with Security

**Branch**: `001-ai-engine-initialization` | **Date**: 2026-04-24 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-ai-engine-initialization/spec.md` (EDI-22)

**Note**: This plan implements Phase 0 (Research) and Phase 1 (Design & Contracts) of the speckit workflow.

## Summary

Initialize a production-ready Python FastAPI server with secure internal communication (`X-Internal-Secret` header validation), Clean Architecture structure (domain/application/infra/presentation layers), and comprehensive test coverage (80%+ unit + integration tests). This foundation enables future LLM integration via Langchain while maintaining security, scalability, and code quality standards.

## Technical Context

**Language/Version**: Python 3.9+  
**Primary Dependencies**: FastAPI, Uvicorn, Pydantic, python-dotenv, pytest, pytest-cov  
**Storage**: N/A (MVP - in-memory only)  
**Testing**: pytest with pytest-cov (coverage) and unittest.mock (mocking)  
**Target Platform**: Linux containers (Docker); local development on Windows/Mac/Linux  
**Project Type**: Web-service (async FastAPI backend)  
**Performance Goals**: <100ms p95 latency for authenticated requests  
**Constraints**: <403 response time for invalid requests; 80% code coverage minimum  
**Scale/Scope**: Single-instance deployment v1; support for ~100 concurrent connections

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Constitutional Alignment Verified**:

1. **Clean Architecture** - Plan calls for domain/application/infra/presentation layers ✓
2. **Mandatory Test Coverage** - 80% coverage requirement + unit + integration tests specified ✓
3. **SOLID Principles** - Dependency injection, low cyclomatic complexity (<5) targeted ✓
4. **Security First** - Environment-based secrets (python-dotenv), no hardcoding ✓
5. **Dependency Injection** - Middleware and handlers accept dependencies as parameters ✓

**No violations identified.** All requirements align with constitution principles.

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-engine-initialization/
├── plan.md              # This file
├── research.md          # Phase 0 output (research and clarifications)
├── data-model.md        # Phase 1 output (entities and domain model)
├── quickstart.md        # Phase 1 output (setup and testing guide)
├── contracts/           # Phase 1 output (API contract definitions)
│   └── consult-api.md   # POST /api/v1/ai/consult contract
└── checklists/
    └── requirements.md  # Feature acceptance checklist
```

### Source Code (Repository Root: c:\projects\interasisai-engine)

```text
.
├── domain/                           # Domain layer (business logic, entities)
│   ├── __init__.py
│   ├── models.py                     # ConsultRequest, ConsultResponse, SecurityContext
│   ├── interfaces.py                 # ISecurityValidator, ILogger, etc.
│   └── exceptions.py                 # Custom domain exceptions
│
├── application/                      # Application layer (use cases, orchestration)
│   ├── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── consult_service.py       # ConsultService business logic
│   └── dto/                          # Data Transfer Objects
│       ├── __init__.py
│       ├── request.py                # ConsultRequest DTO
│       └── response.py               # ConsultResponse DTO
│
├── infra/                            # Infrastructure layer (external integrations)
│   ├── __init__.py
│   ├── security/
│   │   ├── __init__.py
│   │   ├── secret_loader.py         # Load X_INTERNAL_SECRET from env
│   │   └── secret_validator.py      # Validate X-Internal-Secret header
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py               # Environment configuration (python-dotenv)
│   └── logging/
│       ├── __init__.py
│       └── logger.py                 # Logging abstraction
│
├── presentation/                     # Presentation layer (API, routes)
│   ├── __init__.py
│   ├── main.py                       # FastAPI app initialization
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── security_middleware.py   # X-Internal-Secret validation middleware
│   ├── routes/
│   │   ├── __init__.py
│   │   └── consult_routes.py         # POST /api/v1/ai/consult endpoint
│   └── schemas.py                    # Pydantic schemas for request/response
│
├── tests/                            # Test directory
│   ├── __init__.py
│   ├── unit/                         # Unit tests (mocked dependencies)
│   │   ├── __init__.py
│   │   ├── test_security_validator.py
│   │   ├── test_consult_service.py
│   │   ├── test_secret_loader.py
│   │   └── test_middleware.py
│   ├── integration/                  # Integration tests (real middleware + endpoints)
│   │   ├── __init__.py
│   │   ├── test_consult_endpoint.py
│   │   ├── test_security_flow.py
│   │   └── conftest.py               # Pytest fixtures and test config
│   ├── fixtures/
│   │   ├── __init__.py
│   │   ├── .env.test                 # Test environment variables
│   │   └── test_data.py              # Shared test data
│   └── pytest.ini                    # Pytest configuration (coverage settings)
│
├── .env.example                      # Example environment variables
├── .env                              # Actual environment (git-ignored)
├── .gitignore                        # Git ignore rules
├── requirements.txt                  # Python dependencies
├── main.py                           # Entry point (runs presentation.main)
├── README.md                         # Project documentation
└── Dockerfile                        # Docker configuration (for future use)
```

**Structure Decision**: Clean Architecture (4-layer) selected per constitutional requirements. Single project structure with clear separation:
- **Domain**: Business logic, agnostic of frameworks
- **Application**: Orchestration and services
- **Infrastructure**: External integrations (env config, logging)
- **Presentation**: API routes and middleware
- **Tests**: Parallel structure mirroring source (unit + integration)

---

## Phase 0: Research & Clarifications

**Status**: All technical context from spec is clear. No NEEDS CLARIFICATION items.

**Research Findings** (will be detailed in `research.md`):

1. **FastAPI + Uvicorn**: Best practices for async middleware in FastAPI
   - Middleware runs before route handlers
   - Async middleware can await operations
   - Return responses early to reject unauthorized requests

2. **Python-dotenv**: Best practices for environment management
   - .env files in project root or subdirectories (specify path)
   - Environment variable naming: `X_INTERNAL_SECRET` (uppercase with underscores)
   - Missing env vars can default or fail at startup

3. **Pydantic v2**: Request/response validation
   - Models with Field() for validation rules
   - Automatic OpenAPI documentation integration

4. **pytest Configuration**: 80% coverage targets
   - pytest-cov plugin for coverage reporting
   - `pytest --cov=. --cov-report=term` for local runs
   - `pytest --cov=. --cov-report=html` for detailed reports

5. **Mocking Strategy**: unittest.mock and pytest-mock
   - Mock environment variable loading in unit tests
   - Mock FastAPI request/response in unit tests
   - Real middleware execution in integration tests

---

## Phase 1: Design & Contracts

### Data Model (will be in `data-model.md`)

**Entities identified**:

1. **ConsultRequest** (Domain entity)
   - `message: str` - consultation query
   - Validation: non-empty message (max 2000 chars for MVP)

2. **ConsultResponse** (Domain entity)
   - `message: str` - echoed from request
   - `timestamp: datetime` - response time
   - Future fields: llm_response, token_usage, execution_trace

3. **SecurityContext** (Domain entity)
   - `is_authorized: bool` - validation result
   - `source: str` - "internal" or other
   - Future fields: origin_ip, request_id

4. **Config** (Infrastructure entity)
   - `x_internal_secret: str` - loaded from environment
   - `log_level: str` - logging configuration
   - Future fields: llm_provider_keys, database_url

### API Contract (will be in `contracts/consult-api.md`)

**Endpoint**: `POST /api/v1/ai/consult`

**Request**:
```json
{
  "message": "string (required, 1-2000 chars)"
}
```

**Response (200 OK)**:
```json
{
  "message": "string (echoed)",
  "timestamp": "ISO8601 datetime"
}
```

**Response (403 Forbidden)**: Missing or invalid `X-Internal-Secret` header
```json
{
  "detail": "Forbidden"
}
```

**Headers Required**:
- `X-Internal-Secret: <secret-value>` (validated against `X_INTERNAL_SECRET` env var)

### Quickstart Guide (will be in `quickstart.md`)

**Setup**:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your X_INTERNAL_SECRET value
```

**Run Server**:
```bash
uvicorn presentation.main:app --reload
# Server runs on http://localhost:8000
```

**Test Security Validation**:
```bash
# Without header (should get 403)
curl -X POST http://localhost:8000/api/v1/ai/consult \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}'

# With correct header
curl -X POST http://localhost:8000/api/v1/ai/consult \
  -H "Content-Type: application/json" \
  -H "X-Internal-Secret: your-secret-from-env" \
  -d '{"message": "hello"}'
```

**Run Tests**:
```bash
# Run all tests with coverage
pytest --cov=. --cov-report=term-missing

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

---

## Implementation Phases Summary

| Phase | Deliverables | Owner | Timeline |
|-------|--------------|-------|----------|
| Phase 0 | research.md (done above) | Analysis | Now |
| Phase 1 | data-model.md, contracts/, quickstart.md | Design | Now |
| Phase 2 | tasks.md (via /speckit.tasks) | Planning | After Phase 1 |
| Phase 3 | Implementation (per tasks.md) | Dev | After Phase 2 |

---

**Version**: 1.0.0 | **Created**: 2026-04-24 | **Branch**: 001-ai-engine-initialization
