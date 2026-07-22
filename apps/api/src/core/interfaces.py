"""
Provider Interfaces - All providers implement these.
Swap any provider without touching business logic.
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional


class STTProvider(ABC):
    @abstractmethod
    async def transcribe_stream(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[str, None]: ...

    @abstractmethod
    async def transcribe_buffer(self, audio_bytes: bytes, language: Optional[str] = None) -> str: ...

    @abstractmethod
    async def detect_language(self, audio_bytes: bytes) -> str: ...


class TTSProvider(ABC):
    @abstractmethod
    async def synthesize_stream(self, text: str, language: str = "en", voice_id: Optional[str] = None) -> AsyncGenerator[bytes, None]: ...

    @abstractmethod
    async def synthesize(self, text: str, language: str = "en", voice_id: Optional[str] = None) -> bytes: ...

    @abstractmethod
    def get_supported_voices(self) -> list[dict]: ...


class LLMProvider(ABC):
    @abstractmethod
    async def generate_stream(self, messages: list[dict], system_prompt: str, temperature: float = 0.7, max_tokens: int = 150) -> AsyncGenerator[str, None]: ...

    @abstractmethod
    async def generate(self, messages: list[dict], system_prompt: str, temperature: float = 0.7, max_tokens: int = 150) -> str: ...
