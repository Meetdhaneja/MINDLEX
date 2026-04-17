from __future__ import annotations

import re

import httpx


class LLMService:
    def __init__(self, base_url: str, api_key: str | None, model: str, temperature: float, max_tokens: int, sentence_limit: int) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._sentence_limit = sentence_limit

    async def generate(self, system_prompt: str, user_prompt: str, history: list[dict[str, str]]) -> str:
        headers = {}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        body = {
            "model": self._model,
            "messages": [{"role": "system", "content": system_prompt}, *history[-6:], {"role": "user", "content": user_prompt}],
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            full_url = self._base_url if self._base_url.endswith("/v1") else f"{self._base_url}/v1"
            response = await client.post(f"{full_url}/chat/completions", json=body, headers=headers)
            if response.is_error:
                error_detail = response.text
                raise httpx.HTTPStatusError(f"LLM Provider Error: {response.status_code} - {error_detail}", request=response.request, response=response)
            payload = response.json()
        content = payload.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return self._compress(content)

    def _compress(self, content: str) -> str:
        if not content:
            return "I’m here with you. Let’s take one small step and keep this simple. What feels most important to steady first?"
        sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", content) if part.strip()]
        return " ".join(sentences[: self._sentence_limit])
