# Tasks: FastAPI AI Engine Initialization with Security

**Input**: Design documents from `/specs/001-ai-engine-initialization/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/consult-api.md, quickstart.md

**Tests**: Testes sao obrigatorios para esta feature (unitarios com mocks + integracao), com cobertura minima de 80%.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3, US4)
- Every task includes explicit file path(s)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project bootstrap in repository root and baseline developer tooling.

- [ ] T001 Create initial Python package folders and `__init__.py` files in `domain/`, `application/`, `application/services/`, `application/dto/`, `infra/`, `infra/config/`, `infra/security/`, `infra/logging/`, `presentation/`, `presentation/routes/`, `presentation/middleware/`, `tests/`, `tests/unit/`, `tests/integration/`, `tests/fixtures/`
- [ ] T002 Create dependency manifest in `requirements.txt` with FastAPI, Uvicorn, Pydantic, python-dotenv, pytest, pytest-cov, pytest-mock
- [ ] T003 [P] Create environment templates in `.env.example` and `tests/fixtures/.env.test` with `X_INTERNAL_SECRET`, `LOG_LEVEL`, `APP_NAME`, `ENVIRONMENT`
- [ ] T004 [P] Update ignore rules in `.gitignore` and `.dockerignore` to exclude `.env`, `.venv`, `__pycache__`, `.pytest_cache`, `htmlcov`
- [ ] T005 Create pytest configuration in `pytest.ini` with coverage threshold >= 80 and test discovery for `tests/unit` and `tests/integration`
- [ ] T006 [P] Create application entrypoints in `main.py` and `presentation/main.py` with FastAPI app bootstrap placeholder
- [ ] T007 [P] Create baseline project documentation in `README.md` with setup, run, and test commands

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core cross-cutting components required before any user story work.

**CRITICAL**: No user story implementation starts before this phase is complete.

- [ ] T008 Implement strongly typed environment loader in `infra/config/settings.py` (load_dotenv, required variable validation, fail-fast)
- [ ] T009 [P] Define shared domain exceptions in `domain/exceptions.py` for unauthorized access and configuration errors
- [ ] T010 [P] Define domain interfaces in `domain/interfaces.py` for secret validation and logging abstractions
- [ ] T011 Implement secret loading and comparison helpers in `infra/security/secret_loader.py` and `infra/security/secret_validator.py`
- [ ] T012 Implement structured logger adapter in `infra/logging/logger.py` and wire with settings
- [ ] T013 Implement global error handlers and response mapping in `presentation/main.py` for 403, 422, and 500 contract behavior
- [ ] T014 [P] Implement reusable testing fixtures in `tests/integration/conftest.py` and `tests/fixtures/test_data.py`

**Checkpoint**: Foundation complete. User story implementation can begin.

---

## Phase 3: User Story 1 - Backend Server Bootstrap with Secure Communication (Priority: P1) MVP

**Goal**: Run FastAPI server with mandatory `X-Internal-Secret` enforcement and working consult echo endpoint.

**Independent Test**: Run server and verify `POST /api/v1/ai/consult` returns 403 without/with wrong secret and 200 with valid secret.

### Tests for User Story 1

- [ ] T015 [P] [US1] Add unit tests for secret validator decision branches in `tests/unit/test_security_validator.py`
- [ ] T016 [P] [US1] Add unit tests for middleware authorization paths in `tests/unit/test_middleware.py`
- [ ] T017 [P] [US1] Add integration tests for auth outcomes (missing/invalid/valid header) in `tests/integration/test_security_flow.py`
- [ ] T018 [US1] Add endpoint integration tests for consult happy path and forbidden responses in `tests/integration/test_consult_endpoint.py`

### Implementation for User Story 1

- [ ] T019 [P] [US1] Define domain entities `ConsultRequest`, `ConsultResponse`, `SecurityContext` in `domain/models.py`
- [ ] T020 [P] [US1] Define Pydantic API schemas for consult request/response in `presentation/schemas.py`
- [ ] T021 [US1] Implement `ConsultService` echo logic with UTC timestamp in `application/services/consult_service.py`
- [ ] T022 [US1] Implement security middleware to enforce `X-Internal-Secret` on all requests in `presentation/middleware/security_middleware.py`
- [ ] T023 [US1] Implement consult route handler `POST /api/v1/ai/consult` in `presentation/routes/consult_routes.py`
- [ ] T024 [US1] Wire middleware, routes, and startup settings in `presentation/main.py`
- [ ] T025 [US1] Make unit/integration tests pass for US1 and adjust implementation in `presentation/middleware/security_middleware.py`, `presentation/routes/consult_routes.py`, `application/services/consult_service.py`

**Checkpoint**: US1 independently functional and demonstrable as MVP.

---

## Phase 4: User Story 2 - Project Structure for Scalability (Priority: P2)

**Goal**: Enforce Clean Architecture boundaries and prepare extension points for future LLM/Langchain integration.

**Independent Test**: Validate imports and responsibilities by layer; add a sample LLM abstraction without changing route code.

### Tests for User Story 2

- [ ] T026 [P] [US2] Add architecture boundary tests for forbidden cross-layer imports in `tests/unit/test_architecture_boundaries.py`
- [ ] T027 [P] [US2] Add integration test ensuring API still works after dependency injection wiring in `tests/integration/test_app_wiring.py`

### Implementation for User Story 2

- [ ] T028 [P] [US2] Create application DTOs for request/response mapping in `application/dto/request.py` and `application/dto/response.py`
- [ ] T029 [US2] Refactor consult use case orchestration into `application/services/consult_service.py` using domain interfaces from `domain/interfaces.py`
- [ ] T030 [US2] Add LLM provider abstraction placeholder (`ILLMProvider`) in `domain/interfaces.py` and implementation stub in `infra/security/secret_validator.py` replaced by proper file `infra/llm/provider_stub.py`
- [ ] T031 [US2] Enforce dependency injection composition root in `presentation/main.py` (settings, logger, secret validator, services)
- [ ] T032 [US2] Update architecture documentation with layer responsibilities in `README.md`

**Checkpoint**: US2 complete, architecture is extensible for future LLM tooling.

---

## Phase 5: User Story 3 - Environment Configuration Management (Priority: P2)

**Goal**: Ensure environment-driven configuration is safe, explicit, and testable across dev/test contexts.

**Independent Test**: Boot with `.env` and `.env.test`, validate secret loading behavior and startup failure on missing required vars.

### Tests for User Story 3

- [ ] T033 [P] [US3] Add unit tests for settings validation and fail-fast behavior in `tests/unit/test_settings.py`
- [ ] T034 [P] [US3] Add unit tests for dotenv loader and default values in `tests/unit/test_secret_loader.py`
- [ ] T035 [US3] Add integration tests for startup behavior with valid/invalid environment in `tests/integration/test_env_startup.py`

### Implementation for User Story 3

- [ ] T036 [US3] Finalize settings object with strict required fields and environment enum checks in `infra/config/settings.py`
- [ ] T037 [US3] Implement startup config validation hook in `presentation/main.py`
- [ ] T038 [US3] Align environment templates and documentation in `.env.example`, `tests/fixtures/.env.test`, and `README.md`

**Checkpoint**: US3 complete with deterministic environment handling.

---

## Phase 6: User Story 4 - Test Coverage and Quality Assurance (Priority: P2)

**Goal**: Guarantee 80%+ coverage and robust quality gates with unit + integration + mocks.

**Independent Test**: Run `pytest --cov=. --cov-report=term-missing` and verify threshold passes and critical paths are fully covered.

### Tests for User Story 4

- [ ] T039 [P] [US4] Add unit tests for consult service edge cases (empty/long message handling contracts) in `tests/unit/test_consult_service.py`
- [ ] T040 [P] [US4] Add integration tests for 422 validation contract and timestamp response format in `tests/integration/test_consult_contract_validation.py`
- [ ] T041 [P] [US4] Add unit tests using mocks for logger and settings injection in `tests/unit/test_dependency_injection.py`
- [ ] T042 [US4] Add coverage gate test command and CI-friendly script in `README.md` and `pytest.ini`

### Implementation for User Story 4

- [ ] T043 [US4] Refine production code to satisfy all tests and remove flaky behavior in `application/services/consult_service.py`, `presentation/routes/consult_routes.py`, `infra/config/settings.py`
- [ ] T044 [US4] Ensure test pyramid balance and fixture reuse in `tests/integration/conftest.py` and `tests/fixtures/test_data.py`
- [ ] T045 [US4] Record final coverage baseline and critical-path matrix in `specs/001-ai-engine-initialization/quickstart.md`

**Checkpoint**: US4 complete with enforced quality baseline.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening and verification across all stories.

- [ ] T046 [P] Harmonize API docs and examples with implemented behavior in `specs/001-ai-engine-initialization/contracts/consult-api.md` and `README.md`
- [ ] T047 [P] Validate quickstart end-to-end commands and expected outputs in `specs/001-ai-engine-initialization/quickstart.md`
- [ ] T048 Run full test suite and coverage gate, fixing remaining gaps across `tests/unit/` and `tests/integration/`
- [ ] T049 [P] Security hardening review for forbidden-path responses and secret logging in `presentation/middleware/security_middleware.py` and `infra/logging/logger.py`
- [ ] T050 Final cleanup/refactor for readability and complexity (<5 cyclomatic per function) in `application/services/consult_service.py`, `presentation/main.py`, `presentation/routes/consult_routes.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 (Setup): starts immediately
- Phase 2 (Foundational): depends on Phase 1 and blocks all user stories
- Phase 3 (US1): depends on Phase 2
- Phase 4 (US2): depends on Phase 2 and can run after US1 MVP checkpoint
- Phase 5 (US3): depends on Phase 2 and can run in parallel with US2
- Phase 6 (US4): depends on US1/US2/US3 implementation completion
- Phase 7 (Polish): depends on all selected stories done

