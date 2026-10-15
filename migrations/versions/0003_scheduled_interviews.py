"""Календарь интервью

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-15
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

TZ = sa.DateTime(timezone=True)


def upgrade() -> None:
    op.create_table(
        "scheduled_interviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("candidates.id"), nullable=False),
        sa.Column("branch_id", sa.Integer(), sa.ForeignKey("branches.id"), nullable=False),
        sa.Column("interviewer_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("starts_at", TZ, nullable=False),
        sa.Column("duration_min", sa.Integer(), nullable=False),
        sa.Column("format", sa.String(16), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("comment", sa.String(500), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", TZ, nullable=False),
    )
    for column in ("candidate_id", "branch_id", "interviewer_id", "starts_at", "status"):
        op.create_index(f"ix_scheduled_interviews_{column}", "scheduled_interviews", [column])


def downgrade() -> None:
    op.drop_table("scheduled_interviews")
