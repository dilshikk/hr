"""initial schema"""
import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

TS = sa.DateTime(timezone=True)


def upgrade() -> None:
    op.create_table(
        "branches",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
        sa.Column("created_at", TS, nullable=False),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("telegram_id", sa.BigInteger, nullable=False, unique=True),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("branch_id", sa.Integer, sa.ForeignKey("branches.id")),
        sa.Column("is_active", sa.Boolean, nullable=False),
        sa.Column("created_at", TS, nullable=False),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"])
    op.create_table(
        "vacancies",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("branch_id", sa.Integer, sa.ForeignKey("branches.id"), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("owner_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("created_at", TS, nullable=False),
    )
    op.create_index("ix_vacancies_branch_id", "vacancies", ["branch_id"])
    op.create_table(
        "candidates",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("telegram_id", sa.BigInteger),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("phone", sa.String(32)),
        sa.Column("branch_id", sa.Integer, sa.ForeignKey("branches.id"), nullable=False),
        sa.Column("vacancy_id", sa.Integer, sa.ForeignKey("vacancies.id")),
        sa.Column("stage", sa.String(24), nullable=False),
        sa.Column("assignee_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("notes", sa.Text, nullable=False),
        sa.Column("created_at", TS, nullable=False),
    )
    for col in ("telegram_id", "phone", "branch_id", "stage"):
        op.create_index(f"ix_candidates_{col}", "candidates", [col])
    op.create_table(
        "pipeline_events",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("candidate_id", sa.Integer, sa.ForeignKey("candidates.id"), nullable=False),
        sa.Column("actor_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("from_stage", sa.String(24), nullable=False),
        sa.Column("to_stage", sa.String(24), nullable=False),
        sa.Column("reason", sa.String(300), nullable=False),
        sa.Column("created_at", TS, nullable=False),
    )
    op.create_index("ix_pipeline_events_candidate_id", "pipeline_events", ["candidate_id"])
    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", TS, nullable=False),
        sa.Column("revoked", sa.Boolean, nullable=False),
        sa.Column("created_at", TS, nullable=False),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])
    op.create_index("ix_auth_sessions_token_hash", "auth_sessions", ["token_hash"])
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("actor_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("target", sa.String(64), nullable=False),
        sa.Column("created_at", TS, nullable=False),
    )
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])


def downgrade() -> None:
    for t in ("audit_logs", "auth_sessions", "pipeline_events", "candidates", "vacancies", "users", "branches"):
        op.drop_table(t)
