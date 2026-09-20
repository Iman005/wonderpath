"""user password hash + trip notes and packing lists

Revision ID: f1a9b3c4d567
Revises: e8f2b0c7a351
Create Date: 2026-08-22 23:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "f1a9b3c4d567"
down_revision = "e8f2b0c7a351"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("password_hash", sa.String(length=255), nullable=True))
    op.create_table(
        "trip_notes",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("trip_id", sa.String(length=36), sa.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False),
        sa.Column("trip_day_id", sa.String(length=36), sa.ForeignKey("trip_days.id", ondelete="CASCADE"), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "packing_lists",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("trip_id", sa.String(length=36), sa.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False),
        sa.Column("trip_day_id", sa.String(length=36), sa.ForeignKey("trip_days.id", ondelete="CASCADE"), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "packing_items",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "packing_list_id",
            sa.String(length=36),
            sa.ForeignKey("packing_lists.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("label", sa.String(length=200), nullable=False),
        sa.Column("is_checked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("packing_items")
    op.drop_table("packing_lists")
    op.drop_table("trip_notes")
    op.drop_column("users", "password_hash")
