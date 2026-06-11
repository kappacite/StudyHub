"""add class type to groups and assignment tables

Revision ID: a3f1e7c09b22
Revises: 6712d2893f33
Create Date: 2026-06-11 20:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3f1e7c09b22'
down_revision = '6712d2893f33'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    group_columns = {
        column["name"]
        for column in inspector.get_columns("groups")
    } if "groups" in tables else set()

    # Extend groups table
    is_postgres = bind.dialect.name == 'postgresql'
    is_class_default = 'false' if is_postgres else '0'
    with op.batch_alter_table('groups', schema=None) as batch_op:
        if "type" not in group_columns:
            batch_op.add_column(sa.Column('type', sa.String(length=10), nullable=False, server_default='study'))
        if "is_class" not in group_columns:
            batch_op.add_column(sa.Column('is_class', sa.Boolean(), nullable=False, server_default=sa.text(is_class_default)))

    # Create assignments table
    if "assignments" not in tables:
        op.create_table(
            'assignments',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('group_id', sa.Integer(), nullable=False),
            sa.Column('binder_id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=200), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('due_date', sa.DateTime(), nullable=True),
            sa.Column('created_by', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
            sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['binder_id'], ['binders.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # Create assignment_progress table
    if "assignment_progress" not in tables:
        op.create_table(
            'assignment_progress',
            sa.Column('assignment_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('cards_reviewed', sa.Integer(), nullable=False, server_default=sa.text('0')),
            sa.Column('score_pct', sa.Float(), nullable=True),
            sa.Column('completed_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['assignment_id'], ['assignments.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('assignment_id', 'user_id')
        )


def downgrade():
    op.drop_table('assignment_progress')
    op.drop_table('assignments')
    with op.batch_alter_table('groups', schema=None) as batch_op:
        batch_op.drop_column('is_class')
        batch_op.drop_column('type')
