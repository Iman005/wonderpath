"""share_token on trips for public read-only snapshots

Revision ID: i4j6k8l0m2no
Revises: h3i5j7k9l0mn
Create Date: 2026-08-26
"""
from alembic import op
import sqlalchemy as sa


revision = "i4j6k8l0m2no"
down_revision = "h3i5j7k9l0mn"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("trips", sa.Column("share_token", sa.String(length=64), nullable=True))
    op.create_index("ix_trips_share_token", "trips", ["share_token"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_trips_share_token", table_name="trips")
    op.drop_column("trips", "share_token")
