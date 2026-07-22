"""OpenAI GPT LLM - High quality, paid."""

import httpx
import json
from typing import AsyncGenerator
from ...core.interfaces import LLMProvider
from ...config import get_settings


class OpenAILLM(LLMProvider):
    def __init__(self):
        s = get_settings()
        self.api_key = s.openai_api_key
        self.model = s.openai_model

    async def generate_stream(self, messages: list[dict], system_prompt: str, temperature: float = 0.7, max_tokens: int = 150) -> AsyncGenerator[str, None]:
        all_msgs = [{"role": "system", "content": system_prompt}] + messages
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST", "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": self.model, "messages": all_msgs, "temperature": temperature, "max_tokens": max_tokens, "stream": True},
                timeout=30.0,
            ) as r:
                async for line in r.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            content = json.loads(data)["choices"][0].get("delta", {}).get("content", "")
                            if content:
                                yield content
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue

    async def generate(self, messages: list[dict], system_prompt: str, temperature: float = 0.7, max_tokens: int = 150) -> str:
        all_msgs = [{"role": "system", "content": system_prompt}] + messages
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": self.model, "messages": all_msgs, "temperature": temperature, "max_tokens": max_tokens},
                timeout=30.0,
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            return f"[OpenAI Error: {r.status_code}]"
