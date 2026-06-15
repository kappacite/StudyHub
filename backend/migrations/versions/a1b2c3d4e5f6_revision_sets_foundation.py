"""revision sets foundation (D3c) : tables revision_sets / revision_items + study_sessions.item

Revision ID: a1b2c3d4e5f6
Revises: f2b3c4d5e6a7
Create Date: 2026-06-15 14:00:00.000000

Socle des ensembles de révision génériques (qcm/vf/association/definition/ordre),
indépendants des flashcards (qui restent recto/verso dans les decks). Ajoute aussi
le suivi unifié `item_id`/`item_type` sur study_sessions (D5).

Additif et idempotent (guard `inspector`), compatible SQLite et PostgreSQL.
"""
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = 'f2b3c4d5e6a7'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "revision_sets" not in tables:
        op.create_table(
            "revision_sets",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("type", sa.String(length=20), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("binder_id", sa.Integer(), nullable=True),
            sa.Column("tuning_default", sa.Float(), server_default="1.0", nullable=False),
            sa.Column("is_public", sa.Boolean(), server_default="0", nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["binder_id"], ["binders.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_revision_sets_user_id", "revision_sets", ["user_id"])
        op.create_index("ix_revision_sets_binder_id", "revision_sets", ["binder_id"])

    if "revision_items" not in tables:
        op.create_table(
            "revision_items",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("set_id", sa.Integer(), nullable=False),
            sa.Column("payload", sa.JSON(), nullable=False),
            sa.Column("position", sa.Integer(), server_default="0", nullable=False),
            sa.Column("tuning", sa.Float(), server_default="1.0", nullable=False),
            sa.Column("ease_factor", sa.Float(), nullable=False, server_default="2.5"),
            sa.Column("interval", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("repetitions", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("next_review", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
            sa.ForeignKeyConstraint(["set_id"], ["revision_sets.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_revision_items_set_id_next_review",
            "revision_items",
            ["set_id", "next_review"],
        )

    # Suivi unifié des éléments de révision sur study_sessions (D5).
    if "study_sessions" in tables:
        cols = {c["name"] for c in inspector.get_columns("study_sessions")}
        with op.batch_alter_table("study_sessions", schema=None) as batch_op:
            if "item_id" not in cols:
                batch_op.add_column(sa.Column("item_id", sa.Integer(), nullable=True))
            if "item_type" not in cols:
                batch_op.add_column(sa.Column("item_type", sa.String(length=20), nullable=True))
        # Index séparé (idempotent) sur item_id.
        existing_idx = {i["name"] for i in inspector.get_indexes("study_sessions")}
        if "ix_study_sessions_item_id" not in existing_idx:
            op.create_index("ix_study_sessions_item_id", "study_sessions", ["item_id"])


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "study_sessions" in tables:
        existing_idx = {i["name"] for i in inspector.get_indexes("study_sessions")}
        if "ix_study_sessions_item_id" in existing_idx:
            op.drop_index("ix_study_sessions_item_id", table_name="study_sessions")
        cols = {c["name"] for c in inspector.get_columns("study_sessions")}
        with op.batch_alter_table("study_sessions", schema=None) as batch_op:
            if "item_type" in cols:
                batch_op.drop_column("item_type")
            if "item_id" in cols:
                batch_op.drop_column("item_id")

    if "revision_items" in tables:
        op.drop_table("revision_items")
    if "revision_sets" in tables:
        op.drop_table("revision_sets")
