"""add_fk_indexes_decks_notes_binders

Revision ID: da4b5645c877
Revises: ccdfa6ffc564
Create Date: 2026-06-13 03:19:31.115039

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'da4b5645c877'
down_revision = 'ccdfa6ffc564'
branch_labels = None
depends_on = None


def upgrade():
    # Index sur les clés étrangères de filtrage (PostgreSQL ne les crée pas
    # automatiquement). Noms alignés sur la convention `index=True` des modèles.
    op.create_index(op.f("ix_decks_user_id"), "decks", ["user_id"], unique=False)
    op.create_index(op.f("ix_decks_binder_id"), "decks", ["binder_id"], unique=False)
    op.create_index(op.f("ix_notes_user_id"), "notes", ["user_id"], unique=False)
    op.create_index(op.f("ix_notes_binder_id"), "notes", ["binder_id"], unique=False)
    op.create_index(op.f("ix_binders_user_id"), "binders", ["user_id"], unique=False)
    op.create_index(op.f("ix_binders_parent_id"), "binders", ["parent_id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_binders_parent_id"), table_name="binders")
    op.drop_index(op.f("ix_binders_user_id"), table_name="binders")
    op.drop_index(op.f("ix_notes_binder_id"), table_name="notes")
    op.drop_index(op.f("ix_notes_user_id"), table_name="notes")
    op.drop_index(op.f("ix_decks_binder_id"), table_name="decks")
    op.drop_index(op.f("ix_decks_user_id"), table_name="decks")
