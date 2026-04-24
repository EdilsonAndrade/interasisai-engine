# Research: FastAPI AI Engine Initialization

**Date**: 2026-04-24  
**Feature**: 001-ai-engine-initialization  
**Status**: Complete - All technical questions resolved

## Research Findings

### 1. FastAPI & Uvicorn Best Practices

**Decision**: Use FastAPI 0.104.1+ with Uvicorn as ASGI server

**Rationale**:
- FastAPI provides async-first design required for LLM processing
- Built-in OpenAPI documentation (Swagger UI)
- Native Pydantic v2 integration for validation
- Type hints enable IDE support and runtime validation
- Middleware system is clean and flexible

**Alternatives Considered**:
- Flask: Synchronous by default; requires additional async libraries
- Django: Heavier framework than needed for MVP; more configuration
- Starlette: Lower-level; FastAPI builds on it with more abstractions

**Implementation Details**:
- Use async route handlers for compatibility with async middleware
- Middleware executes before route handlers; can return early for 403
- Use `FastAPI()` app instance with `@app.middleware("http")` decorator
- Uvicorn runs on `0.0.0.0:8000` by default

**References**:
- https://fastapi.tiangolo.com/advanced/middleware/
- https://www.uvicorn.org/

---

### 2. Environment Variable Management with python-dotenv

**Decision**: Use `python-dotenv` to load environment variables from `.env` file

**Rationale**:
- Keeps secrets out of version control
- Supports per-environment configuration (dev/.env, test/.env.test, prod/.env.prod)
- Simple API: `load_dotenv()` then `os.getenv()`
- Works cross-platform (Windows, macOS, Linux)

**Implementation Details**:
- Call `load_dotenv()` once at application startup (in `infra/config/settings.py`)
- Use uppercase with underscores for env var names: `X_INTERNAL_SECRET`
- Provide `.env.example` with all required variables documented
- Fail loudly if required env vars are missing: `os.getenv("X_INTERNAL_SECRET") or raise ValueError(...)`

**Best Practices**:
- `.env` files in `.gitignore` (NEVER commit secrets)
- `.env.example` in version control (documents structure)
- Support `.env.test` for testing with test secrets
- Support `.env.local` for local overrides (optional)

**References**:
- https://github.com/theskumar/python-dotenv
- https://12factor.net/config

---

### 3. Pydantic v2 for Request/Response Validation

**Decision**: Use Pydantic v2 models for all request/response validation

**Rationale**:
- Strong type safety at runtime
- Automatic validation and error messages
- FastAPI automatically converts Pydantic models to/from JSON
- Generates OpenAPI schemas for documentation
- Supports custom validators and field constraints

**Implementation Details**:
- Define models in `domain/models.py` (business logic)
- Create DTOs in `application/dto/` for API layer conversion
- Use `FastAPI` route parameter annotations with Pydantic models
- FastAPI handles JSON serialization automatically
- Custom validators via `@field_validator` (Pydantic v2)

**Example**:
```python
from pydantic import BaseModel, Field

class ConsultRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)

class ConsultResponse(BaseModel):
    message: str
    timestamp: datetime
```

**References**:
- https://docs.pydantic.dev/latest/
- https://fastapi.tiangolo.com/tutorial/body/

---

### 4. Middleware Security Pattern

**Decision**: Implement custom HTTP middleware for `X-Internal-Secret` validation

**Rationale**:
- Middleware executes on every request before route handlers
- Can return 403 immediately without processing request body
- Cleaner than route-level decorators for cross-cutting concerns
- Follows FastAPI security best practices

**Implementation Details**:
- Create `infra/security/secret_validator.py` with validation logic
- Create `presentation/middleware/security_middleware.py` with FastAPI middleware
- Middleware checks for `X-Internal-Secret` header
- Compares against `X_INTERNAL_SECRET` from environment
- Returns `403 Forbidden` if missing or incorrect (no detailed error message to avoid information leakage)
- Passes validated `SecurityContext` to route handlers via request state

**Security Considerations**:
- Don't leak whether header is missing vs. incorrect
- Don't log the actual secret value (log only "validation pass/fail")
- Return same status code for all failures
- Time-constant comparison optional for MVP (use simple == for MVP)

**References**:
- https://fastapi.tiangolo.com/advanced/middleware/
- https://owasp.org/www-community/attacks/Information_exposure_through_an_error_message

---

### 5. Testing Strategy: Unit + Integration + Mocked

**Decision**: Combine unit tests (mocked dependencies) and integration tests (real middleware)

