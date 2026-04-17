from __future__ import annotations

from typing import Any


def build_prompt(
    state: str,
    emotion: str,
    risk: str,
    tone: str,
    memory: dict[str, Any],
    retrieved_context: list[dict[str, Any]],
    history: list[dict[str, str]],
    follow_up_question: str,
) -> tuple[str, str]:
    history_text = "\n".join(f"{item['role']}: {item['content']}" for item in history[-6:])
    memory_text = (
        f"Habits: {', '.join(memory['habits']) or 'none'}\n"
        f"Issues: {', '.join(memory['common_issues']) or 'none'}\n"
        f"Personality: {', '.join(memory['personality']) or 'none'}\n"
        f"Preferred solutions: {', '.join(memory['preferred_solutions']) or 'none'}\n"
        f"Rejected solutions: {', '.join(memory['rejected_solutions']) or 'none'}"
    )
    rag_text = "\n".join(
        f"- {item.get('name', 'General')} | category={item.get('category', 'general')} | score={item.get('score', 0):.2f}"
        for item in retrieved_context
    )
    system_prompt = f"""
You are MindLex, a safe AI life assistant.
Rules:
- Never diagnose or give medication advice.
- If risk is HIGH, prioritize immediate crisis support.
- Keep responses to 3-4 short sentences maximum.
- Express one idea only.
- Give one micro-action only.
- Ask exactly one follow-up question.
- Avoid repetition and avoid reusing rejected solutions.
- Tone should be {tone}.
- Conversation stage is {state}; emotion is {emotion}; risk is {risk}.
""".strip()
    user_prompt = f"""
USER MEMORY
{memory_text}

RETRIEVED CONTEXT
{rag_text or "- none"}

RECENT HISTORY
{history_text or "No prior history."}

Please answer the user in a supportive, concise way and end with this exact follow-up question if it fits naturally:
{follow_up_question}
""".strip()
    return system_prompt, user_prompt
