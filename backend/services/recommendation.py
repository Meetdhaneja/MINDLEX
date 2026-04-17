from __future__ import annotations

from typing import Iterable


SOLUTION_POOL = {
    "sadness": [
        ("Reset the room", "Tidy one small surface for two minutes.", "Small order can lower emotional load."),
        ("Get daylight", "Step near a window or outside for five minutes.", "Light can help interrupt heavy momentum."),
        ("Name the feeling", "Write one sentence that starts with 'Right now I feel...'.", "Labeling can reduce overwhelm."),
    ],
    "anxiety": [
        ("Lower the pace", "Unclench your jaw and relax your shoulders once.", "Physical release can calm the loop."),
        ("Shrink the problem", "Choose the next five-minute task only.", "Narrowing focus reduces spiral thinking."),
        ("Ground with senses", "Name three things you can see.", "External focus can settle racing thoughts."),
    ],
    "anger": [
        ("Pause the reaction", "Take ten slow steps before replying to anyone.", "Movement can reduce intensity."),
        ("Cool the body", "Drink a glass of cold water.", "Body regulation helps emotions drop faster."),
        ("Contain the story", "Write one sentence about what crossed your boundary.", "Clarity helps anger feel usable."),
    ],
    "neutral": [
        ("Keep momentum", "Pick one easy win for the next 15 minutes.", "Simple structure protects energy."),
        ("Check your baseline", "Drink water now if you haven’t recently.", "Body basics matter before deeper work."),
        ("Protect attention", "Silence one distracting app for an hour.", "Fewer interruptions support consistency."),
    ],
}


def build_recommendations(
    emotion: str,
    preferred: Iterable[str],
    rejected: Iterable[str],
    recent: Iterable[str],
    enabled: bool,
) -> list[dict[str, str]]:
    if not enabled:
        return []

    rejected_set = {item.lower() for item in rejected}
    recent_set = {item.lower() for item in recent}
    preferred_set = {item.lower() for item in preferred}
    cards: list[dict[str, str]] = []
    pool = SOLUTION_POOL.get(emotion, SOLUTION_POOL["neutral"])
    ordered = sorted(pool, key=lambda item: item[0].lower() not in preferred_set)
    for title, action, reason in ordered:
        if title.lower() in rejected_set or title.lower() in recent_set:
            continue
        cards.append({"title": title, "action": action, "reason": reason})
        if len(cards) == 3:
            break
    return cards
