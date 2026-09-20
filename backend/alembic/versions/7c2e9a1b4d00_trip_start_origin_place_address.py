"""trip start_date, origin, and place address

Revision ID: 7c2e9a1b4d00
Revises: 4d89afd10b43
Create Date: 2026-08-13 13:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "7c2e9a1b4d00"
down_revision = "4d89afd10b43"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("trips", sa.Column("start_date", sa.DateTime(), nullable=True))
    op.add_column("trips", sa.Column("origin_latitude", sa.Float(), nullable=True))
    op.add_column("trips", sa.Column("origin_longitude", sa.Float(), nullable=True))
    op.add_column("trips", sa.Column("origin_label", sa.String(length=200), nullable=True))
    op.add_column("places", sa.Column("address", sa.String(length=400), nullable=True))


def downgrade() -> None:
    op.drop_column("places", "address")
    op.drop_column("trips", "origin_label")
    op.drop_column("trips", "origin_longitude")
    op.drop_column("trips", "origin_latitude")
    op.drop_column("trips", "start_date")
