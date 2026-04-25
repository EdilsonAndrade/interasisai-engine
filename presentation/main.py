from contextlib import asynccontextmanager

import langchain  # noqa: F401  # smoke import: ensure LangChain ecosystem is available at boot

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from application.services.consult_service import ConsultService
from application.services.langchain_chat_use_case import LangChainChatUseCase
from infra.config.settings import Settings, load_settings
from infra.logging.logger import AppLogger
from infra.security.secret_validator import SecretValidator
from presentation.middleware.security_middleware import SecurityMiddleware
from presentation.routes.chat_routes import router as chat_router
from presentation.routes.consult_routes import router as consult_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = load_settings()
    logger = AppLogger(settings.app_name, settings.log_level)
    secret_validator = SecretValidator(settings)

    app.state.settings = settings
    app.state.logger = logger
    app.state.secret_validator = secret_validator
    app.state.consult_service = ConsultService()
    app.state.chat_use_case = LangChainChatUseCase(logger=logger)

    yield


def create_app(settings_override: Settings | None = None) -> FastAPI:
    app = FastAPI(title="InterasisAI Engine", lifespan=lifespan)

    if settings_override is not None:
        app.state.settings = settings_override
        app.state.logger = AppLogger(settings_override.app_name, settings_override.log_level)
        app.state.secret_validator = SecretValidator(settings_override)
        app.state.consult_service = ConsultService()
        app.state.chat_use_case = LangChainChatUseCase(logger=app.state.logger)

    @app.middleware("http")
    async def security_middleware(request: Request, call_next):
        validator = getattr(request.app.state, "secret_validator", None)
        if validator is None:
            settings = getattr(request.app.state, "settings", None)
            if settings is None:
                settings = load_settings()
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
