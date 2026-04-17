from __future__ import annotations

from datetime import datetime, timezone

from .db import ConversationState, UserMemory, dumps_json_list, loads_json_list


ISSUE_KEYWORDS = {
    "exam stress": ["exam", "study", "grade", "college", "test"],
    "work stress": ["work", "job", "boss", "deadline", "office"],
    "relationship strain": ["relationship", "partner", "breakup", "girlfriend", "boyfriend"],
    "family stress": ["family", "parent", "mother", "father", "home"],
    "sleep difficulty": ["sleep", "insomnia", "awake", "tired", "rest"],
    "self-worth": ["worthless", "not good enough", "failure", "guilt"],
    "health worry": ["health", "illness", "symptom", "doctor"],
}


def get_or_create_state(session, user_id: str) -> ConversationState:
    state = session.get(ConversationState, user_id)
    if state is None:
        state = ConversationState(user_id=user_id, current_state="greeting")
        session.add(state)
        session.flush()
    return state


def get_or_create_memory(session, user_id: str) -> UserMemory:
    memory = session.get(UserMemory, user_id)
    if memory is None:
        memory = UserMemory(
            user_id=user_id,
            past_emotions="[]",
            recurring_issues="[]",
            last_topics="[]",
            risk_history="[]",
            updated_at=datetime.now(timezone.utc),
        )
        session.add(memory)
        session.flush()
    return memory


def memory_snapshot(memory: UserMemory) -> dict[str, list[str]]:
    return {
        "past_emotions": loads_json_list(memory.past_emotions),
        "recurring_issues": loads_json_list(memory.recurring_issues),
        "last_topics": loads_json_list(memory.last_topics),
        "risk_history": loads_json_list(memory.risk_history),
    }


def update_memory(memory: UserMemory, user_input: str, emotion: str, risk: str) -> dict[str, list[str]]:
    snapshot = memory_snapshot(memory)
    snapshot["past_emotions"] = _append_unique(snapshot["past_emotions"], emotion, limit=6)
    snapshot["risk_history"] = _append_unique(snapshot["risk_history"], risk, limit=10)

    lowered = user_input.lower()
    for issue_name, keywords in ISSUE_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            snapshot["recurring_issues"] = _append_unique(snapshot["recurring_issues"], issue_name, limit=6)
            snapshot["last_topics"] = _append_unique(snapshot["last_topics"], issue_name, limit=4)

    if not snapshot["last_topics"]:
        snapshot["last_topics"] = _append_unique(snapshot["last_topics"], "current stress", limit=4)

    memory.past_emotions = dumps_json_list(snapshot["past_emotions"])
    memory.recurring_issues = dumps_json_list(snapshot["recurring_issues"])
    memory.last_topics = dumps_json_list(snapshot["last_topics"])
    memory.risk_history = dumps_json_list(snapshot["risk_history"])
    memory.updated_at = datetime.now(timezone.utc)
    return snapshot


def _append_unique(values: list[str], new_value: str, limit: int) -> list[str]:
    clean = (new_value or "").strip()
    if not clean:
        return values[:limit]
    filtered = [item for item in values if item.lower() != clean.lower()]
    return [clean, *filtered][:limit]
