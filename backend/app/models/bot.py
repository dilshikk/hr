"""Данные старого бота (mado_jbot): справочники, пользователи бота, чёрный список, интервью.

Названия таблиц совпадают со старой базой, где это возможно. Исключения:
- старая `users` (пользователи бота) -> `bot_users`, так как `users` уже занята сотрудниками;
- старая `vacancies` (справочник должностей) -> `positions`, так как `vacancies` уже занята вакансиями.
"""
from datetime import datetime

from sqlalchemy import JSON, BigInteger, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, utcnow


class Position(Base, TimestampMixin):
    """Справочник должностей для выбора кандидатом (старая таблица vacancies)."""
    __tablename__ = "positions"
    id: Mapped[int] = mapped_column(primary_key=True)
    name_ru: Mapped[str] = mapped_column(String(100))
    name_uz: Mapped[str] = mapped_column(String(100))
    emoji: Mapped[str] = mapped_column(String(16), default="")
    is_active: Mapped[bool] = mapped_column(default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


class MetroStation(Base):
    """Станции метро Ташкента для выбора района/места работы."""
    __tablename__ = "metro_stations"
    id: Mapped[int] = mapped_column(primary_key=True)
    name_ru: Mapped[str] = mapped_column(String(100))
    name_uz: Mapped[str] = mapped_column(String(100))
    name_en: Mapped[str | None] = mapped_column(String(100), nullable=True)
    line: Mapped[str] = mapped_column(String(16), index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(default=True)


class BotUser(Base, TimestampMixin):
    """Пользователь Telegram-бота (старая таблица users). Не путать с сотрудниками `users`."""
    __tablename__ = "bot_users"
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    lang: Mapped[str] = mapped_column(String(4), default="ru")


class BlacklistEntry(Base):
    """Заблокированные пользователи. unblock_at пуст — блокировка бессрочная."""
    __tablename__ = "blacklist"
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    blocked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    unblock_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class InterviewSession(Base):
    """AI-интервью в боте: вопросы-ответы и итоговый отчёт."""
    __tablename__ = "interview_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("bot_users.user_id"), index=True
    )
    # Кандидат HR-платформы, к которому относится опрос (автоматически по Telegram ID или вручную).
    candidate_id: Mapped[int | None] = mapped_column(ForeignKey("candidates.id"), index=True, nullable=True)
    qa_log: Mapped[list] = mapped_column(JSON, default=list)
    q_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="active")
    report_resume: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    report_skills: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    report_personality: Mapped[dict | None] = mapped_column(JSON, nullable=True)
