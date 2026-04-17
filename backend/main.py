from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .db import (
    EmotionLog,
    Message,
    RoutineHistory,
    User,
    UserProfile,
    ConversationState,
    UserInsight,
    get_or_create_insight,
    get_or_create_profile,
    get_or_create_state,
    get_or_create_user,
    get_session,
    init_db,
    json_list,
    parse_json_list,
)
from .schemas import (
    ChatRequest,
    ChatResponse,
    DashboardCard,
    DashboardResponse,
    HistoryItem,
    InsightPayload,
    RecommendationCard,
    RoutinePlan,
    RoutineTask,
    SessionItem,
    UserProfilePayload,
    SessionRenameRequest,
)
from .services.cache import CacheService
from .services.conversation import resolve_state
from .services.emotion import EmotionService
from .services.life_intelligence import build_insights
from .services.llm import LLMService
from .services.memory import extract_memory_updates
from .services.personality import infer_personality_traits, tone_guide
from .services.prompt_builder import build_prompt
from .services.rag import RagService
from .services.recommendation import build_recommendations
from .services.risk import assess_risk, crisis_message
from .services.routine import build_routine


settings = get_settings()
emotion_service = EmotionService(settings.emotion_model_name)
rag_service = RagService(settings.dsm_data_path, settings.embedding_model_name)
llm_service = LLMService(
    settings.lm_studio_url,
    settings.lm_studio_model,
    settings.llm_temperature,
    settings.llm_max_tokens,
    settings.response_sentence_limit,
)
cache_service = CacheService(settings.redis_url, settings.cache_ttl_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    try:
        rag_service.load()
    except Exception as exc:  # pragma: no cover
        print(f"RAG warmup skipped: {exc}")
    try:
        emotion_service.load()
    except Exception as exc:  # pragma: no cover
        print(f"Emotion warmup skipped: {exc}")
    yield


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    user_id = payload.user_id.strip()
    message = payload.message.strip()
    emotion = emotion_service.detect(message)
    risk = assess_risk(message, emotion.label)
    retrieved_context = rag_service.retrieve(message, settings.rag_top_k)
    timestamp = datetime.now(timezone.utc)

    with get_session() as session:
        user = get_or_create_user(session, user_id)
        profile = get_or_create_profile(session, user_id)
        state = get_or_create_state(session, user_id)
        insight = get_or_create_insight(session, user_id)

        history_rows = session.query(Message).filter(Message.user_id == user_id).order_by(Message.created_at.asc()).all()
        history = [{"role": row.role, "content": row.content} for row in history_rows][-settings.max_history_messages :]

        habits = parse_json_list(profile.habits)
        issues = parse_json_list(profile.common_issues)
        personality = parse_json_list(profile.personality)
        preferred_solutions = parse_json_list(profile.preferred_solutions)
        rejected_solutions = parse_json_list(profile.rejected_solutions)
        recent_suggestions = parse_json_list(profile.recent_suggestions)
        emotional_history = parse_json_list(profile.emotional_history)
        routine_history = parse_json_list(profile.routine_history)
        goals = parse_json_list(profile.goals)

        updates = extract_memory_updates(message)
        habits = _merge_unique(habits, updates["habits"])
        issues = _merge_unique(issues, updates["common_issues"])
        preferred_solutions = _merge_unique(preferred_solutions, updates["preferred_solutions"])
        rejected_solutions = _merge_unique(rejected_solutions, updates["rejected_solutions"])
        goals = _merge_unique(goals, updates["goals"])
        personality = infer_personality_traits(message, personality)
        emotional_history = _merge_unique(emotional_history[-9:], [emotion.label])

        current_state, next_state = resolve_state(state.current_state, risk.level, len(history_rows) // 2 + 1)
        follow_up_question = _follow_up_question(next_state, emotion.label)

        recommendations_raw = build_recommendations(
            emotion=emotion.label,
            preferred=preferred_solutions,
            rejected=rejected_solutions,
            recent=recent_suggestions,
            enabled=(len(history_rows) // 2) >= settings.recommendation_trigger_min,
        )
        recent_suggestions = _merge_unique(recent_suggestions[-5:], [card["title"] for card in recommendations_raw])

        motivation_level = "low" if any(issue in issues for issue in ["motivation dips", "low mood"]) else "steady"
        routine_raw = build_routine(habits, emotion.label, motivation_level)
        routine_history = _merge_unique(routine_history[-5:], [routine_raw["summary"]])
        insights_raw = build_insights(emotional_history, habits, issues)
        tone = tone_guide(personality, emotion.label)

        if risk.emergency_override:
            response_text = crisis_message()
        else:
            memory = {
                "habits": habits,
                "common_issues": issues,
                "personality": personality,
                "preferred_solutions": preferred_solutions,
                "rejected_solutions": rejected_solutions,
            }
            system_prompt, user_prompt = build_prompt(
                state=current_state,
                emotion=emotion.label,
                risk=risk.level,
                tone=tone,
                memory=memory,
                retrieved_context=retrieved_context,
                history=history,
                follow_up_question=follow_up_question,
            )
            cache_key = cache_service.make_key("chat", user_id, message, emotion.label, current_state)
            cached = cache_service.get_json(cache_key)
            if cached:
                response_text = cached["response"]
            else:
                try:
                    response_text = await llm_service.generate(system_prompt, user_prompt, history + [{"role": "user", "content": message}])
                except httpx.HTTPError as exc:
                    raise HTTPException(status_code=502, detail=f"LM Studio request failed: {exc}") from exc
                cache_service.set_json(cache_key, {"response": response_text})

        profile.habits = json_list(habits)
        profile.common_issues = json_list(issues)
        profile.personality = json_list(personality)
        profile.preferred_solutions = json_list(preferred_solutions)
        profile.rejected_solutions = json_list(rejected_solutions)
        profile.recent_suggestions = json_list(recent_suggestions)
        profile.emotional_history = json_list(emotional_history)
        profile.routine_history = json_list(routine_history)
        profile.goals = json_list(goals)
        profile.updated_at = timestamp

        state.current_state = next_state
        state.updated_at = timestamp

        insight.patterns = json_list(insights_raw["patterns"])
        insight.trends = json_list(insights_raw["trends"])
        insight.flags = json_list(insights_raw["flags"])
        insight.updated_at = timestamp

        session.add(Message(user_id=user_id, role="user", state=current_state, content=message, emotion=emotion.label, risk=risk.level))
        session.add(Message(user_id=user_id, role="assistant", state=current_state, content=response_text, emotion=emotion.label, risk=risk.level))
        session.add(EmotionLog(user_id=user_id, emotion=emotion.label, risk=risk.level, score=f"{risk.score:.2f}"))
        session.add(RoutineHistory(user_id=user_id, summary=routine_raw["summary"], tasks=json_list([task["title"] for task in routine_raw["tasks"]])))
        user.updated_at = timestamp

    return ChatResponse(
        response=response_text,
        emotion=emotion.label,
        risk=risk.level,
        recommendations=[RecommendationCard(**card) for card in recommendations_raw],
        routine=RoutinePlan(summary=routine_raw["summary"], tasks=[RoutineTask(**task) for task in routine_raw["tasks"]]),
        state=current_state,
        follow_up_question=follow_up_question,
        profile=UserProfilePayload(
            habits=habits,
            common_issues=issues,
            personality=personality,
            preferred_solutions=preferred_solutions,
            rejected_solutions=rejected_solutions,
            recent_suggestions=recent_suggestions,
            emotional_history=emotional_history,
            routine_history=routine_history,
            goals=goals,
        ),
        insights=InsightPayload(**insights_raw),
        retrieved_context=retrieved_context,
        timestamp=timestamp,
    )


@app.get("/history", response_model=list[HistoryItem])
def history(user_id: str = Query(..., min_length=1)) -> list[HistoryItem]:
    with get_session() as session:
        rows = session.query(Message).filter(Message.user_id == user_id).order_by(Message.created_at.asc()).all()
        return [
            HistoryItem(
                id=row.id,
                user_id=row.user_id,
                role=row.role,
                state=row.state,
                content=row.content,
                emotion=row.emotion,
                risk=row.risk,
                created_at=row.created_at,
            )
            for row in rows
        ]


@app.get("/sessions", response_model=list[SessionItem])
def sessions() -> list[SessionItem]:
    with get_session() as session:
        users = session.query(User).order_by(User.updated_at.desc()).all()
        items = []
        for user in users:
            last_message = session.query(Message).filter(Message.user_id == user.id).order_by(Message.created_at.desc()).first()
            if not last_message:
                continue
            items.append(
                SessionItem(
                    user_id=user.id,
                    name=user.display_name,
                    last_message=last_message.content[:70],
                    timestamp=last_message.created_at,
                )
            )
        return items


@app.patch("/sessions/{user_id}/rename")
def rename_session(user_id: str, payload: SessionRenameRequest):
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.display_name = payload.name
        session.add(user)
        return {"status": "ok", "name": payload.name}


@app.delete("/sessions/{user_id}")
def delete_session(user_id: str):
    with get_session() as session:
        session.query(Message).filter(Message.user_id == user_id).delete()
        session.query(EmotionLog).filter(EmotionLog.user_id == user_id).delete()
        session.query(RoutineHistory).filter(RoutineHistory.user_id == user_id).delete()
        session.query(UserProfile).filter(UserProfile.user_id == user_id).delete()
        session.query(ConversationState).filter(ConversationState.user_id == user_id).delete()
        session.query(UserInsight).filter(UserInsight.user_id == user_id).delete()
        session.query(User).filter(User.id == user_id).delete()
        return {"status": "ok", "deleted_user_id": user_id}


@app.get("/dashboard", response_model=DashboardResponse)
def dashboard(user_id: str = Query(..., min_length=1)) -> DashboardResponse:
    with get_session() as session:
        profile = get_or_create_profile(session, user_id)
        insight = get_or_create_insight(session, user_id)
        last_routine = session.query(RoutineHistory).filter(RoutineHistory.user_id == user_id).order_by(RoutineHistory.created_at.desc()).first()
        emotions = session.query(EmotionLog).filter(EmotionLog.user_id == user_id).order_by(EmotionLog.created_at.desc()).limit(6).all()
        cards = [
            DashboardCard(label="Habits tracked", value=str(len(parse_json_list(profile.habits))), trend="Adaptive memory"),
            DashboardCard(label="Active goals", value=str(len(parse_json_list(profile.goals))), trend="Micro-task ready"),
            DashboardCard(label="Recent emotion", value=emotions[0].emotion if emotions else "neutral", trend="Live detection"),
            DashboardCard(label="Risk status", value=emotions[0].risk if emotions else "LOW", trend="Safety monitored"),
        ]
        recent_routine = None
        if last_routine:
            recent_routine = RoutinePlan(
                summary=last_routine.summary,
                tasks=[RoutineTask(title=task, timing="Planned", reason="Recently suggested routine task.") for task in parse_json_list(last_routine.tasks)],
            )
        return DashboardResponse(
            user_id=user_id,
            cards=cards,
            profile=UserProfilePayload(
                habits=parse_json_list(profile.habits),
                common_issues=parse_json_list(profile.common_issues),
                personality=parse_json_list(profile.personality),
                preferred_solutions=parse_json_list(profile.preferred_solutions),
                rejected_solutions=parse_json_list(profile.rejected_solutions),
                recent_suggestions=parse_json_list(profile.recent_suggestions),
                emotional_history=parse_json_list(profile.emotional_history),
                routine_history=parse_json_list(profile.routine_history),
                goals=parse_json_list(profile.goals),
            ),
            insights=InsightPayload(
                patterns=parse_json_list(insight.patterns),
                trends=parse_json_list(insight.trends),
                flags=parse_json_list(insight.flags),
            ),
            recent_routine=recent_routine,
            recent_emotions=[entry.emotion for entry in emotions],
        )


def _merge_unique(existing: list[str], additions: list[str]) -> list[str]:
    merged = list(existing)
    seen = {item.lower() for item in merged}
    for item in additions:
        if item and item.lower() not in seen:
            merged.append(item)
            seen.add(item.lower())
    return merged


def _follow_up_question(state: str, emotion: str) -> str:
    if state == "exploration":
        return "What part of this feels most active for you right now?"
    if state == "insight":
        return "When does this pattern usually show up most strongly?"
    if state == "coping":
        return "Which one tiny step feels easiest to try first?"
    if state == "closing":
        return "What would help you carry this steadiness into the next few hours?"
    if emotion == "anxiety":
        return "What would help your body feel five percent safer right now?"
    return "What feels most useful for us to focus on next?"