### User Story Dependencies

- US1 (P1): no dependency on other stories after foundation
- US2 (P2): independent from US3, uses US1 baseline app wiring
- US3 (P2): independent from US2, uses foundational settings/security
- US4 (P2): depends on implemented functionality from US1-US3 to reach coverage goals

### Within Each User Story

- Test tasks first (must fail before implementation)
- Models/schemas before services
- Services before middleware/routes wiring
- Integration validation before story checkpoint

## Parallel Opportunities

- Setup tasks: T003, T004, T006, T007 can run in parallel
- Foundational tasks: T009, T010, T014 can run in parallel
- US1 tests T015, T016, T017 can run in parallel
- US2 tests T026, T027 can run in parallel
- US3 tests T033, T034 can run in parallel
- US4 tests T039, T040, T041 can run in parallel
- Polish tasks T046, T047, T049 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Run in parallel after foundation:
Task T015 - tests/unit/test_security_validator.py
Task T016 - tests/unit/test_middleware.py
Task T017 - tests/integration/test_security_flow.py

# Run in parallel for implementation artifacts:
Task T019 - domain/models.py
Task T020 - presentation/schemas.py
```

## Parallel Example: User Story 2

```bash
Task T026 - tests/unit/test_architecture_boundaries.py
Task T028 - application/dto/request.py + application/dto/response.py
Task T032 - README.md
```

## Parallel Example: User Story 3

```bash
Task T033 - tests/unit/test_settings.py
Task T034 - tests/unit/test_secret_loader.py
Task T038 - .env.example + tests/fixtures/.env.test + README.md
```

## Parallel Example: User Story 4

```bash
Task T039 - tests/unit/test_consult_service.py
Task T040 - tests/integration/test_consult_contract_validation.py
Task T041 - tests/unit/test_dependency_injection.py
```

---

## Implementation Strategy

### MVP First (US1 only)

1. Finish Phase 1 and Phase 2
2. Deliver Phase 3 (US1) completely
3. Validate independent acceptance for secure consult endpoint
4. Demo/deploy MVP baseline

### Incremental Delivery

1. Add US2 (architecture hardening)
2. Add US3 (configuration hardening)
3. Add US4 (quality baseline and coverage)
4. Finish with Phase 7 polish

### Team Parallel Strategy

1. Team aligns on Phase 1 and Phase 2
2. After checkpoint, split work:
- Engineer A: US2 tasks
- Engineer B: US3 tasks
- Engineer C: US4 tests and coverage automation
3. Merge back for Phase 7 final hardening

---

## Notes

- All tasks follow mandatory checklist format.
- User story labels appear only in story phases.
- File paths target repository root (no `interasisai-ai-engine` subfolder).
- Tests are mandatory per spec and constitution.
