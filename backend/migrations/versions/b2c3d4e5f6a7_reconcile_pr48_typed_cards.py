"""reconcile PR #48 (D3c) : déplacer les cartes typées des decks vers les ensembles de révision

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-15 14:30:00.000000

La PR #48 avait introduit des cartes typées (card_type ∈ {qcm,vf,ordre,assoc} + payload)
dans les decks de flashcards. Décision D3c : un deck = flashcards recto/verso uniquement.
Cette migration transfère chaque carte non-`basic` vers un RevisionSet homogène
(un ensemble par couple deck/type) puis supprime la carte du deck. Les decks
redeviennent donc homogènes (flashcards `basic`).

Idempotente : après transfert il ne reste plus de carte non-`basic`, donc une
ré-exécution est sans effet. Compatible SQLite et PostgreSQL (types gérés par
SQLAlchemy core, dont le payload JSON).
"""
from alembic import op
import sqlalchemy as sa


revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


# Ancien card_type (PR #48) -> type d'ensemble de révision (D3c).
TYPE_MAP = {"qcm": "qcm", "vf": "vf", "ordre": "ordre", "assoc": "association"}
TYPE_LABELS = {"qcm": "QCM", "vf": "Vrai/Faux", "ordre": "Ordre", "assoc": "Association"}


def _tables(meta):
    decks = sa.Table(
        "decks", meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String),
        sa.Column("user_id", sa.Integer),
        sa.Column("binder_id", sa.Integer),
    )
    flashcards = sa.Table(
        "flashcards", meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("deck_id", sa.Integer),
        sa.Column("card_type", sa.String),
        sa.Column("payload", sa.JSON),
        sa.Column("ease_factor", sa.Float),
        sa.Column("interval", sa.Integer),
        sa.Column("repetitions", sa.Integer),
        sa.Column("next_review", sa.DateTime),
    )
    revision_sets = sa.Table(
        "revision_sets", meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String),
        sa.Column("description", sa.Text),
        sa.Column("type", sa.String),
        sa.Column("user_id", sa.Integer),
        sa.Column("binder_id", sa.Integer),
        sa.Column("tuning_default", sa.Float),
        sa.Column("is_public", sa.Boolean),
    )
    revision_items = sa.Table(
        "revision_items", meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("set_id", sa.Integer),
        sa.Column("payload", sa.JSON),
        sa.Column("position", sa.Integer),
        sa.Column("tuning", sa.Float),
        sa.Column("ease_factor", sa.Float),
        sa.Column("interval", sa.Integer),
        sa.Column("repetitions", sa.Integer),
        sa.Column("next_review", sa.DateTime),
    )
    return decks, flashcards, revision_sets, revision_items


def reconcile(bind):
    """Logique de réconciliation (extraite pour être testable hors contexte Alembic)."""
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if "flashcards" not in tables or "revision_sets" not in tables or "revision_items" not in tables:
        return
    if "card_type" not in {c["name"] for c in inspector.get_columns("flashcards")}:
        return

    meta = sa.MetaData()
    decks, flashcards, revision_sets, revision_items = _tables(meta)

    # Couples (deck, type) à reconstituer en ensembles homogènes.
    groups = bind.execute(
        sa.select(flashcards.c.deck_id, flashcards.c.card_type)
        .where(flashcards.c.card_type.isnot(None))
        .where(flashcards.c.card_type != "basic")
        .distinct()
    ).fetchall()

    for deck_id, card_type in groups:
        new_type = TYPE_MAP.get(card_type)
        if new_type is None:
            continue

        deck = bind.execute(
            sa.select(decks.c.name, decks.c.user_id, decks.c.binder_id).where(decks.c.id == deck_id)
        ).first()
        if deck is None:
            continue

        label = TYPE_LABELS.get(card_type, card_type)
        set_name = f"{deck.name} — {label}"[:100]
        result = bind.execute(
            revision_sets.insert().values(
                name=set_name,
                description=None,
                type=new_type,
                user_id=deck.user_id,
                binder_id=deck.binder_id,
                tuning_default=1.0,
                is_public=False,
            )
        )
        set_id = result.inserted_primary_key[0]

        cards = bind.execute(
            sa.select(
                flashcards.c.id, flashcards.c.payload, flashcards.c.ease_factor,
                flashcards.c.interval, flashcards.c.repetitions, flashcards.c.next_review,
            )
            .where(flashcards.c.deck_id == deck_id)
            .where(flashcards.c.card_type == card_type)
            .order_by(flashcards.c.id)
        ).fetchall()

        for position, card in enumerate(cards):
            bind.execute(
                revision_items.insert().values(
                    set_id=set_id,
                    payload=card.payload if card.payload is not None else {},
                    position=position,
                    tuning=1.0,
                    ease_factor=card.ease_factor if card.ease_factor is not None else 2.5,
                    interval=card.interval if card.interval is not None else 0,
                    repetitions=card.repetitions if card.repetitions is not None else 0,
                    next_review=card.next_review,
                )
            )

        bind.execute(
            flashcards.delete()
            .where(flashcards.c.deck_id == deck_id)
            .where(flashcards.c.card_type == card_type)
        )


def upgrade():
    reconcile(op.get_bind())


def downgrade():
    # Réconciliation de données non réversible : on ne reconstruit pas les cartes
    # typées dans les decks (no-op pour rester idempotent et sûr).
    pass
