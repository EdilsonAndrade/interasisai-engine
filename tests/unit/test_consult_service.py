import pytest

from application.services.consult_service import ConsultService
from domain.models import ConsultRequest
from tests.fixtures.test_data import LONG_MESSAGE, VALID_MESSAGE


@pytest.mark.asyncio
async def test_consult_service_echoes_message_with_timestamp() -> None:
    service = ConsultService()
    response = await service.process_consult(ConsultRequest(message=VALID_MESSAGE))

    assert response.message == VALID_MESSAGE
    assert response.timestamp is not None


@pytest.mark.asyncio
async def test_consult_service_rejects_blank_message() -> None:
    service = ConsultService()

    with pytest.raises(ValueError):
        await service.process_consult(ConsultRequest(message="   "))


@pytest.mark.asyncio
async def test_consult_service_rejects_too_long_message() -> None:
    service = ConsultService()

    with pytest.raises(ValueError):
        await service.process_consult(ConsultRequest(message=LONG_MESSAGE))
