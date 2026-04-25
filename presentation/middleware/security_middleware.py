from dataclasses import dataclass, field
from typing import Iterable, Optional

from fastapi import Request
from starlette.responses import JSONResponse

from domain.interfaces import ILogger
from domain.models import AccessDenialEvent, SecurityContext
from infra.security.secret_validator import SecretValidator


_DEFAULT_PUBLIC_PATHS: frozenset[str] = frozenset(
    {
        "/docs",
        "/docs/oauth2-redirect",
        "/redoc",
        "/openapi.json",
    }
)


@dataclass(slots=True)
class SecurityMiddleware:
    validator: SecretValidator
    logger: Optional[ILogger] = None
    public_paths: frozenset[str] = field(default_factory=lambda: _DEFAULT_PUBLIC_PATHS)

    async def __call__(self, request: Request, call_next):
        if self._is_public_path(request.url.path):
            request.state.security_context = SecurityContext(is_authorized=False, source="public")
            return await call_next(request)

        provided_secret = request.headers.get("X-Internal-Secret")
        if not self.validator.is_valid(provided_secret):
            reason = "missing_header" if provided_secret is None else "invalid_secret"
            self._log_denial(request, reason)
            request.state.security_context = SecurityContext(is_authorized=False, source="unknown")
            return JSONResponse(status_code=403, content={"detail": "Forbidden"})

        request.state.security_context = SecurityContext(is_authorized=True, source="internal")
        return await call_next(request)

    def _is_public_path(self, path: str) -> bool:
        return path in self.public_paths

    def _log_denial(self, request: Request, reason: str) -> None:
        if self.logger is None:
            return
        client_host = request.client.host if request.client else None
        event = AccessDenialEvent.create(path=request.url.path, reason=reason, client_host=client_host)
        self.logger.warning(
            f"access_denied path={event.path} reason={event.reason} client={event.client_host} ts={event.timestamp.isoformat()}"
        )


def public_paths(extra: Iterable[str] = ()) -> frozenset[str]:
    return frozenset(_DEFAULT_PUBLIC_PATHS | set(extra))
