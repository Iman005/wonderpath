"""trip_stays.sort_index for mixed day itinerary

Revision ID: e8f2b0c7a351
Revises: d4e8a1c6f270
Create Date: 2026-08-22 14:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "e8f2b0c7a351"
down_revision = "d4e8a1c6f270"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "trip_stays",
        sa.Column("sort_index", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("trip_stays", "sort_index")
