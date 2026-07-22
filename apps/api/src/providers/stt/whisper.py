"""Whisper STT - Local, free, offline."""

import asyncio
import tempfile
import os
from typing import AsyncGenerator, Optional
from ...core.interfaces import STTProvider
from ...config import get_settings


class WhisperSTT(STTProvider):
    def __init__(self):
        self.model_size = get_settings().whisper_model_size
        self._model = None

    def _load(self):
        if not self._model:
            import whisper
            self._model = whisper.load_model(self.model_size)
        return self._model

    async def transcribe_stream(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[str, None]:
        buffer = b""
        async for chunk in audio_stream:
            buffer += chunk
            if len(buffer) >= 32000:
                text = await self.transcribe_buffer(buffer)
                buffer = b""
                if text.strip():
                    yield text
        if buffer:
            text = await self.transcribe_buffer(buffer)
            if text.strip():
                yield text

    async def transcribe_buffer(self, audio_bytes: bytes, language: Optional[str] = None) -> str:
        model = self._load()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            path = f.name
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: model.transcribe(path, language=language, fp16=False))
            return result.get("text", "").strip()
        finally:
            os.unlink(path)

    async def detect_language(self, audio_bytes: bytes) -> str:
        model = self._load()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            path = f.name
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: model.transcribe(path, fp16=False))
            return result.get("language", "en")
        finally:
            os.unlink(path)
