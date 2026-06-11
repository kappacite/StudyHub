"""add tags system

Revision ID: f4a8d9e2c731
Revises: c23a7429e6f8
Create Date: 2026-06-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "f4a8d9e2c731"
down_revision = "c23a7429e6f8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("color", sa.String(length=7), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "user_id", name="uq_tags_name_user_id"),
    )

    _create_link_table("note_tags", "note_id", "notes")
    _create_link_table("deck_tags", "deck_id", "decks")
    _create_link_table("diagram_tags", "diagram_id", "diagrams")
    _create_link_table("pdf_tags", "pdf_id", "pdf_documents")
    _create_link_table("binder_tags", "binder_id", "binders")

    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        op.execute(
            """
            INSERT INTO tags (name, user_id)
            SELECT DISTINCT tag_name, user_id
            FROM (
                SELECT tag_name, user_id
                FROM binders,
                LATERAL json_array_elements_text(
                    CASE WHEN json_typeof(tags::json) = 'array' THEN tags::json ELSE '[]'::json END
                ) AS tag_name
                WHERE tags IS NOT NULL
                
                UNION
                
                SELECT tags::json#>>'{}' AS tag_name, user_id
                FROM binders
                WHERE tags IS NOT NULL AND json_typeof(tags::json) = 'string'
            ) sub
            WHERE tag_name IS NOT NULL AND tag_name <> ''
            ON CONFLICT (name, user_id) DO NOTHING
            """
        )
        op.execute(
            """
            INSERT INTO binder_tags (binder_id, tag_id)
            SELECT DISTINCT sub.binder_id, tags.id
            FROM (
                SELECT binders.id AS binder_id, tag_name, binders.user_id
                FROM binders,
                LATERAL json_array_elements_text(
                    CASE WHEN json_typeof(binders.tags::json) = 'array' THEN binders.tags::json ELSE '[]'::json END
                ) AS tag_name
                WHERE binders.tags IS NOT NULL
                
                UNION
                
                SELECT binders.id AS binder_id, binders.tags::json#>>'{}' AS tag_name, binders.user_id
                FROM binders
                WHERE binders.tags IS NOT NULL AND json_typeof(binders.tags::json) = 'string'
            ) sub
            JOIN tags ON tags.name = sub.tag_name AND tags.user_id = sub.user_id
            ON CONFLICT DO NOTHING
            """
        )

    with op.batch_alter_table("binders", schema=None) as batch_op:
        batch_op.drop_column("tags")


def downgrade():
    with op.batch_alter_table("binders", schema=None) as batch_op:
        batch_op.add_column(sa.Column("tags", sa.JSON(), nullable=True))

    op.drop_table("binder_tags")
    op.drop_table("pdf_tags")
    op.drop_table("diagram_tags")
    op.drop_table("deck_tags")
    op.drop_table("note_tags")
    op.drop_table("tags")


def _create_link_table(table_name: str, entity_column: str, entity_table: str):
    op.create_table(
        table_name,
        sa.Column(entity_column, sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint([entity_column], [f"{entity_table}.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint(entity_column, "tag_id"),
    )
