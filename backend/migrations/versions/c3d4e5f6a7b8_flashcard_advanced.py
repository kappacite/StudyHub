"""flashcard advanced (A1) : mode inversé + tuning par carte/deck

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-06-15 16:00:00.000000

Ajoute le mode inversé (D7) et le fine-tuning SM-2 (D4) côté flashcards :
- decks.reversed (Bool), decks.tuning_default (Float)
- flashcards.tuning (Float), flashcards.reverse_of_id (Integer, miroir verso→recto)

Additif et idempotent (guard `inspector`), compatible SQLite et PostgreSQL.
"""
from alembic import op
import sqlalchemy as sa


revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "decks" in tables:
        cols = {c["name"] for c in inspector.get_columns("decks")}
        with op.batch_alter_table("decks", schema=None) as batch_op:
            if "reversed" not in cols:
                batch_op.add_column(sa.Column("reversed", sa.Boolean(), server_default="0", nullable=False))
            if "tuning_default" not in cols:
                batch_op.add_column(sa.Column("tuning_default", sa.Float(), server_default="1.0", nullable=False))

    if "flashcards" in tables:
        cols = {c["name"] for c in inspector.get_columns("flashcards")}
        with op.batch_alter_table("flashcards", schema=None) as batch_op:
            if "tuning" not in cols:
                batch_op.add_column(sa.Column("tuning", sa.Float(), server_default="1.0", nullable=False))
            if "reverse_of_id" not in cols:
                batch_op.add_column(sa.Column("reverse_of_id", sa.Integer(), nullable=True))
        existing_idx = {i["name"] for i in inspector.get_indexes("flashcards")}
        if "ix_flashcards_reverse_of_id" not in existing_idx:
            op.create_index("ix_flashcards_reverse_of_id", "flashcards", ["reverse_of_id"])


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "flashcards" in tables:
        existing_idx = {i["name"] for i in inspector.get_indexes("flashcards")}
        if "ix_flashcards_reverse_of_id" in existing_idx:
            op.drop_index("ix_flashcards_reverse_of_id", table_name="flashcards")
        cols = {c["name"] for c in inspector.get_columns("flashcards")}
        with op.batch_alter_table("flashcards", schema=None) as batch_op:
            if "reverse_of_id" in cols:
                batch_op.drop_column("reverse_of_id")
            if "tuning" in cols:
                batch_op.drop_column("tuning")

    if "decks" in tables:
        cols = {c["name"] for c in inspector.get_columns("decks")}
        with op.batch_alter_table("decks", schema=None) as batch_op:
            if "tuning_default" in cols:
                batch_op.drop_column("tuning_default")
            if "reversed" in cols:
                batch_op.drop_column("reversed")
