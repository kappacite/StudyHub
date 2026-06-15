"""add class_questions table (Q&A élèves, B4)

Revision ID: a7c1d2e3f4b5
Revises: c3d4e5f6a7b8
Create Date: 2026-06-15 00:40:00.000000

Questions des élèves au professeur. Additif et idempotent.
"""
from alembic import op
import sqlalchemy as sa


revision = 'a7c1d2e3f4b5'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "class_questions" not in tables:
        op.create_table(
            'class_questions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('group_id', sa.Integer(), nullable=False),
            sa.Column('author_id', sa.Integer(), nullable=False),
            sa.Column('body', sa.Text(), nullable=False),
            sa.Column('answer', sa.Text(), nullable=True),
            sa.Column('answered_by', sa.Integer(), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=False, server_default='open'),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
            sa.Column('answered_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['answered_by'], ['users.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_class_questions_group_id', 'class_questions', ['group_id'])
        op.create_index('ix_class_questions_author_id', 'class_questions', ['author_id'])
        op.create_index('ix_class_questions_created_at', 'class_questions', ['created_at'])
        op.create_index('ix_class_questions_group_id_created_at', 'class_questions', ['group_id', 'created_at'])


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "class_questions" in tables:
        op.drop_index('ix_class_questions_group_id_created_at', table_name='class_questions')
        op.drop_index('ix_class_questions_created_at', table_name='class_questions')
        op.drop_index('ix_class_questions_author_id', table_name='class_questions')
        op.drop_index('ix_class_questions_group_id', table_name='class_questions')
        op.drop_table('class_questions')
