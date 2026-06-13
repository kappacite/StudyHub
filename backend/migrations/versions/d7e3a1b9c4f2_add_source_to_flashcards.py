"""add source to flashcards

Revision ID: d7e3a1b9c4f2
Revises: 2ac3bf658f47
Create Date: 2026-06-13 17:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7e3a1b9c4f2'
down_revision = '2ac3bf658f47'
branch_labels = None
depends_on = None


def upgrade():
    # Colonne NOT NULL sur table existante : server_default='manual' backfill les
    # lignes existantes (cartes issues des balises / créées par l'utilisateur).
    with op.batch_alter_table('flashcards', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'source',
                sa.String(length=10),
                server_default='manual',
                nullable=False,
            )
        )


def downgrade():
    with op.batch_alter_table('flashcards', schema=None) as batch_op:
        batch_op.drop_column('source')