**Rationale**:
- Unit tests are fast, isolated, and test business logic
- Integration tests verify middleware-route interactions work correctly
- Mocking allows testing error cases (e.g., env var missing)
- 80% coverage threshold ensures critical paths are tested

**Unit Test Focus Areas**:
- `test_secret_validator.py`: Validate logic with mocked env vars
  - Test: secret matches → True
  - Test: secret mismatch → False
  - Test: missing secret env var → raises exception
  
- `test_middleware.py`: Middleware behavior with mocked FastAPI request
  - Test: valid header → passes request to handler
  - Test: invalid header → returns 403
  - Test: missing header → returns 403

- `test_consult_service.py`: Business logic with mocked dependencies
  - Test: echo functionality
  - Test: timestamp generation

**Integration Test Focus Areas**:
- `test_consult_endpoint.py`: Full request-response cycle
  - Test: POST /api/v1/ai/consult with valid secret → 200 + echoed message
  - Test: POST /api/v1/ai/consult without secret → 403
  - Test: POST /api/v1/ai/consult with wrong secret → 403
  - Test: Various valid/invalid payload sizes

- `test_security_flow.py`: Middleware + endpoint interaction
  - Test: Middleware rejects before route handler runs
  - Test: Authorized requests reach handler

**Tool Stack**:
- Framework: `pytest`
- Coverage: `pytest-cov` (minimum 80% line coverage)
- Mocking: `unittest.mock` (built-in) + `pytest-mock` (pytest plugin)
- Fixtures: `pytest` fixtures in `conftest.py` for reusable test setup

**Coverage Metrics**:
- Line coverage ≥ 80%
- Branch coverage ≥ 70% (edge cases)
- Critical path coverage = 100% (security middleware, validation)

**References**:
- https://docs.pytest.org/
- https://pytest-cov.readthedocs.io/
- https://docs.python.org/3/library/unittest.mock.html

---

### 6. Async Pattern in FastAPI

**Decision**: Use async route handlers and middleware for I/O efficiency

**Rationale**:
- FastAPI leverages async/await for handling multiple concurrent requests
- Async middleware integrates seamlessly with async routes
- Required for future LLM API calls (which are typically async)
- Better resource utilization than threads

**Implementation Details**:
- All route handlers: `async def endpoint(...)`
- Middleware: `async def middleware(...)`
- Use `await` for I/O operations (future LLM calls, database queries)
- For CPU-bound operations, use `asyncio.to_thread()` or thread pool

**Example**:
```python
@app.post("/api/v1/ai/consult")
async def consult(request: ConsultRequest):
    # Route handler is async
    service = ConsultService()
    response = await service.process_consult(request)
    return response
```

**References**:
- https://fastapi.tiangolo.com/async-and-await/
- https://fastapi.tiangolo.com/advanced/async-sql-databases/

---

### 7. Clean Architecture Layer Dependencies

**Decision**: Enforce strict dependency direction: Domain → Application → Infrastructure ← Presentation

**Rationale**:
- Domain layer has no dependencies (core business logic only)
- Application layer depends on domain + infra abstractions
- Infrastructure layer implements abstractions, external integrations
- Presentation layer depends on application layer
- Enables testing and future LLM provider swaps

**Dependency Rules**:
- ✅ Domain: No imports from other layers
- ✅ Application: Imports from domain + infra interfaces (via dependency injection)
- ✅ Infrastructure: Imports from domain (for interfaces) + third-party libs
- ✅ Presentation: Imports from application + domain models (for request/response)
- ❌ No circular dependencies
- ❌ No presentation logic in domain/application

**Example**:
```
Domain (models.py, interfaces.py)
  ↑
Application (services.py) → uses domain models, calls infra via interfaces
  ↑
Infrastructure (settings.py, secret_validator.py) → implements interfaces
  ↑
Presentation (routes.py) → calls application services
```

**References**:
- https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html

---

## Clarifications Resolved

✅ **All questions from spec have been researched and resolved. No NEEDS CLARIFICATION items remain.**

| Question | Answer | Source |
|----------|--------|--------|
| Which ASGI server? | Uvicorn | FastAPI docs |
| Env var management? | python-dotenv | 12-factor app principles |
| Secret comparison method? | Simple == for MVP | Security best practices |
| Test framework? | pytest + pytest-cov | Python testing standard |
| Async pattern? | async/await throughout | FastAPI design |
| Layer dependencies? | Domain → App → Infra ← Presentation | Clean Architecture |

---

**Status**: ✅ Ready for Phase 1 Design  
**Next**: Generate data-model.md, contracts/, quickstart.md
