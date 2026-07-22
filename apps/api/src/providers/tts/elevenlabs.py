"""ElevenLabs TTS - Best human-like voice quality."""

import httpx
from typing import AsyncGenerator, Optional
from ...core.interfaces import TTSProvider
from ...config import get_settings


class ElevenLabsTTS(TTSProvider):
    def __init__(self):
        s = get_settings()
        self.api_key = s.elevenlabs_api_key
        self.voice_id = s.elevenlabs_voice_id
        self.model = s.elevenlabs_model

    async def synthesize_stream(self, text: str, language: str = "en", voice_id: Optional[str] = None) -> AsyncGenerator[bytes, None]:
        voice = voice_id or self.voice_id
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST", f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/stream",
                headers={"xi-api-key": self.api_key, "Content-Type": "application/json"},
                json={"text": text, "model_id": self.model, "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.3, "use_speaker_boost": True}},
                timeout=15.0,
            ) as r:
                if r.status_code == 200:
                    async for chunk in r.aiter_bytes(1024):
                        if chunk:
                            yield chunk

    async def synthesize(self, text: str, language: str = "en", voice_id: Optional[str] = None) -> bytes:
        voice = voice_id or self.voice_id
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice}",
                headers={"xi-api-key": self.api_key, "Content-Type": "application/json"},
                json={"text": text, "model_id": self.model, "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.3, "use_speaker_boost": True}},
                timeout=15.0,
            )
            return r.content if r.status_code == 200 else b""

    def get_supported_voices(self) -> list[dict]:
        return [
            {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Sarah", "gender": "female", "accent": "american"},
            {"id": "JBFqnCBsd6RMkjVDRZzb", "name": "George", "gender": "male", "accent": "british"},
            {"id": "onwK4e9ZLuTAKqWW03F9", "name": "Daniel", "gender": "male", "accent": "british"},
            {"id": "Xb7hH8MSUJpSbSDYk0k2", "name": "Alice", "gender": "female", "accent": "british"},
        ]
