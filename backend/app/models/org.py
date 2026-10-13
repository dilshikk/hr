"""Организация: филиалы и сотрудники системы."""
from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Branch(Base, TimestampMixin):
    __tablename__ = "branches"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)


class User(Base, TimestampMixin):
    """Сотрудник системы (HR, менеджер и т.д.). Роль — одна на MVP."""
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(200), default="")
    role: Mapped[str] = mapped_column(String(32), default="viewer")
    branch_id: Mapped[int | None] = mapped_column(ForeignKey("branches.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
