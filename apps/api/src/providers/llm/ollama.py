"""Ollama LLM - Local, free, no API key needed."""

import httpx
import json
from typing import AsyncGenerator
from ...core.interfaces import LLMProvider
from ...config import get_settings


class OllamaLLM(LLMProvider):
    def __init__(self):
        s = get_settings()
        self.base_url = s.ollama_base_url
        self.model = s.ollama_model

    async def generate_stream(self, messages: list[dict], system_prompt: str, temperature: float = 0.7, max_tokens: int = 150) -> AsyncGenerator[str, None]:
        all_msgs = [{"role": "system", "content": system_prompt}] + messages
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST", f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": all_msgs, "stream": True, "options": {"temperature": temperature, "num_predict": max_tokens}},
                timeout=60.0,
            ) as r:
                async for line in r.aiter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            content = chunk.get("message", {}).get("content", "")
                            if content:
                                yield content
                            if chunk.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue

    async def generate(self, messages: list[dict], system_prompt: str, temperature: float = 0.7, max_tokens: int = 150) -> str:
        all_msgs = [{"role": "system", "content": system_prompt}] + messages
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": all_msgs, "stream": False, "options": {"temperature": temperature, "num_predict": max_tokens}},
                timeout=60.0,
            )
            if r.status_code == 200:
                return r.json().get("message", {}).get("content", "")
            return "[Ollama Error - is it running?]"
