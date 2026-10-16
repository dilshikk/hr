"""Напоминания, документы кандидатов, привязка опросов бота к кандидатам

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-16
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

TZ = sa.DateTime(timezone=True)


def upgrade() -> None:
    op.add_column("candidates", sa.Column("next_contact_at", TZ, nullable=True))
    op.add_column("candidates", sa.Column("next_contact_note", sa.String(300), nullable=False, server_default=""))
    op.add_column("candidates", sa.Column("reminder_sent", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_index("ix_candidates_next_contact_at", "candidates", ["next_contact_at"])

    op.add_column("scheduled_interviews", sa.Column("reminder_sent", sa.Boolean(), nullable=False, server_default=sa.false()))

    op.add_column("interview_sessions", sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("candidates.id"), nullable=True))
    op.create_index("ix_interview_sessions_candidate_id", "interview_sessions", ["candidate_id"])

    op.create_table(
        "candidate_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("candidates.id"), nullable=False),
        sa.Column("filename", sa.String(200), nullable=False),
        sa.Column("content_type", sa.String(64), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("stored_name", sa.String(64), nullable=False),
        sa.Column("uploaded_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", TZ, nullable=False),
    )
    op.create_index("ix_candidate_documents_candidate_id", "candidate_documents", ["candidate_id"])
    op.create_index("ix_candidate_documents_stored_name", "candidate_documents", ["stored_name"], unique=True)


def downgrade() -> None:
    op.drop_table("candidate_documents")
    op.drop_index("ix_interview_sessions_candidate_id", table_name="interview_sessions")
    op.drop_column("interview_sessions", "candidate_id")
    op.drop_column("scheduled_interviews", "reminder_sent")
    op.drop_index("ix_candidates_next_contact_at", table_name="candidates")
    op.drop_column("candidates", "reminder_sent")
    op.drop_column("candidates", "next_contact_note")
    op.drop_column("candidates", "next_contact_at")
