"""add notifications table and groups.leaderboard_enabled

Revision ID: d9a4c5e6b7f8
Revises: c8e2b3d4f6a7
Create Date: 2026-06-15 00:20:00.000000

Engagement classe (PR 4) : notifications in-app + classement opt-in.
Additif et idempotent.
"""
from alembic import op
import sqlalchemy as sa


revision = 'd9a4c5e6b7f8'
down_revision = 'c8e2b3d4f6a7'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    is_postgres = bind.dialect.name == 'postgresql'
    bool_true = 'true' if is_postgres else '1'

    group_cols = {
        c["name"] for c in inspector.get_columns("groups")
    } if "groups" in tables else set()

    if "groups" in tables and "leaderboard_enabled" not in group_cols:
        with op.batch_alter_table('groups', schema=None) as batch_op:
            batch_op.add_column(sa.Column(
                'leaderboard_enabled', sa.Boolean(), nullable=False,
                server_default=sa.text(bool_true),
            ))

    if "notifications" not in tables:
        op.create_table(
            'notifications',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('type', sa.String(length=30), nullable=False),
            sa.Column('title', sa.String(length=200), nullable=False),
            sa.Column('body', sa.Text(), nullable=True),
            sa.Column('link', sa.String(length=255), nullable=True),
            sa.Column('group_id', sa.Integer(), nullable=True),
            sa.Column('read_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
        op.create_index('ix_notifications_created_at', 'notifications', ['created_at'])


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "notifications" in tables:
        op.drop_index('ix_notifications_created_at', table_name='notifications')
        op.drop_index('ix_notifications_user_id', table_name='notifications')
        op.drop_table('notifications')

    if "groups" in tables:
        with op.batch_alter_table('groups', schema=None) as batch_op:
            batch_op.drop_column('leaderboard_enabled')
