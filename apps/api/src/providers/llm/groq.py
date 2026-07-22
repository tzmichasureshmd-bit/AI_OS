"""Groq LLM - Fastest inference (~100ms). Free tier."""

import httpx
import json
from typing import AsyncGenerator
from ...core.interfaces import LLMProvider
from ...config import get_settings


class GroqLLM(LLMProvider):
    def __init__(self):
        s = get_settings()
        self.api_key = s.groq_api_key
        self.model = s.groq_model

    async def generate_stream(self, messages: list[dict], system_prompt: str, temperature: float = 0.7, max_tokens: int = 150) -> AsyncGenerator[str, None]:
        all_msgs = [{"role": "system", "content": system_prompt}] + messages
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST", "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": self.model, "messages": all_msgs, "temperature": temperature, "max_tokens": max_tokens, "stream": True},
                timeout=30.0,
            ) as r:
                if r.status_code == 200:
                    async for line in r.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                content = chunk["choices"][0].get("delta", {}).get("content", "")
                                if content:
                                    yield content
                            except (json.JSONDecodeError, KeyError, IndexError):
                                continue

    async def generate(self, messages: list[dict], system_prompt: str, temperature: float = 0.7, max_tokens: int = 150) -> str:
        all_msgs = [{"role": "system", "content": system_prompt}] + messages
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": self.model, "messages": all_msgs, "temperature": temperature, "max_tokens": max_tokens},
                timeout=30.0,
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            return f"[LLM Error: {r.status_code}]"
