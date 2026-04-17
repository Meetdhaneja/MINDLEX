from __future__ import annotations


def micro_action_for_emotion(emotion: str) -> str:
    actions = {
        "sadness": "Write down one kind thing you need right now.",
        "anxiety": "Take 3 slow breaths and relax your shoulders once.",
        "anger": "Step away for 2 minutes and unclench your jaw and hands.",
        "fear": "Name 3 things you can see and 2 things you can feel.",
    }
    return actions.get(emotion, "Write one sentence about what feels heaviest right now.")


def run_cbt_flow(user_input: str, memory: dict, emotion: str, state: str) -> dict[str, str]:
    last_topic = memory.get("last_topics", [None])[0]
    issue_hint = last_topic or "this situation"
    emotion_hint = emotion if emotion and emotion != "neutral" else "this feeling"

    return {
        "step_1_identify_emotion": f"Help the user name the strongest emotion connected to {issue_hint}.",
        "step_2_identify_negative_thought": f"Ask what thought or belief appears when {emotion_hint} shows up.",
        "step_3_challenge_thought": "Gently question whether the thought is fully true, fully permanent, or the only explanation.",
        "step_4_alternative_thought": "Offer a more balanced, compassionate alternative thought.",
        "step_5_small_action": micro_action_for_emotion(emotion),
        "state_focus": state,
    }
