from domain.interfaces import STTProvider


class STTProviderStub(STTProvider):
    def transcribe(self, audio_bytes: bytes, mime_type: str | None) -> tuple[str, float]:
        if not audio_bytes:
            return "audio processado", 0.8
        payload = audio_bytes.decode("utf-8", errors="ignore").strip()
        if "LOW_CONF" in payload:
            text = payload.replace("LOW_CONF", "").strip() or "audio incompreensivel"
            return text, 0.4
        if payload.startswith("TEXT:"):
            return payload.replace("TEXT:", "", 1).strip(), 0.95
        if payload:
            return payload, 0.85
        return "audio processado", 0.8
