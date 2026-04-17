from __future__ import annotations


CRISIS_STATE = "crisis_mode"
CONVERSATION_STATES = [
    "greeting",
    "exploration",
    "emotion_identification",
    "problem_identification",
    "insight",
    "coping",
    "reflection",
    "closing",
]

STATE_ORDER = {
    "greeting": "exploration",
    "exploration": "emotion_identification",
    "emotion_identification": "problem_identification",
    "problem_identification": "insight",
    "insight": "coping",
    "coping": "reflection",
    "reflection": "closing",
    "closing": "exploration",
}


def get_active_state(stored_state: str | None, risk_level: str) -> str:
    if risk_level == "HIGH":
        return CRISIS_STATE
    if stored_state == CRISIS_STATE:
        return "reflection"
    return stored_state or "greeting"


def get_next_state(active_state: str, risk_level: str) -> str:
    if risk_level == "HIGH":
        return CRISIS_STATE
    return STATE_ORDER.get(active_state, "exploration")


def adaptive_tone(emotion: str) -> str:
    mapping = {
        "sadness": "Use a gentle, slower, supportive tone.",
        "anxiety": "Use a calming tone with grounding and reassurance.",
        "anger": "Use a validating, steady, de-escalating tone.",
        "fear": "Use a calm, stabilizing tone and reduce overwhelm.",
    }
    return mapping.get(emotion, "Use a warm, human, conversational tone.")


def generate_follow_up_question(state: str, emotion: str, memory: dict) -> str:
    topic_hint = memory.get("last_topics", [])
    recurring_hint = memory.get("recurring_issues", [])
    emotion_hint = memory.get("past_emotions", [])

    if state == "greeting":
        return "How are you feeling today?"
    if state == "exploration":
        if topic_hint:
            return f"Do you want to share a little more about {topic_hint[0]} and what happened today?"
        return "Do you want to share what happened?"
    if state == "emotion_identification":
        if emotion and emotion != "neutral":
            return f"Would you say the strongest feeling right now is still {emotion}, or has it shifted a bit?"
        return "Are you feeling more sad, anxious, angry, or overwhelmed?"
    if state == "problem_identification":
        if recurring_hint:
            return f"What do you think is driving this, especially around {recurring_hint[0]}?"
        return "What do you think is causing this most right now?"
    if state == "insight":
        return "When this feeling shows up, what thought usually comes with it?"
    if state == "coping":
        return "What feels most realistic for you to try in the next few minutes?"
    if state == "reflection":
        if emotion_hint:
            return f"When you compare this to earlier moments like {emotion_hint[0]}, what feels different now?"
        return "What stands out to you from this conversation so far?"
    if state == "closing":
        return "Would you like to check in again later about how this goes?"
    return "Would you like to keep exploring this together?"
