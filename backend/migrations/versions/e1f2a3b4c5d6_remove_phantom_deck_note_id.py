"""remove phantom deck concept (decks.note_id)

Revision ID: e1f2a3b4c5d6
Revises: d9a4c5e6b7f8
Create Date: 2026-06-15 00:20:00.000000

Suppression de la fonctionnalité de "deck fantôme" : plus aucune flashcard n'est
créée automatiquement depuis une note. On retire la colonne decks.note_id.

Non destructif : les decks fantômes existants (note_id renseigné) sont DÉTACHÉS
et conservés comme decks normaux ; on retire simplement le préfixe "[Phantom]
Note: " de leur nom. Les cartes déjà générées sont préservées.

Additif et idempotent.
"""
from alembic import op
import sqlalchemy as sa


revision = 'e1f2a3b4c5d6'
down_revision = 'd9a4c5e6b7f8'
branch_labels = None
depends_on = None

_PREFIX = "[Phantom] Note: "


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "decks" not in set(inspector.get_table_names()):
        return
    deck_cols = {c["name"] for c in inspector.get_columns("decks")}
    if "note_id" not in deck_cols:
        return  # déjà migré

    # 1. Détacher : retirer le préfixe "[Phantom] Note: " des decks fantômes.
    rows = bind.execute(
        sa.text("SELECT id, name FROM decks WHERE note_id IS NOT NULL")
    ).fetchall()
    for row in rows:
        name = row.name or ""
        if name.startswith(_PREFIX):
            bind.execute(
                sa.text("UPDATE decks SET name = :n WHERE id = :i"),
                {"n": name[len(_PREFIX):] or "Deck", "i": row.id},
            )

    # 2. Supprimer la colonne (batch -> compatible SQLite ET PostgreSQL ; la FK
    #    dépendante est retirée automatiquement par le drop de colonne).
    with op.batch_alter_table("decks", schema=None) as batch_op:
        batch_op.drop_column("note_id")


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "decks" not in set(inspector.get_table_names()):
        return
    deck_cols = {c["name"] for c in inspector.get_columns("decks")}
    if "note_id" in deck_cols:
        return
    with op.batch_alter_table("decks", schema=None) as batch_op:
        batch_op.add_column(sa.Column("note_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_decks_note_id_notes", "notes", ["note_id"], ["id"], ondelete="CASCADE"
        )
