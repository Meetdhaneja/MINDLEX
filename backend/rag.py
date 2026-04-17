from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


logger = logging.getLogger(__name__)

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DSM_DATA_PATH = Path(os.getenv("DSM_DATA_PATH", BASE_DIR / "data" / "dsm.json"))
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")


class RagEngine:
    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []
        self._chunks: list[str] = []
        self._model: SentenceTransformer | None = None
        self._index = None

    def load(self) -> None:
        if self._index is not None:
            return

        with DSM_DATA_PATH.open("r", encoding="utf-8") as handle:
            self._records = json.load(handle)

        self._chunks = [self._to_chunk(record) for record in self._records]
        self._model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        embeddings = self._model.encode(self._chunks, convert_to_numpy=True, normalize_embeddings=True)
        embeddings = embeddings.astype("float32")

        self._index = faiss.IndexFlatIP(embeddings.shape[1])
        self._index.add(embeddings)

    def retrieve(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        self.load()
        if not self._index or not self._model:
            return []
            
        try:
            query_vector = self._model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
            scores, indices = self._index.search(query_vector, top_k)
            results = []
            for idx, score in zip(indices[0], scores[0]):
                if idx < 0 or idx >= len(self._records):
                    continue
                record = self._records[int(idx)]
                results.append(
                    {
                        "name": record.get("name", "Unknown Disorder"),
                        "category": record.get("category", "General"),
                        "code": record.get("code", "N/A"),
                        "duration": record.get("duration", "Not specified"),
                        "risk_level": record.get("risk_level", "low"),
                        "criteria": record.get("criteria", {}),
                        "keywords": record.get("keywords", []),
                        "score": float(score),
                    }
                )
            return results
        except Exception as exc:
            logger.error(f"Retrieval error: {exc}")
            return []

    @staticmethod
    def _to_chunk(record: dict[str, Any]) -> str:
        # Robustly extract symptoms
        raw_symptoms = record.get("symptoms", [])
        if isinstance(raw_symptoms, list):
            symptom_texts = [
                s.get("text", str(s)) if isinstance(s, dict) else str(s)
                for s in raw_symptoms
            ]
        else:
            symptom_texts = []
        symptoms_str = ", ".join(symptom_texts) or "None listed"

        # Robustly extract criteria
        criteria = record.get("criteria", {})
        if not isinstance(criteria, dict):
            criteria = {}
            
        # Robustly extract keywords
        keywords = record.get("keywords", [])
        keywords_str = ", ".join(keywords) if isinstance(keywords, list) else ""

        return (
            f"Category: {record.get('category', 'N/A')}\n"
            f"Disorder: {record.get('name', 'Unknown')} ({record.get('code', 'N/A')})\n"
            f"Criteria A: {criteria.get('A', 'N/A')}\n"
            f"Criteria B: {criteria.get('B', 'N/A')}\n"
            f"Criteria C: {criteria.get('C', 'N/A')}\n"
            f"Symptoms: {symptoms_str}\n"
            f"Duration: {record.get('duration', 'N/A')}\n"
            f"Keywords: {keywords_str}\n"
            f"Risk level: {record.get('risk_level', 'unknown')}"
        )


rag_engine = RagEngine()
