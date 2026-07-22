"""Piper TTS - Local, free, open-source."""

import asyncio
import subprocess
from typing import AsyncGenerator, Optional
from ...core.interfaces import TTSProvider
from ...config import get_settings


class PiperTTS(TTSProvider):
    def __init__(self):
        self.model = get_settings().piper_model_path

    async def synthesize_stream(self, text: str, language: str = "en", voice_id: Optional[str] = None) -> AsyncGenerator[bytes, None]:
        audio = await self.synthesize(text, language, voice_id)
        for i in range(0, len(audio), 1024):
            yield audio[i:i+1024]

    async def synthesize(self, text: str, language: str = "en", voice_id: Optional[str] = None) -> bytes:
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._run, text, voice_id or self.model)
        except Exception:
            return b""

    def _run(self, text: str, model: str) -> bytes:
        try:
            p = subprocess.run(["piper", "--model", model, "--output-raw"], input=text.encode(), capture_output=True, timeout=10)
            return p.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return b""

    def get_supported_voices(self) -> list[dict]:
        return [{"id": "en_US-lessac-medium", "name": "Lessac", "gender": "male"}]
