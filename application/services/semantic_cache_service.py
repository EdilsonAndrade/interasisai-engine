from domain.interfaces import EmbeddingProvider, SemanticCacheRepository
from domain.models import AudioPayload, RegistroSemantico


class SemanticCacheService:
    def __init__(
        self,
        repository: SemanticCacheRepository,
        embedding_provider: EmbeddingProvider,
        threshold: float,
    ) -> None:
        self._repository = repository
        self._embedding_provider = embedding_provider
        self._threshold = threshold

    @property
    def threshold(self) -> float:
        return self._threshold

    def find_match(self, query: str) -> tuple[RegistroSemantico, float] | None:
        embedding = self._embedding_provider.embed(query)
        return self._repository.find_best_match(embedding, self._threshold)

    def save_response(
        self,
        *,
        query: str,
        response_text: str,
        response_audio: AudioPayload,
    ) -> RegistroSemantico:
        embedding = self._embedding_provider.embed(query)
        return self._repository.save(
            query_canonical=query,
            embedding_vector=embedding,
            response_text=response_text,
            response_audio=response_audio,
        )

    def register_hit(self, semantic_id: str) -> None:
        self._repository.register_hit(semantic_id)
