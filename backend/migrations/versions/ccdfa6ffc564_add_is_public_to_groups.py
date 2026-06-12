"""add is_public to groups

Revision ID: ccdfa6ffc564
Revises: bbc025114df0
Create Date: 2026-06-12 21:58:23.606301

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ccdfa6ffc564'
down_revision = 'bbc025114df0'
branch_labels = None
depends_on = None


def upgrade():
    # Manually added to resolve missing column in production
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    group_columns = {col["name"] for col in inspector.get_columns("groups")} if "groups" in inspector.get_table_names() else set()
    
    with op.batch_alter_table('groups', schema=None) as batch_op:
        if "is_public" not in group_columns:
            # Set default value depending on dialect
            is_postgres = bind.dialect.name == 'postgresql'
            default_val = 'false' if is_postgres else '0'
            batch_op.add_column(sa.Column('is_public', sa.Boolean(), nullable=False, server_default=sa.text(default_val)))


def downgrade():
    with op.batch_alter_table('groups', schema=None) as batch_op:
        batch_op.drop_column('is_public')


