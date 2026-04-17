from __future__ import annotations

import json

from .conversation_engine import adaptive_tone, generate_follow_up_question


SAFETY_RULES = """You are an AI mental health, psychiatrist assistant.
- Never diagnose or prescribe. Provide non-clinical guidance.
- Safety > Accuracy > Helpfulness.
- Keep answers SHORT (max 3-4 sentences, max 80-120 words).
- Be meaningful but concise.
- Give ONE small actionable suggestion.
- Ask ONE follow-up question.
- Avoid long explanations and detailed educational text.
- Give NO multi-step plans. Only ONE easy micro-solution."""


def build_prompt(
    *,
    state: str,
    emotion: str,
    risk: str,
    memory: dict,
    context: list[dict],
    history: list[dict],
    user_input: str,
    cbt_flow: dict,
) -> tuple[str, str]:
    follow_up_question = generate_follow_up_question(state, emotion, memory)
    dsm_context = "\n\n".join(
        [
            (
                f"{item['name']} ({item['code']}) | {item['category']}\n"
                f"Criteria A: {item.get('criteria', {}).get('A', 'Not specified')}\n"
                f"Criteria B: {item.get('criteria', {}).get('B', 'Not specified')}\n"
                f"Criteria C: {item.get('criteria', {}).get('C', 'Not specified')}\n"
                f"Duration: {item.get('duration', 'Not specified')}\n"
                f"Keywords: {', '.join(item.get('keywords', []))}"
            )
            for item in context
        ]
    )
    recent_history = json.dumps(history[-10:], ensure_ascii=True)
    memory_text = json.dumps(memory, ensure_ascii=True)
    cbt_text = json.dumps(cbt_flow, ensure_ascii=True)

    user_prompt = f"""Current conversation stage: {state}
Detected emotion: {emotion}
Risk level: {risk}
Tone guidance: {adaptive_tone(emotion)}

Structured user memory:
{memory_text}

Recent messages:
{recent_history}

Relevant DSM educational context:
{dsm_context}

CBT flow guidance:
{cbt_text}

Current user input:
{user_input}

Emotion adaptation rules:
- sadness -> soft, supportive
- anxiety -> calming, grounding
- anger -> validating, de-escalating

Build a response that follows this MANDATORY structure:
1. Empathy (1 short sentence)
2. Insight (1 short sentence)
3. Micro-solution (1 actionable, tiny suggestion like "take 3 slow breaths")
4. Follow-up question (Just one question to continue the conversation)

Additional constraints:
- Keep the reply warm, human, and strictly concise.
- Do NOT give multiple solutions or over-explain DSM concepts.
- End with this or a very similar short follow-up question: "{follow_up_question}"
"""
    return SAFETY_RULES, user_prompt
