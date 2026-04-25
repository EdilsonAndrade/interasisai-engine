from dataclasses import dataclass
from typing import Optional

from fastapi import Request
from starlette.responses import JSONResponse

from domain.interfaces import ILogger
from domain.models import AccessDenialEvent, SecurityContext
from infra.security.secret_validator import SecretValidator


@dataclass(slots=True)
class SecurityMiddleware:
    validator: SecretValidator
    logger: Optional[ILogger] = None

    async def __call__(self, request: Request, call_next):
        provided_secret = request.headers.get("X-Internal-Secret")
        if not self.validator.is_valid(provided_secret):
            reason = "missing_header" if provided_secret is None else "invalid_secret"
            self._log_denial(request, reason)
            request.state.security_context = SecurityContext(is_authorized=False, source="unknown")
            return JSONResponse(status_code=403, content={"detail": "Forbidden"})

        request.state.security_context = SecurityContext(is_authorized=True, source="internal")
        return await call_next(request)

    def _log_denial(self, request: Request, reason: str) -> None:
        if self.logger is None:
            return
        client_host = request.client.host if request.client else None
        event = AccessDenialEvent.create(path=request.url.path, reason=reason, client_host=client_host)
        self.logger.warning(
            f"access_denied path={event.path} reason={event.reason} client={event.client_host} ts={event.timestamp.isoformat()}"
        )
