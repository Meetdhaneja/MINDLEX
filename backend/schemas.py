from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=128)
    message: str = Field(..., min_length=1, max_length=4000)


class RecommendationCard(BaseModel):
    title: str
    action: str
    reason: str


class RoutineTask(BaseModel):
    title: str
    timing: str
    reason: str


class RoutinePlan(BaseModel):
    summary: str
    tasks: list[RoutineTask]


class DashboardCard(BaseModel):
    label: str
    value: str
    trend: str | None = None


class HistoryItem(BaseModel):
    id: int
    user_id: str
    role: str
    state: str
    content: str
    emotion: str | None = None
    risk: str | None = None
    created_at: datetime


class SessionItem(BaseModel):
    user_id: str
    name: str | None = None
    last_message: str
    timestamp: datetime


class SessionRenameRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)


class UserProfilePayload(BaseModel):
    habits: list[str]
    common_issues: list[str]
    personality: list[str]
    preferred_solutions: list[str]
    rejected_solutions: list[str]
    recent_suggestions: list[str]
    emotional_history: list[str]
    routine_history: list[str]
    goals: list[str]


class InsightPayload(BaseModel):
    patterns: list[str]
    trends: list[str]
    flags: list[str]


class ChatResponse(BaseModel):
    response: str
    emotion: str
    risk: str
    recommendations: list[RecommendationCard]
    routine: RoutinePlan
    state: str
    follow_up_question: str
    profile: UserProfilePayload
    insights: InsightPayload
    retrieved_context: list[dict[str, Any]]
    timestamp: datetime


class DashboardResponse(BaseModel):
    user_id: str
    cards: list[DashboardCard]
    profile: UserProfilePayload
    insights: InsightPayload
    recent_routine: RoutinePlan | None = None
    recent_emotions: list[str]
