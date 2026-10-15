"""Найм: вакансии, кандидаты, история этапов, календарь интервью."""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, utcnow


class Vacancy(Base, TimestampMixin):
    __tablename__ = "vacancies"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(16), default="draft")
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)


class Candidate(Base, TimestampMixin):
    __tablename__ = "candidates"
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, index=True, nullable=True)
    full_name: Mapped[str] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(32), index=True, nullable=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    vacancy_id: Mapped[int | None] = mapped_column(ForeignKey("vacancies.id"), nullable=True)
    stage: Mapped[str] = mapped_column(String(24), default="new", index=True)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    events: Mapped[list["PipelineEvent"]] = relationship(back_populates="candidate")


class PipelineEvent(Base):
    """История переходов: кто, когда, откуда, куда, почему."""
    __tablename__ = "pipeline_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), index=True)
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    from_stage: Mapped[str] = mapped_column(String(24))
    to_stage: Mapped[str] = mapped_column(String(24))
    reason: Mapped[str] = mapped_column(String(300), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    candidate: Mapped[Candidate] = relationship(back_populates="events")


class ScheduledInterview(Base):
    """Назначенное интервью с оценкой. Отдельно от опросов в боте (InterviewSession)."""
    __tablename__ = "scheduled_interviews"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), index=True)
    # Филиал копируется с кандидата, чтобы изоляцию проверять без лишних запросов.
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    interviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    duration_min: Mapped[int] = mapped_column(default=30)
    format: Mapped[str] = mapped_column(String(16), default="offline")
    status: Mapped[str] = mapped_column(String(16), default="scheduled", index=True)
    score: Mapped[int | None] = mapped_column(nullable=True)
    comment: Mapped[str] = mapped_column(String(500), default="")
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
