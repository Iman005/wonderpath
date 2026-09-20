"""place details_json for demo catalogs

Revision ID: d4e8a1c6f270
Revises: c5d3b7a9e142
Create Date: 2026-08-22 10:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "d4e8a1c6f270"
down_revision = "c5d3b7a9e142"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("places", sa.Column("details_json", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("places", "details_json")
