from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseModel):
    app_name: str = "MindLex AI Life Assistant"
    app_version: str = "3.0.0"
    environment: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    database_url: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./psychat.db"))
    groq_api_key: str | None = Field(default_factory=lambda: os.getenv("GROQ_API_KEY"))
    redis_url: str = Field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    lm_studio_url: str = Field(default_factory=lambda: os.getenv("LM_STUDIO_URL", "http://127.0.0.1:1234"))
    lm_studio_model: str = Field(default_factory=lambda: os.getenv("LM_STUDIO_MODEL", "nvidia/nemotron-3-nano-4b"))
    dsm_data_path: Path = Field(default_factory=lambda: Path(os.getenv("DSM_DATA_PATH", BASE_DIR / "data" / "dsm_top50_clean.json")))
    embedding_model_name: str = Field(default_factory=lambda: os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"))
    emotion_model_name: str = Field(default_factory=lambda: os.getenv("EMOTION_MODEL_NAME", "j-hartmann/emotion-english-distilroberta-base"))
    cors_origins: list[str] = Field(
        default_factory=lambda: [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",") if origin.strip()]
    )
    max_history_messages: int = Field(default_factory=lambda: int(os.getenv("MAX_HISTORY_MESSAGES", "8")))
    rag_top_k: int = Field(default_factory=lambda: int(os.getenv("RAG_TOP_K", "3")))
    recommendation_trigger_min: int = Field(default_factory=lambda: int(os.getenv("RECOMMENDATION_TRIGGER_MIN", "3")))
    llm_temperature: float = Field(default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.35")))
    llm_max_tokens: int = Field(default_factory=lambda: int(os.getenv("LLM_MAX_TOKENS", "180")))
    response_sentence_limit: int = Field(default_factory=lambda: int(os.getenv("RESPONSE_SENTENCE_LIMIT", "4")))
    cache_ttl_seconds: int = Field(default_factory=lambda: int(os.getenv("CACHE_TTL_SECONDS", "900")))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
