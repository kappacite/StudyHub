"""add_composite_perf_indexes

Revision ID: 50d9267a41a3
Revises: da4b5645c877
Create Date: 2026-06-13 03:21:11.142799

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '50d9267a41a3'
down_revision = 'da4b5645c877'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "ix_flashcards_deck_id_next_review",
        "flashcards",
        ["deck_id", "next_review"],
        unique=False,
    )
    op.create_index(
        "ix_study_sessions_user_id_created_at",
        "study_sessions",
        ["user_id", "created_at"],
        unique=False,
    )


def downgrade():
    op.drop_index("ix_study_sessions_user_id_created_at", table_name="study_sessions")
    op.drop_index("ix_flashcards_deck_id_next_review", table_name="flashcards")
