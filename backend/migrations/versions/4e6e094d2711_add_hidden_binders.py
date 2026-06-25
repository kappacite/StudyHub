"""add_hidden_binders

Revision ID: 4e6e094d2711
Revises: a7c1d2e3f4b5
Create Date: 2026-06-25 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e6e094d2711'
down_revision = 'a7c1d2e3f4b5'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "hidden_binders",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("binder_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["binder_id"], ["binders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "binder_id"),
    )


def downgrade():
    op.drop_table("hidden_binders")
