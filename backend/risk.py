from __future__ import annotations

from dataclasses import dataclass

from .emotion import EmotionResult


HIGH_RISK_KEYWORDS = {
    "suicide",
    "suicidal",
    "kill myself",
    "end my life",
    "want to die",
    "self harm",
    "hurt myself",
    "overdose",
    "can't go on",
}

MEDIUM_RISK_KEYWORDS = {
    "panic",
    "anxious",
    "anxiety",
    "terrified",
    "hopeless",
    "worthless",
    "alone",
    "overwhelmed",
    "depressed",
}

EMOTION_WEIGHTS = {
    "fear": 2,
    "sadness": 2,
    "anger": 1,
    "disgust": 1,
}


@dataclass
class RiskResult:
    level: str
    score: int
    emergency_override: bool


def assess_risk(text: str, emotion: EmotionResult) -> RiskResult:
    lowered = text.lower()

    keyword_score = 0
    if any(term in lowered for term in HIGH_RISK_KEYWORDS):
        keyword_score += 5
    elif any(term in lowered for term in MEDIUM_RISK_KEYWORDS):
        keyword_score += 2

    emotion_score = 0
    if emotion.confidence >= 0.45:
        emotion_score = EMOTION_WEIGHTS.get(emotion.label, 0)

    total = keyword_score + emotion_score

    if keyword_score >= 5 or total >= 5:
        return RiskResult(level="HIGH", score=total, emergency_override=True)
    if total >= 2:
        return RiskResult(level="MEDIUM", score=total, emergency_override=False)
    return RiskResult(level="LOW", score=total, emergency_override=False)


def emergency_message() -> str:
    return (
        "I am really glad you reached out. Your message suggests you may be at high risk right now. "
        "Please contact local emergency services or a crisis hotline immediately, and if possible tell a trusted "
        "person near you right away. If you are in the U.S. or Canada, call or text 988 now."
    )
