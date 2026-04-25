import base64

from domain.exceptions import AudioSynthesisError
from domain.interfaces import TTSProvider
from domain.models import AudioPayload


class TTSProviderStub(TTSProvider):
    def synthesize(self, text: str) -> AudioPayload:
        if "[tts_fail]" in text:
            raise AudioSynthesisError("Falha ao sintetizar audio para a resposta atual.")
        raw_audio = f"AUDIO:{text}".encode("utf-8")
        encoded = base64.b64encode(raw_audio).decode("ascii")
        duration_ms = max(500, min(15000, len(text) * 45))
        return AudioPayload(
            mime_type="audio/mpeg",
            encoding="base64",
            content=encoded,
            duration_ms=duration_ms,
        )
