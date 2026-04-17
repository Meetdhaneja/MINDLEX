from __future__ import annotations

from dataclasses import dataclass


HIGH_RISK_TERMS = [
    "suicide",
    "kill myself",
    "self harm",
    "hurt myself",
    "end my life",
    "no reason to live",
]
MEDIUM_RISK_TERMS = [
    "can't cope",
    "breakdown",
    "worthless",
    "hopeless",
    "not safe",
    "spiraling",
]


@dataclass
class RiskResult:
    level: str
    score: float
    emergency_override: bool


def assess_risk(message: str, emotion: str) -> RiskResult:
    text = message.lower()
    if any(term in text for term in HIGH_RISK_TERMS):
        return RiskResult(level="HIGH", score=0.95, emergency_override=True)
    if any(term in text for term in MEDIUM_RISK_TERMS) or emotion in {"sadness", "anger"}:
        return RiskResult(level="MEDIUM", score=0.58, emergency_override=False)
    return RiskResult(level="LOW", score=0.21, emergency_override=False)


def crisis_message() -> str:
    return (
        "I’m really glad you said this out loud. If you might act on these thoughts, call emergency services now or "
        "reach the 988 Suicide & Crisis Lifeline immediately, and stay near a trusted person. Can you tell me if "
        "you are in immediate danger right now?"
    )
