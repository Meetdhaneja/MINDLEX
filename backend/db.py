from __future__ import annotations

import json
from contextlib import contextmanager
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from .config import get_settings


settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def json_list(values: list[str] | None = None) -> str:
    return json.dumps(values or [], ensure_ascii=True)


def parse_json_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [str(item) for item in parsed if str(item).strip()]
    except json.JSONDecodeError:
        return []
    return []


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    display_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    state: Mapped[str] = mapped_column(String(64), default="greeting", nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    emotion: Mapped[str | None] = mapped_column(String(64), nullable=True)
    risk: Mapped[str | None] = mapped_column(String(16), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)


class UserProfile(Base):
    __tablename__ = "user_profile"

    user_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    habits: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    common_issues: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    personality: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    preferred_solutions: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    rejected_solutions: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    recent_suggestions: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    emotional_history: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    routine_history: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    goals: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)


class ConversationState(Base):
    __tablename__ = "conversation_state"

    user_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    current_state: Mapped[str] = mapped_column(String(64), default="greeting", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)


class RoutineHistory(Base):
    __tablename__ = "routine_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    tasks: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)


class EmotionLog(Base):
    __tablename__ = "emotion_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    emotion: Mapped[str] = mapped_column(String(64), nullable=False)
    risk: Mapped[str] = mapped_column(String(16), nullable=False)
    score: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)


class UserInsight(Base):
    __tablename__ = "user_insights"

    user_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    patterns: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    trends: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    flags: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_or_create_user(session, user_id: str) -> User:
    user = session.get(User, user_id)
    if user is None:
        user = User(id=user_id)
        session.add(user)
        session.flush()
    return user


def get_or_create_profile(session, user_id: str) -> UserProfile:
    profile = session.get(UserProfile, user_id)
    if profile is None:
        profile = UserProfile(user_id=user_id)
        session.add(profile)
        session.flush()
    return profile


def get_or_create_state(session, user_id: str) -> ConversationState:
    state = session.get(ConversationState, user_id)
    if state is None:
        state = ConversationState(user_id=user_id)
        session.add(state)
        session.flush()
    return state


def get_or_create_insight(session, user_id: str) -> UserInsight:
    insight = session.get(UserInsight, user_id)
    if insight is None:
        insight = UserInsight(user_id=user_id)
        session.add(insight)
        session.flush()
    return insight


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
