"""add card_type and payload to flashcards (typed revision items)

Revision ID: f2b3c4d5e6a7
Revises: e1f2a3b4c5d6
Create Date: 2026-06-15 12:00:00.000000

Cartes de révision typées : un jeu de révision (deck) peut désormais contenir,
en plus des cartes recto/verso ('basic'), des items 'qcm' | 'vf' | 'ordre' |
'assoc' dont le contenu structuré vit dans `payload`.

Additif et idempotent.
"""
from alembic import op
import sqlalchemy as sa


revision = 'f2b3c4d5e6a7'
down_revision = 'e1f2a3b4c5d6'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "flashcards" not in set(inspector.get_table_names()):
        return
    cols = {c["name"] for c in inspector.get_columns("flashcards")}
    with op.batch_alter_table("flashcards", schema=None) as batch_op:
        if "card_type" not in cols:
            batch_op.add_column(
                sa.Column(
                    "card_type",
                    sa.String(length=12),
                    nullable=False,
                    server_default="basic",
                )
            )
        if "payload" not in cols:
            batch_op.add_column(sa.Column("payload", sa.JSON(), nullable=True))


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "flashcards" not in set(inspector.get_table_names()):
        return
    cols = {c["name"] for c in inspector.get_columns("flashcards")}
    with op.batch_alter_table("flashcards", schema=None) as batch_op:
        if "payload" in cols:
            batch_op.drop_column("payload")
        if "card_type" in cols:
            batch_op.drop_column("card_type")
