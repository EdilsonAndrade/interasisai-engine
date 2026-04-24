# Interasisai AI Engine Constitution

A constitution defining the non-negotiable development practices, architectural principles, and quality standards for the Interasisai AI Engine project - a Python FastAPI-based service for LLM orchestration and AI integration.

## Core Principles

### I. Clean Architecture with Separation of Concerns
The codebase MUST follow Clean Architecture layers: `domain/`, `application/`, `infra/`, `presentation/`. Each layer has explicit responsibilities:
- **Domain**: Core business logic, entities, and interfaces (framework-agnostic)
- **Application**: Use cases, orchestration, and service logic
- **Infrastructure**: External integrations, database, LLM providers, dependency implementations
- **Presentation**: API routes, DTOs, request/response handling

**Rationale**: Enables future integration of LLM frameworks (Langchain, Llama-index, etc.) without restructuring. Facilitates testing and maintenance.

### II. Mandatory Test Coverage: Unit, Integration, and Mocked Tests
Test coverage MUST be at least 80% across all code paths. The following test types are MANDATORY:

- **Unit Tests with Mocks**: Test individual functions/classes in isolation, mocking external dependencies (environment variables, future LLM providers, database connections)
  - Middleware security logic MUST be unit tested with mocked FastAPI dependencies
  - Request/response validation MUST be unit tested independently
  - Mock external I/O to ensure fast, deterministic tests

- **Integration Tests**: Verify end-to-end functionality including middleware integration with routes
  - Middleware + endpoint interactions MUST be tested together
  - Full request/response flows MUST be validated
  - Use test configurations (test `.env` files) for integration scenarios

- **When Mocking Makes Sense**: Mock async operations, environment variable loading, future LLM API calls; DO NOT mock the security middleware during integration tests (test it live)

**Testing Framework**: pytest with pytest-cov (coverage), unittest.mock (mocking)

**Rationale**: Catches regressions early, ensures security validations are correct, enables safe refactoring, and builds confidence in critical code paths (especially security middleware).

### III. SOLID Principles and Low Cyclomatic Complexity
Code MUST adhere to SOLID principles:
- **S**ingle Responsibility: Each class/function has one reason to change
- **O**pen/Closed: Open for extension, closed for modification
- **L**iskov Substitution: Implementations must be substitutable
- **I**nterface Segregation: Clients depend on specific interfaces, not monolithic ones
- **D**ependency Inversion: Depend on abstractions, not concrete implementations

Cyclomatic complexity MUST NOT exceed 5 per function. Measured via linting tools.

**Rationale**: Prepares foundation for Langchain/LLM tool integration, reduces maintenance burden, improves code reusability.

### IV. Security First: Environment-Based Secrets and Internal Authentication
Secrets (including `X_INTERNAL_SECRET`) MUST NEVER be hardcoded:
- All configuration loaded from environment variables via python-dotenv
- `.env` files MUST be in `.gitignore` to prevent accidental commits
- `X-Internal-Secret` header validation MUST occur on every request (middleware level)
- Security middleware MUST return 403 Forbidden for invalid/missing secrets without revealing why

**Rationale**: Protects credentials, enforces consistent security posture, enables environment-specific deployments (dev/test/prod).

### V. Clear Abstraction Boundaries and Dependency Injection
All external dependencies (FastAPI, LLM providers, databases, environment) MUST be injected, not hardcoded:
- Middleware and route handlers MUST accept dependencies as parameters
- Infrastructure implementations MUST be in `infra/` layer
- Tests MUST be able to provide mock implementations

**Rationale**: Enables testability, supports multiple LLM backends, allows configuration flexibility.

## Development Standards

### Code Organization
- **Structure**: Domain → Application → Infrastructure → Presentation (dependency direction: inward)
- **Naming**: Clear, descriptive names; no abbreviations unless standard (e.g., `X_INTERNAL_SECRET`, `ConsultRequest`)
- **Async/Await**: FastAPI routes MUST use async functions for compatibility with async middleware

### Deployment Configuration
- `.env.example`: MUST document all required environment variables with placeholders
- `.gitignore`: MUST include `.env`, `__pycache__/`, `.venv/`, `*.pyc`, `tests/.pytest_cache`
- `requirements.txt`: MUST pin versions for reproducibility; include: FastAPI, Uvicorn, Pydantic, python-dotenv, pytest, pytest-cov

### Documentation
- Clear docstrings for all public functions and classes
- README MUST describe project structure, setup instructions, and testing procedures
- Inline comments for complex logic only (code clarity preferred)

## Future-Proofing Constraints

### LLM Integration Readiness
The architecture MUST support future Langchain integration without refactoring:
- Domain layer: Define LLM-agnostic interfaces (e.g., `ILLMProvider`)
- Application layer: Create use cases for LLM chains and prompt management
- Infrastructure layer: Implement concrete LLM providers (OpenAI, Anthropic, local models)
- No hardcoding of specific LLM library names in domain or core logic

### No Framework Lock-in
Infrastructure layer MUST be swappable:
- Future migration between Langchain, Llama-index, or other AI frameworks MUST NOT require application/domain layer changes
- Database/persistence will be abstracted when added
- HTTP clients will use dependency injection

## Governance

### Constitution Authority
This constitution supersedes all other guidance documents. All PRs, code reviews, and design decisions MUST verify compliance with these principles.

### Amending the Constitution
Constitution changes MUST:
1. Be justified with rationale (why the change, what problem it solves)
2. Document backward compatibility impact (MAJOR/MINOR/PATCH version bump)
3. Include migration plan if existing code is affected
4. Be approved before implementation

### Version Bumping Rules
- **MAJOR**: Principle removal or redefinition affecting existing code (e.g., architecture layer removal)
- **MINOR**: New principle added or existing principle expanded (e.g., new test requirement)
- **PATCH**: Clarifications, wording improvements, typo fixes

### Compliance Verification
- **Code Review Gate**: Every PR MUST pass linting (cyclomatic complexity check) and achieve 80% test coverage
- **Automated Checks**: Use pytest with coverage reports, linters (pylint, flake8)
- **Manual Review**: Architects verify Clean Architecture boundaries and SOLID principle adherence

**Reference Documentation**: See `.github/copilot-instructions.md` and `/specs/` for implementation details.

---

**Version**: 1.0.0 | **Ratified**: 2026-04-24 | **Last Amended**: 2026-04-24
