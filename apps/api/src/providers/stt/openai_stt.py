"""OpenAI Whisper API STT - Cloud, high accuracy."""

import httpx
from typing import AsyncGenerator, Optional
from ...core.interfaces import STTProvider
from ...config import get_settings


class OpenAISTT(STTProvider):
    def __init__(self):
        self.api_key = get_settings().openai_api_key

    async def transcribe_stream(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[str, None]:
        buffer = b""
        async for chunk in audio_stream:
            buffer += chunk
            if len(buffer) >= 48000:
                text = await self.transcribe_buffer(buffer)
                buffer = b""
                if text.strip():
                    yield text
        if buffer:
            text = await self.transcribe_buffer(buffer)
            if text.strip():
                yield text

    async def transcribe_buffer(self, audio_bytes: bytes, language: Optional[str] = None) -> str:
        async with httpx.AsyncClient() as client:
            files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
            data = {"model": "whisper-1"}
            if language:
                data["language"] = language
            r = await client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                files=files, data=data, timeout=30.0,
            )
            return r.json().get("text", "") if r.status_code == 200 else ""

    async def detect_language(self, audio_bytes: bytes) -> str:
        async with httpx.AsyncClient() as client:
            files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
            r = await client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                files=files, data={"model": "whisper-1", "response_format": "verbose_json"}, timeout=30.0,
            )
            return r.json().get("language", "en") if r.status_code == 200 else "en"
