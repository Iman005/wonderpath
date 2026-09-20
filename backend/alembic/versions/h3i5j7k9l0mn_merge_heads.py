"""merge trip_end_date and party_size branches

Revision ID: h3i5j7k9l0mn
Revises: c2d8e4f6a901, g2h4i6j8k0lm
Create Date: 2026-08-25
"""

from alembic import op  # noqa: F401

revision = "h3i5j7k9l0mn"
down_revision = ("c2d8e4f6a901", "g2h4i6j8k0lm")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
