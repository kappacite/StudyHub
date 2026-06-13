"""add_hidden_notes

Revision ID: 2ac3bf658f47
Revises: 50d9267a41a3
Create Date: 2026-06-13 15:54:47.570034

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ac3bf658f47'
down_revision = '50d9267a41a3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "hidden_notes",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("note_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["note_id"], ["notes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "note_id"),
    )


def downgrade():
    op.drop_table("hidden_notes")
