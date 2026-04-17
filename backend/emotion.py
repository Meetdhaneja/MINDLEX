from __future__ import annotations

import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from transformers import pipeline


logger = logging.getLogger(__name__)

load_dotenv()

EMOTION_MODEL_NAME = "j-hartmann/emotion-english-distilroberta-base"
DEFAULT_EMOTION = "neutral"


@dataclass
class EmotionResult:
    label: str
    confidence: float


class EmotionAnalyzer:
    def __init__(self) -> None:
        self._classifier = None
        self._load_error = None

    def load(self) -> None:
        if self._classifier:
            return

        token = os.getenv("HF_TOKEN")
        try:
            self._classifier = pipeline(
                "text-classification",
                model=EMOTION_MODEL_NAME,
                token=token,
                top_k=None,
            )
        except Exception as exc:  # pragma: no cover
            self._load_error = exc
            logger.warning("Emotion model unavailable, falling back to neutral: %s", exc)

    def detect(self, text: str) -> EmotionResult:
        self.load()
        if not self._classifier:
            return EmotionResult(label=DEFAULT_EMOTION, confidence=0.0)

        try:
            predictions = self._classifier(text, truncation=True)
            if predictions and isinstance(predictions[0], list):
                predictions = predictions[0]
            best = max(predictions, key=lambda item: item["score"])
            return EmotionResult(label=best["label"].lower(), confidence=float(best["score"]))
        except Exception as exc:  # pragma: no cover
            logger.warning("Emotion detection failed, falling back to neutral: %s", exc)
            return EmotionResult(label=DEFAULT_EMOTION, confidence=0.0)


emotion_analyzer = EmotionAnalyzer()
