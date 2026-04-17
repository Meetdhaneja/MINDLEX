from __future__ import annotations


def build_routine(habits: list[str], emotion: str, motivation_level: str) -> dict[str, object]:
    tasks: list[dict[str, str]] = []
    if "sleeping late" in habits:
        tasks.append({"title": "Set a soft shutdown time", "timing": "Tonight", "reason": "A calmer evening helps reset sleep pressure."})
    if "skipping meals" in habits:
        tasks.append({"title": "Eat one easy meal", "timing": "Next 2 hours", "reason": "Steadier energy helps emotional regulation."})
    if emotion == "anxiety":
        tasks.append({"title": "Start with one low-stakes task", "timing": "This morning", "reason": "Early momentum can lower anticipatory stress."})
    if emotion == "sadness":
        tasks.append({"title": "Get light and movement", "timing": "Before noon", "reason": "Light activity can reduce emotional heaviness."})
    if motivation_level == "low":
        tasks.append({"title": "Keep the bar tiny", "timing": "All day", "reason": "Small wins are more sustainable than ideal plans."})

    defaults = [
        {"title": "Drink water and check posture", "timing": "Now", "reason": "Physical reset supports focus."},
        {"title": "Protect one 20-minute focus block", "timing": "Today", "reason": "A clear block helps create traction."},
        {"title": "Do a gentle evening review", "timing": "Tonight", "reason": "Reflection helps the system adapt tomorrow."},
    ]
    for task in defaults:
        if len(tasks) >= 5:
            break
        if task["title"] not in {existing["title"] for existing in tasks}:
            tasks.append(task)
    return {
        "summary": "Since your recent pattern suggests a lighter day is better, this routine keeps the load realistic and steady.",
        "tasks": tasks[:5],
    }
