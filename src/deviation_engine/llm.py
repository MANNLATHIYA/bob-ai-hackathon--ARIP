from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod

import httpx


class LLMClient(ABC):
    @abstractmethod
    async def complete_json(self, system: str, prompt: str) -> dict: ...


class DisabledLLM(LLMClient):
    async def complete_json(self, system: str, prompt: str) -> dict:
        return {"is_deviation": False, "confidence": 0, "reason": "LLM disabled"}


class OpenAICompatibleLLM(LLMClient):
    def __init__(self) -> None:
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.key = os.environ["LLM_API_KEY"]
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")

    async def complete_json(self, system: str, prompt: str) -> dict:
        payload = {"model": self.model, "response_format": {"type": "json_object"}, "messages": [
            {"role": "system", "content": system}, {"role": "user", "content": prompt}
        ], "temperature": 0}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(f"{self.base_url}/chat/completions", headers={"Authorization": f"Bearer {self.key}"}, json=payload)
            response.raise_for_status()
            return json.loads(response.json()["choices"][0]["message"]["content"])


class AnthropicLLM(LLMClient):
    def __init__(self) -> None:
        self.key = os.environ["LLM_API_KEY"]
        self.model = os.getenv("LLM_MODEL", "claude-3-5-haiku-latest")

    async def complete_json(self, system: str, prompt: str) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post("https://api.anthropic.com/v1/messages", headers={
                "x-api-key": self.key, "anthropic-version": "2023-06-01", "content-type": "application/json"
            }, json={"model": self.model, "max_tokens": 700, "temperature": 0, "system": system,
                     "messages": [{"role": "user", "content": prompt + "\nReturn JSON only."}]})
            response.raise_for_status()
            text = response.json()["content"][0]["text"]
            return json.loads(text[text.find("{"):text.rfind("}") + 1])


def get_llm() -> LLMClient:
    if not os.getenv("LLM_API_KEY"):
        return DisabledLLM()
    return AnthropicLLM() if os.getenv("LLM_PROVIDER", "openai").lower() == "anthropic" else OpenAICompatibleLLM()

