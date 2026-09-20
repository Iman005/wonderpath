"""budget ceiling and trip side expenses

Revision ID: 9f1c4e8a2b10
Revises: 7c2e9a1b4d00
Create Date: 2026-08-17 15:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "9f1c4e8a2b10"
down_revision = "7c2e9a1b4d00"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("trips", sa.Column("budget_ceiling", sa.Float(), nullable=True))
    op.create_table(
        "trip_side_expenses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("trip_id", sa.String(length=36), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_trip_side_expenses_trip_id"),
        "trip_side_expenses",
        ["trip_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_trip_side_expenses_trip_id"), table_name="trip_side_expenses")
    op.drop_table("trip_side_expenses")
    op.drop_column("trips", "budget_ceiling")
