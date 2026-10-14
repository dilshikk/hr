"""2FA: секреты TOTP и коды восстановления

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-14
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

TZ = sa.DateTime(timezone=True)


def upgrade() -> None:
    op.create_table(
        "user_totp",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("secret_enc", sa.String(255), nullable=False),
        sa.Column("confirmed", sa.Boolean(), nullable=False),
        sa.Column("last_step", sa.Integer(), nullable=False),
        sa.Column("created_at", TZ, nullable=False),
    )
    op.create_index("ix_user_totp_user_id", "user_totp", ["user_id"], unique=True)

    op.create_table(
        "recovery_codes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("code_hash", sa.String(64), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False),
        sa.Column("created_at", TZ, nullable=False),
    )
    op.create_index("ix_recovery_codes_user_id", "recovery_codes", ["user_id"])
    op.create_index("ix_recovery_codes_code_hash", "recovery_codes", ["code_hash"])


def downgrade() -> None:
    for table in ("recovery_codes", "user_totp"):
        op.drop_table(table)
