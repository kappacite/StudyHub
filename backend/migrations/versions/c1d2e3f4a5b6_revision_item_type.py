"""revision item type (D8) : deplace type de revision_sets vers revision_items

Revision ID: c1d2e3f4a5b6
Revises: 4e6e094d2711
Create Date: 2026-08-28 12:00:00.000000

Ajoute revision_items.type (backfille depuis revision_sets.type pour les
lignes existantes -- tous les ensembles actuels sont homogenes) et rend
revision_sets.type nullable (ensembles heterogenes futurs, type porte par
l'item). Additif et idempotent (guard inspector), compatible SQLite et
PostgreSQL.
"""
from alembic import op
import sqlalchemy as sa


revision = 'c1d2e3f4a5b6'
down_revision = '4e6e094d2711'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    cols = {c["name"] for c in inspector.get_columns("revision_items")}
    if "type" not in cols:
        with op.batch_alter_table("revision_items", schema=None) as batch_op:
            batch_op.add_column(sa.Column("type", sa.String(length=20), nullable=True))

        op.execute(
            "UPDATE revision_items SET type = ("
            "SELECT revision_sets.type FROM revision_sets "
            "WHERE revision_sets.id = revision_items.set_id"
            ") WHERE type IS NULL"
        )

    with op.batch_alter_table("revision_sets", schema=None) as batch_op:
        batch_op.alter_column("type", existing_type=sa.String(length=20), nullable=True)


def downgrade():
    with op.batch_alter_table("revision_sets", schema=None) as batch_op:
        batch_op.alter_column("type", existing_type=sa.String(length=20), nullable=False)

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("revision_items")}
    if "type" in cols:
        with op.batch_alter_table("revision_items", schema=None) as batch_op:
            batch_op.drop_column("type")
