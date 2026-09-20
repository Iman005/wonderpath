"""users table for Google sign-in

Revision ID: b8e2f4a1c903
Revises: a3b7c1d4e890
Create Date: 2026-08-21 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b8e2f4a1c903"
down_revision = "a3b7c1d4e890"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("google_sub", sa.String(length=128), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("display_name", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("google_sub"),
    )


def downgrade() -> None:
    op.drop_table("users")
