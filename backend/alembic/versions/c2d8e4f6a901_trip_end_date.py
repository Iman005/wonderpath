"""trip end_date for calendar range

Revision ID: c2d8e4f6a901
Revises: f1a9b3c4d567
Create Date: 2026-08-23 12:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "c2d8e4f6a901"
down_revision = "f1a9b3c4d567"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("trips", sa.Column("end_date", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("trips", "end_date")
