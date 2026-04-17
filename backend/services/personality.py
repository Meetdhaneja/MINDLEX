from __future__ import annotations


def infer_personality_traits(message: str, known_traits: list[str]) -> list[str]:
    text = message.lower()
    traits = list(known_traits)
    detected = []
    if any(token in text for token in ["overthink", "panic", "worried", "stress"]):
        detected.append("anxious")
    if any(token in text for token in ["just tell me", "be direct", "quick answer"]):
        detected.append("direct")
    if any(token in text for token in ["quiet", "keep to myself", "alone", "withdraw"]):
        detected.append("introvert")
    for trait in detected:
        if trait not in traits:
            traits.append(trait)
    return traits


def tone_guide(traits: list[str], emotion: str) -> str:
    if "direct" in traits:
        return "concise, grounded, practical"
    if "anxious" in traits or emotion == "anxiety":
        return "calm, reassuring, steady"
    if "introvert" in traits:
        return "soft, thoughtful, low-pressure"
    return "warm, clear, supportive"
