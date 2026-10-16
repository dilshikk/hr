"""Найм: вакансии, кандидаты, история этапов, календарь интервью, документы."""
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
    # Напоминание «связаться с кандидатом»: получает ответственный (или сотрудники филиала).
    next_contact_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    next_contact_note: Mapped[str] = mapped_column(String(300), default="")
    reminder_sent: Mapped[bool] = mapped_column(default=False)
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
    # Напоминание интервьюеру за час до начала отправляется один раз.
    reminder_sent: Mapped[bool] = mapped_column(default=False)


class CandidateDocument(Base):
    """Метаданные загруженного файла. Сам файл лежит на диске под случайным именем stored_name."""
    __tablename__ = "candidate_documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), index=True)
    filename: Mapped[str] = mapped_column(String(200))
    content_type: Mapped[str] = mapped_column(String(64))
    size_bytes: Mapped[int] = mapped_column()
    sha256: Mapped[str] = mapped_column(String(64))
    stored_name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    uploaded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
