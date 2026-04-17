from __future__ import annotations

import random
from typing import Any

# Standard recommendation pools
EMOTION_RECOMMENDATIONS = {
    "sadness": [
        "Write down what’s bothering you",
        "Do one small, easy activity",
        "Listen to supportive music",
        "Reach out to someone you trust",
    ],
    "anxiety": [
        "Take 3 slow breaths for 1 minute",
        "Try the 5-4-3-2-1 grounding technique",
        "Take a short walk or break",
        "Drink a glass of cold water",
    ],
    "anger": [
        "Step away for a minute",
        "Take a physical pause and stretch",
        "Write your angry feelings down, then tear it up",
        "Do some intense short exercise",
    ],
    "neutral": [
        "Take a 5-minute break from screens",
        "Do a quick mindfulness body scan",
        "Stretch your shoulders and neck",
        "Plan something small you enjoy",
    ],
}

RISK_RECOMMENDATIONS = {
    "HIGH": [
        "Call or text a crisis helpline immediately",
        "Speak to a trusted friend or family member now",
        "Go to a safe environment",
    ],
    "MEDIUM": [
        "Schedule time with a professional therapist",
        "Review your personal coping plan",
        "Avoid making major decisions right now",
    ],
    "LOW": [
        "Maintain a healthy sleep schedule",
        "Try adding a bit of daily movement",
        "Keep a daily emotional journal",
    ],
}


def generate_recommendations(
    history_len: int, state: str, emotion: str, risk: str, memory: dict[str, Any]
) -> list[str]:
    """
    Produce personalized recommendations based on the user's current situation.
    Triggered if conversation >= 3 messages OR state is coping/closing.
    """
    # 1. Trigger conditions
    if history_len < 3 and state not in ["coping", "closing"] and "help" not in state:
        return []

    # 2. Collect recommendations
    recommendations = set()

    # Priority 1: High Risk Overrides
    r_level = (risk or "LOW").upper()
    if r_level == "HIGH":
        for rec in RISK_RECOMMENDATIONS["HIGH"]:
            recommendations.add(rec)
        return list(recommendations)[:4]

    # Priority 2: Emotion based
    e_lower = emotion.lower()
    base_pool = EMOTION_RECOMMENDATIONS.get(e_lower, EMOTION_RECOMMENDATIONS["neutral"])
    
    # Priority 3: Risk based
    risk_pool = RISK_RECOMMENDATIONS.get(r_level, RISK_RECOMMENDATIONS["LOW"])

    # Priority 4: Memory targeted
    if memory and memory.get("recurring_themes"):
        themes = memory.get("recurring_themes", [])
        if "sleep" in themes:
            recommendations.add("Set a strict screen-time cutoff before bed")
        if "work" in themes:
            recommendations.add("Block out 15 minutes of quiet time at work")

    # Sample and Combine (Ensure max 4)
    sel_emotion = random.sample(base_pool, min(2, len(base_pool)))
    sel_risk = random.sample(risk_pool, min(1, len(risk_pool)))

    for rec in sel_emotion + sel_risk:
        recommendations.add(rec)

    # Return exactly list of strings (max 4)
    return list(recommendations)[:4]
