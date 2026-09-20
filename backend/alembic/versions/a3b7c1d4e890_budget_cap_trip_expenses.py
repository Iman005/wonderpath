"""budget_cap on trips and trip_expenses table

Revision ID: a3b7c1d4e890
Revises: 9f1c4e8a2b10
Create Date: 2026-08-18 00:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "a3b7c1d4e890"
down_revision = "9f1c4e8a2b10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("trips", sa.Column("budget_cap", sa.Float(), nullable=True))
    op.execute(sa.text("UPDATE trips SET budget_cap = budget_ceiling WHERE budget_cap IS NULL"))

    op.create_table(
        "trip_expenses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("trip_id", sa.String(length=36), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trip_expenses_trip_id"), "trip_expenses", ["trip_id"], unique=False)
    op.execute(
        sa.text(
            """
            INSERT INTO trip_expenses (id, trip_id, label, amount, created_at)
            SELECT id, trip_id, label, amount, created_at FROM trip_side_expenses
            """
        )
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_trip_expenses_trip_id"), table_name="trip_expenses")
    op.drop_table("trip_expenses")
    op.drop_column("trips", "budget_cap")
