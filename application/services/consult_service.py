from domain.models import ConsultRequest, ConsultResponse


class ConsultService:
    async def process_consult(self, request: ConsultRequest) -> ConsultResponse:
        message = request.message.strip()
        if not message:
            raise ValueError("message cannot be empty")
        if len(message) > 2000:
            raise ValueError("message exceeds maximum length")
        return ConsultResponse.now(message=message)
