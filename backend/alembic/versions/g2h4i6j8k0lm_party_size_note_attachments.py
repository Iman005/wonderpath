"""party_size, guest_count, note_attachments

Revision ID: g2h4i6j8k0lm
Revises: f1a9b3c4d567
Create Date: 2026-08-25 00:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "g2h4i6j8k0lm"
down_revision = "f1a9b3c4d567"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("trip_places", sa.Column("party_size", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("trip_stays", sa.Column("guest_count", sa.Integer(), nullable=False, server_default="1"))
    op.create_table(
        "note_attachments",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "note_id",
            sa.String(length=36),
            sa.ForeignKey("trip_notes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("mime", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_note_attachments_note_id", "note_attachments", ["note_id"])


def downgrade() -> None:
    op.drop_index("ix_note_attachments_note_id", table_name="note_attachments")
    op.drop_table("note_attachments")
    op.drop_column("trip_stays", "guest_count")
    op.drop_column("trip_places", "party_size")
