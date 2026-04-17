from __future__ import annotations


HABIT_PATTERNS = {
    "sleeping late": ["sleep late", "up late", "can't sleep", "insomnia"],
    "skipping meals": ["skip meals", "not eating", "forgot to eat"],
    "doomscrolling": ["scrolling", "doomscroll", "phone all night"],
    "isolating": ["alone", "isolating", "don't talk to anyone"],
}

ISSUE_PATTERNS = {
    "stress": ["stress", "stressed", "pressure"],
    "overthinking": ["overthink", "spiral", "racing thoughts"],
    "motivation dips": ["unmotivated", "no motivation", "burned out"],
    "low mood": ["sad", "empty", "down"],
}

PREFERENCE_PATTERNS = {
    "walking": ["walk helps", "like walking", "walk outside"],
    "journaling": ["journal", "writing helps"],
    "breathing exercise": ["breathing helps", "breathwork"],
    "music break": ["music helps", "listen to music"],
}

REJECTION_PATTERNS = {
    "meditation": ["hate meditation", "meditation doesn't help"],
    "journaling": ["don't like journaling", "journaling doesn't work"],
}

GOAL_PATTERNS = ["want to", "need to", "my goal", "trying to", "i hope to"]


def extract_memory_updates(message: str) -> dict[str, list[str]]:
    text = message.lower()
    habits = [label for label, phrases in HABIT_PATTERNS.items() if any(phrase in text for phrase in phrases)]
    issues = [label for label, phrases in ISSUE_PATTERNS.items() if any(phrase in text for phrase in phrases)]
    likes = [label for label, phrases in PREFERENCE_PATTERNS.items() if any(phrase in text for phrase in phrases)]
    dislikes = [label for label, phrases in REJECTION_PATTERNS.items() if any(phrase in text for phrase in phrases)]
    goals = [message.strip()[:120]] if any(phrase in text for phrase in GOAL_PATTERNS) else []
    return {
        "habits": habits,
        "common_issues": issues,
        "preferred_solutions": likes,
        "rejected_solutions": dislikes,
        "goals": goals,
    }
