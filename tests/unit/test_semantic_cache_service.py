from application.services.semantic_cache_service import SemanticCacheService
from domain.models import AudioPayload
from infra.semantic.embedding_provider_stub import EmbeddingProviderStub
from infra.semantic.in_memory_semantic_cache import InMemorySemanticCacheRepository


def test_semantic_cache_service_returns_match_above_threshold() -> None:
    repository = InMemorySemanticCacheRepository()
    service = SemanticCacheService(
        repository=repository,
        embedding_provider=EmbeddingProviderStub(),
        threshold=0.85,
    )
    audio = AudioPayload(
        mime_type="audio/mpeg",
        encoding="base64",
        content="abc",
        duration_ms=1200,
    )
    service.save_response(query="quais horarios de atendimento", response_text="8h as 18h", response_audio=audio)

    match = service.find_match("quais horarios de atendimento")

    assert match is not None
    record, score = match
    assert record.response_text == "8h as 18h"
    assert score >= 0.85


def test_semantic_cache_service_returns_none_below_threshold() -> None:
    repository = InMemorySemanticCacheRepository()
    service = SemanticCacheService(
        repository=repository,
        embedding_provider=EmbeddingProviderStub(),
        threshold=0.99,
    )
    audio = AudioPayload(
        mime_type="audio/mpeg",
        encoding="base64",
        content="abc",
        duration_ms=1200,
    )
    service.save_response(query="quais horarios de atendimento", response_text="8h as 18h", response_audio=audio)

    match = service.find_match("segunda via de boleto")

    assert match is None
