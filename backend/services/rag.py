from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import faiss
from sentence_transformers import SentenceTransformer


class RagService:
    def __init__(self, data_path: Path, embedding_model_name: str) -> None:
        self._data_path = data_path
        self._embedding_model_name = embedding_model_name
        self._records: list[dict[str, Any]] = []
        self._chunks: list[str] = []
        self._model: SentenceTransformer | None = None
        self._index = None

    def load(self) -> None:
        if self._index is not None:
            return
        with self._data_path.open("r", encoding="utf-8") as handle:
            self._records = json.load(handle)
        self._chunks = [self._chunkify(item) for item in self._records]
        self._model = SentenceTransformer(self._embedding_model_name)
        matrix = self._model.encode(self._chunks, convert_to_numpy=True, normalize_embeddings=True).astype("float32")
        self._index = faiss.IndexFlatIP(matrix.shape[1])
        self._index.add(matrix)

    def retrieve(self, query: str, top_k: int) -> list[dict[str, Any]]:
        self.load()
        if self._model is None or self._index is None:
            return []
        vector = self._model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
        scores, indices = self._index.search(vector, top_k)
        results = []
        for idx, score in zip(indices[0], scores[0]):
            if int(idx) < 0 or int(idx) >= len(self._records):
                continue
            row = self._records[int(idx)]
            results.append(
                {
                    "name": row.get("name", "DSM context"),
                    "category": row.get("category", "general"),
                    "code": row.get("code", ""),
                    "summary": row.get("duration", ""),
                    "keywords": row.get("keywords", []),
                    "score": float(score),
                }
            )
        return results

    @staticmethod
    def _chunkify(record: dict[str, Any]) -> str:
        criteria = record.get("criteria", {}) if isinstance(record.get("criteria"), dict) else {}
        symptoms = record.get("symptoms", [])
        symptom_text = ", ".join(
            item.get("text", str(item)) if isinstance(item, dict) else str(item)
            for item in symptoms
        )
        return (
            f"{record.get('name', 'Unknown')} | {record.get('category', 'general')} | "
            f"{criteria.get('A', '')} | {criteria.get('B', '')} | {criteria.get('C', '')} | "
            f"{symptom_text} | {', '.join(record.get('keywords', []))}"
        )
