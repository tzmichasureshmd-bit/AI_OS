"""Deepgram STT - Real-time streaming, ~300ms latency."""

import httpx
import json
import asyncio
import websockets
from typing import AsyncGenerator, Optional
from ...core.interfaces import STTProvider
from ...config import get_settings


class DeepgramSTT(STTProvider):
    def __init__(self):
        s = get_settings()
        self.api_key = s.deepgram_api_key
        self.model = s.deepgram_stt_model

    async def transcribe_stream(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[str, None]:
        params = f"?model={self.model}&smart_format=true&interim_results=true&endpointing=300&utterance_end_ms=1000"
        headers = {"Authorization": f"Token {self.api_key}"}

        try:
            async with websockets.connect(f"wss://api.deepgram.com/v1/listen{params}", extra_headers=headers) as ws:
                async def send():
                    async for chunk in audio_stream:
                        if chunk:
                            await ws.send(chunk)
                    await ws.send(json.dumps({"type": "CloseStream"}))

                task = asyncio.create_task(send())
                try:
                    async for msg in ws:
                        data = json.loads(msg)
                        if data.get("type") == "Results":
                            alt = data.get("channel", {}).get("alternatives", [])
                            if alt:
                                text = alt[0].get("transcript", "").strip()
                                if text and data.get("is_final"):
                                    yield text
                except websockets.exceptions.ConnectionClosed:
                    pass
                finally:
                    task.cancel()
        except Exception as e:
            yield f"[STT_ERROR: {e}]"

    async def transcribe_buffer(self, audio_bytes: bytes, language: Optional[str] = None) -> str:
        params = {"model": self.model, "smart_format": "true"}
        if language:
            params["language"] = language
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://api.deepgram.com/v1/listen",
                headers={"Authorization": f"Token {self.api_key}", "Content-Type": "audio/wav"},
                params=params, content=audio_bytes, timeout=15.0,
            )
            if r.status_code == 200:
                return r.json().get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
        return ""

    async def detect_language(self, audio_bytes: bytes) -> str:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://api.deepgram.com/v1/listen",
                headers={"Authorization": f"Token {self.api_key}", "Content-Type": "audio/wav"},
                params={"model": self.model, "detect_language": "true"},
                content=audio_bytes, timeout=10.0,
            )
            if r.status_code == 200:
                return r.json().get("results", {}).get("channels", [{}])[0].get("detected_language", "en")
        return "en"
