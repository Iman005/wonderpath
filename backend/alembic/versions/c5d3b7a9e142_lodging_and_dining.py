"""place kind, traveler count, trip_stays

Revision ID: c5d3b7a9e142
Revises: b8e2f4a1c903
Create Date: 2026-08-21 20:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "c5d3b7a9e142"
down_revision = "b8e2f4a1c903"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Every place cached before this migration is an attraction, so backfill
    # with a server default and only then make the column NOT NULL.
    op.add_column(
        "places",
        sa.Column("kind", sa.String(length=20), nullable=False, server_default="attraction"),
    )
    op.create_index("ix_places_kind", "places", ["kind"])

    op.add_column(
        "trips",
        sa.Column("traveler_count", sa.Integer(), nullable=False, server_default="1"),
    )

    op.create_table(
        "trip_stays",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("trip_id", sa.String(length=36), nullable=False),
        sa.Column("place_id", sa.String(length=36), nullable=False),
        sa.Column("check_in_day_number", sa.Integer(), nullable=False),
        sa.Column("nights", sa.Integer(), nullable=False),
        sa.Column("nightly_rate", sa.Float(), nullable=True),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["place_id"], ["places.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trip_stays_trip_id", "trip_stays", ["trip_id"])


def downgrade() -> None:
    op.drop_index("ix_trip_stays_trip_id", table_name="trip_stays")
    op.drop_table("trip_stays")
    op.drop_column("trips", "traveler_count")
    op.drop_index("ix_places_kind", table_name="places")
    op.drop_column("places", "kind")
