import logging

from domain.interfaces import ILogger


class AppLogger(ILogger):
    def __init__(self, name: str, level: str = "INFO") -> None:
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def info(self, message: str) -> None:
        self._logger.info(message)

    def warning(self, message: str) -> None:
        self._logger.warning(message)

    def error(self, message: str) -> None:
        self._logger.error(message)

    def event(
        self,
        *,
        event_type: str,
        request_id: str,
        latency_ms: int,
        similarity_score: float | None = None,
    ) -> None:
        payload = (
            "event={event} request_id={request_id} latency_ms={latency_ms} "
            "similarity_score={similarity_score}"
        ).format(
            event=event_type,
            request_id=request_id,
            latency_ms=latency_ms,
            similarity_score=similarity_score,
        )
        self.info(payload)
