from __future__ import annotations

import re

import httpx


class LLMService:
    def __init__(self, base_url: str, model: str, temperature: float, max_tokens: int, sentence_limit: int) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._sentence_limit = sentence_limit

    async def generate(self, system_prompt: str, user_prompt: str, history: list[dict[str, str]]) -> str:
        body = {
            "model": self._model,
            "messages": [{"role": "system", "content": system_prompt}, *history[-6:], {"role": "user", "content": user_prompt}],
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{self._base_url}/v1/chat/completions", json=body)
            response.raise_for_status()
            payload = response.json()
        content = payload.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return self._compress(content)

    def _compress(self, content: str) -> str:
        if not content:
            return "I’m here with you. Let’s take one small step and keep this simple. What feels most important to steady first?"
        sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", content) if part.strip()]
        return " ".join(sentences[: self._sentence_limit])
