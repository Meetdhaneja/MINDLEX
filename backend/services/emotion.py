from __future__ import annotations

from dataclasses import dataclass

from transformers import pipeline


EMOTION_MAP = {
    "sadness": "sadness",
    "fear": "anxiety",
    "anger": "anger",
    "joy": "neutral",
    "neutral": "neutral",
    "disgust": "anger",
    "surprise": "anxiety",
}


@dataclass
class EmotionResult:
    label: str
    confidence: float


class EmotionService:
    def __init__(self, model_name: str) -> None:
        self._model_name = model_name
        self._classifier = None

    def load(self) -> None:
        if self._classifier is None:
            self._classifier = pipeline("text-classification", model=self._model_name, top_k=None)

    def detect(self, message: str) -> EmotionResult:
        heuristic = self._heuristic_detect(message)
        try:
            self.load()
            result = self._classifier(message, truncation=True)[0]
            top = max(result, key=lambda item: float(item.get("score", 0)))
            label = EMOTION_MAP.get(str(top.get("label", "")).lower(), "neutral")
            return EmotionResult(label=label, confidence=float(top.get("score", 0.6)))
        except Exception:
            return heuristic

    @staticmethod
    def _heuristic_detect(message: str) -> EmotionResult:
        text = message.lower()
        if any(token in text for token in ["panic", "anxious", "worried", "overthinking", "nervous"]):
            return EmotionResult(label="anxiety", confidence=0.64)
        if any(token in text for token in ["angry", "furious", "irritated", "annoyed"]):
            return EmotionResult(label="anger", confidence=0.62)
        if any(token in text for token in ["sad", "lonely", "empty", "crying", "hopeless"]):
            return EmotionResult(label="sadness", confidence=0.68)
        return EmotionResult(label="neutral", confidence=0.55)
