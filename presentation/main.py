from contextlib import asynccontextmanager

import langchain  # noqa: F401  # smoke import: ensure LangChain ecosystem is available at boot

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from application.services.consult_service import ConsultService
from application.services.langchain_chat_use_case import LangChainChatUseCase
from application.services.semantic_cache_service import SemanticCacheService
from infra.config.settings import Settings, load_settings
from infra.llm.provider_stub import LLMProviderStub
from infra.logging.logger import AppLogger
from infra.semantic.embedding_provider_stub import EmbeddingProviderStub
from infra.semantic.in_memory_semantic_cache import InMemorySemanticCacheRepository
from infra.speech.stt_provider_stub import STTProviderStub
from infra.speech.tts_provider_stub import TTSProviderStub
from infra.security.secret_validator import SecretValidator
from presentation.middleware.security_middleware import SecurityMiddleware
from presentation.openapi import (
    API_DESCRIPTION,
    API_TITLE,
    API_VERSION,
    OPENAPI_TAGS,
)
from presentation.routes.chat_routes import router as chat_router
from presentation.routes.consult_routes import router as consult_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = load_settings(dotenv_path=".env")
    _wire_dependencies(app, settings)

    yield


def create_app(settings_override: Settings | None = None) -> FastAPI:
    app = FastAPI(
        title=API_TITLE,
        description=API_DESCRIPTION,
        version=API_VERSION,
        openapi_tags=OPENAPI_TAGS,
        lifespan=lifespan,
    )

    if settings_override is not None:
        _wire_dependencies(app, settings_override)

    @app.middleware("http")
    async def security_middleware(request: Request, call_next):
        validator = getattr(request.app.state, "secret_validator", None)
        if validator is None:
            settings = getattr(request.app.state, "settings", None)
            if settings is None:
                settings = load_settings(dotenv_path=".env")
                request.app.state.settings = settings
            validator = SecretValidator(settings)
            request.app.state.secret_validator = validator

        logger = getattr(request.app.state, "logger", None)
        middleware = SecurityMiddleware(validator=validator, logger=logger)
        return await middleware(request, call_next)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.exception_handler(Exception)
    async def generic_exception_handler(_: Request, __: Exception) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    app.include_router(consult_router)
    app.include_router(chat_router)
    return app


app = create_app()


def _wire_dependencies(app: FastAPI, settings: Settings) -> None:
    logger = AppLogger(settings.app_name, settings.log_level)
    secret_validator = SecretValidator(settings)
    semantic_repository = InMemorySemanticCacheRepository()
    embedding_provider = EmbeddingProviderStub()
    semantic_cache_service = SemanticCacheService(
        repository=semantic_repository,
        embedding_provider=embedding_provider,
        threshold=settings.semantic_match_threshold,
    )
    llm_provider = LLMProviderStub()
    stt_provider = STTProviderStub()
    tts_provider = TTSProviderStub()

    app.state.settings = settings
    app.state.logger = logger
    app.state.secret_validator = secret_validator
    app.state.consult_service = ConsultService()
    app.state.semantic_cache_service = semantic_cache_service
    app.state.chat_use_case = LangChainChatUseCase(
        semantic_cache_service=semantic_cache_service,
        settings=settings,
        llm_provider=llm_provider,
        stt_provider=stt_provider,
        tts_provider=tts_provider,
        logger=logger,
    )
