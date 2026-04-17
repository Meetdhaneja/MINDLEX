from __future__ import annotations

import hashlib
import json
from typing import Any

try:
    import redis
except Exception:  # pragma: no cover
    redis = None


class CacheService:
    def __init__(self, redis_url: str, ttl_seconds: int) -> None:
        self._ttl_seconds = ttl_seconds
        self._fallback: dict[str, str] = {}
        self._client = None
        if redis is not None:
            try:
                self._client = redis.Redis.from_url(redis_url, decode_responses=True)
                self._client.ping()
            except Exception:
                self._client = None

    @staticmethod
    def make_key(prefix: str, *parts: str) -> str:
        raw = "::".join([prefix, *parts])
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return f"{prefix}:{digest}"

    def get_json(self, key: str) -> dict[str, Any] | None:
        value = self._client.get(key) if self._client is not None else self._fallback.get(key)
        if not value:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None

    def set_json(self, key: str, value: dict[str, Any]) -> None:
        raw = json.dumps(value, ensure_ascii=True)
        if self._client is not None:
            self._client.setex(key, self._ttl_seconds, raw)
        else:
            self._fallback[key] = raw
