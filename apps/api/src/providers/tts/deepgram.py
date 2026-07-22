"""Deepgram TTS - Fast, affordable streaming voice."""

import httpx
from typing import AsyncGenerator, Optional
from ...core.interfaces import TTSProvider
from ...config import get_settings


class DeepgramTTS(TTSProvider):
    def __init__(self):
        s = get_settings()
        self.api_key = s.deepgram_api_key
        self.model = s.deepgram_tts_model

    async def synthesize_stream(self, text: str, language: str = "en", voice_id: Optional[str] = None) -> AsyncGenerator[bytes, None]:
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST", "https://api.deepgram.com/v1/speak",
                headers={"Authorization": f"Token {self.api_key}", "Content-Type": "application/json"},
                params={"model": voice_id or self.model},
                json={"text": text}, timeout=15.0,
            ) as r:
                if r.status_code == 200:
                    async for chunk in r.aiter_bytes(1024):
                        yield chunk

    async def synthesize(self, text: str, language: str = "en", voice_id: Optional[str] = None) -> bytes:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://api.deepgram.com/v1/speak",
                headers={"Authorization": f"Token {self.api_key}", "Content-Type": "application/json"},
                params={"model": voice_id or self.model},
                json={"text": text}, timeout=15.0,
            )
            return r.content if r.status_code == 200 else b""

    def get_supported_voices(self) -> list[dict]:
        return [
            {"id": "aura-asteria-en", "name": "Asteria", "gender": "female"},
            {"id": "aura-orion-en", "name": "Orion", "gender": "male"},
        ]
