"""Начальная схема: HR-платформа и данные старого бота

Revision ID: 0001
Revises:
Create Date: 2026-10-14
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

TZ = sa.DateTime(timezone=True)


def upgrade() -> None:
    op.create_table(
        "branches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
        sa.Column("created_at", TZ, nullable=False),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("branch_id", sa.Integer(), sa.ForeignKey("branches.id"), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", TZ, nullable=False),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)

    op.create_table(
        "vacancies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("branch_id", sa.Integer(), sa.ForeignKey("branches.id"), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", TZ, nullable=False),
    )
    op.create_index("ix_vacancies_branch_id", "vacancies", ["branch_id"])

    op.create_table(
        "candidates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=True),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("branch_id", sa.Integer(), sa.ForeignKey("branches.id"), nullable=False),
        sa.Column("vacancy_id", sa.Integer(), sa.ForeignKey("vacancies.id"), nullable=True),
        sa.Column("stage", sa.String(24), nullable=False),
        sa.Column("assignee_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("created_at", TZ, nullable=False),
    )
    op.create_index("ix_candidates_telegram_id", "candidates", ["telegram_id"])
    op.create_index("ix_candidates_phone", "candidates", ["phone"])
    op.create_index("ix_candidates_branch_id", "candidates", ["branch_id"])
    op.create_index("ix_candidates_stage", "candidates", ["stage"])

    op.create_table(
        "pipeline_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("candidates.id"), nullable=False),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("from_stage", sa.String(24), nullable=False),
        sa.Column("to_stage", sa.String(24), nullable=False),
        sa.Column("reason", sa.String(300), nullable=False),
        sa.Column("created_at", TZ, nullable=False),
    )
    op.create_index("ix_pipeline_events_candidate_id", "pipeline_events", ["candidate_id"])

    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", TZ, nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False),
        sa.Column("created_at", TZ, nullable=False),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])
    op.create_index("ix_auth_sessions_token_hash", "auth_sessions", ["token_hash"], unique=True)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("target", sa.String(64), nullable=False),
        sa.Column("created_at", TZ, nullable=False),
    )
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])

    # Данные старого бота
    op.create_table(
        "positions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name_ru", sa.String(100), nullable=False),
        sa.Column("name_uz", sa.String(100), nullable=False),
        sa.Column("emoji", sa.String(16), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", TZ, nullable=False),
    )
    op.create_table(
        "metro_stations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name_ru", sa.String(100), nullable=False),
        sa.Column("name_uz", sa.String(100), nullable=False),
        sa.Column("name_en", sa.String(100), nullable=True),
        sa.Column("line", sa.String(16), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_metro_stations_line", "metro_stations", ["line"])

    op.create_table(
        "bot_users",
        sa.Column("user_id", sa.BigInteger(), primary_key=True, autoincrement=False),
        sa.Column("username", sa.String(64), nullable=True),
        sa.Column("first_name", sa.String(200), nullable=True),
        sa.Column("lang", sa.String(4), nullable=False),
        sa.Column("created_at", TZ, nullable=False),
    )
    op.create_table(
        "blacklist",
        sa.Column("user_id", sa.BigInteger(), primary_key=True, autoincrement=False),
        sa.Column("blocked_at", TZ, nullable=False),
        sa.Column("unblock_at", TZ, nullable=True),
    )
    op.create_table(
        "interview_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("bot_users.user_id"), nullable=False),
        sa.Column("qa_log", sa.JSON(), nullable=False),
        sa.Column("q_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("report_resume", sa.JSON(), nullable=True),
        sa.Column("report_skills", sa.JSON(), nullable=True),
        sa.Column("report_personality", sa.JSON(), nullable=True),
    )
    op.create_index("ix_interview_sessions_user_id", "interview_sessions", ["user_id"])


def downgrade() -> None:
    # Порядок обратный созданию: сначала таблицы со ссылками.
    for table in (
        "interview_sessions", "blacklist", "bot_users", "metro_stations", "positions",
        "audit_logs", "auth_sessions", "pipeline_events", "candidates",
        "vacancies", "users", "branches",
    ):
        op.drop_table(table)
