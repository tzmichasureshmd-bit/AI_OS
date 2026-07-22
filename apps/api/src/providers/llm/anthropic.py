"""Anthropic Claude LLM - Great instruction following."""

import httpx
import json
from typing import AsyncGenerator
from ...core.interfaces import LLMProvider
from ...config import get_settings


class AnthropicLLM(LLMProvider):
    def __init__(self):
        s = get_settings()
        self.api_key = s.anthropic_api_key
        self.model = s.anthropic_model

    async def generate_stream(self, messages: list[dict], system_prompt: str, temperature: float = 0.7, max_tokens: int = 150) -> AsyncGenerator[str, None]:
        user_msgs = [m for m in messages if m["role"] != "system"]
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST", "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
                json={"model": self.model, "system": system_prompt, "messages": user_msgs, "max_tokens": max_tokens, "temperature": temperature, "stream": True},
                timeout=30.0,
            ) as r:
                async for line in r.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            event = json.loads(line[6:])
                            if event.get("type") == "content_block_delta":
                                text = event.get("delta", {}).get("text", "")
                                if text:
                                    yield text
                        except json.JSONDecodeError:
                            continue

    async def generate(self, messages: list[dict], system_prompt: str, temperature: float = 0.7, max_tokens: int = 150) -> str:
        user_msgs = [m for m in messages if m["role"] != "system"]
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
                json={"model": self.model, "system": system_prompt, "messages": user_msgs, "max_tokens": max_tokens, "temperature": temperature},
                timeout=30.0,
            )
            if r.status_code == 200:
                content = r.json().get("content", [])
                return content[0].get("text", "") if content else ""
            return f"[Anthropic Error: {r.status_code}]"
