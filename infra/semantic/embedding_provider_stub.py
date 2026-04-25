from domain.interfaces import EmbeddingProvider


class EmbeddingProviderStub(EmbeddingProvider):
    def embed(self, text: str) -> list[float]:
        normalized = text.strip().lower()
        if not normalized:
            return [0.0] * 8
        buckets = [0.0] * 8
        for index, char in enumerate(normalized):
            bucket = index % 8
            buckets[bucket] += ord(char)
        magnitude = sum(value * value for value in buckets) ** 0.5
        if magnitude == 0:
            return [0.0] * 8
        return [value / magnitude for value in buckets]
