from __future__ import annotations


STATES = ["greeting", "exploration", "insight", "coping", "closing"]


def resolve_state(current_state: str | None, risk_level: str, message_count: int) -> tuple[str, str]:
    if risk_level == "HIGH":
        return "crisis", "crisis"

    current = current_state or "greeting"
    if current not in STATES:
        current = "greeting"

    if current == "greeting" and message_count >= 1:
        return current, "exploration"
    if current == "exploration" and message_count >= 3:
        return current, "insight"
    if current == "insight" and message_count >= 5:
        return current, "coping"
    if current == "coping" and message_count >= 7:
        return current, "closing"
    return current, current
