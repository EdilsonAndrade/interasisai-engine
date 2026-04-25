from dataclasses import replace
from datetime import datetime, timezone
from math import sqrt
from uuid import uuid4

from domain.interfaces import SemanticCacheRepository
from domain.models import AudioPayload, RegistroSemantico


class InMemorySemanticCacheRepository(SemanticCacheRepository):
    def __init__(self) -> None:
        self._items: list[RegistroSemantico] = []

    def find_best_match(
        self, embedding_vector: list[float], threshold: float
    ) -> tuple[RegistroSemantico, float] | None:
        best: tuple[RegistroSemantico, float] | None = None
        for item in self._items:
            score = _cosine_similarity(embedding_vector, item.embedding_vector)
            if score < threshold:
                continue
            if best is None or score > best[1]:
                best = (item, score)
        return best

    def save(
        self,
        *,
        query_canonical: str,
        embedding_vector: list[float],
        response_text: str,
        response_audio: AudioPayload,
    ) -> RegistroSemantico:
        now = datetime.now(timezone.utc)
        record = RegistroSemantico(
            semantic_id=str(uuid4()),
            query_canonical=query_canonical,
            embedding_vector=embedding_vector,
            response_text=response_text,
            response_audio=response_audio,
            created_at=now,
            updated_at=now,
            hit_count=0,
        )
        self._items.append(record)
        return record

    def register_hit(self, semantic_id: str) -> None:
        for index, item in enumerate(self._items):
            if item.semantic_id != semantic_id:
                continue
            self._items[index] = replace(
                item,
                hit_count=item.hit_count + 1,
                updated_at=datetime.now(timezone.utc),
            )
            return


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    numerator = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = sqrt(sum(a * a for a in left))
    right_norm = sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)
