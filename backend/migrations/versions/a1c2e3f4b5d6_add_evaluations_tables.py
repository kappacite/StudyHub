"""add evaluations tables

Revision ID: a1c2e3f4b5d6
Revises: d7e3a1b9c4f2
Create Date: 2026-06-13 18:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1c2e3f4b5d6'
down_revision = 'd7e3a1b9c4f2'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'evaluations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('note_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=True),
        sa.Column('score_pct', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['note_id'], ['notes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_evaluations_note_id', 'evaluations', ['note_id'])
    op.create_index('ix_evaluations_user_id', 'evaluations', ['user_id'])

    op.create_table(
        'evaluation_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('evaluation_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=10), nullable=False),
        sa.Column('source', sa.String(length=10), server_default='ai', nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('user_answer', sa.JSON(), nullable=True),
        sa.Column('is_correct', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['evaluation_id'], ['evaluations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_evaluation_items_evaluation_id', 'evaluation_items', ['evaluation_id'])


def downgrade():
    op.drop_index('ix_evaluation_items_evaluation_id', table_name='evaluation_items')
    op.drop_table('evaluation_items')
    op.drop_index('ix_evaluations_user_id', table_name='evaluations')
    op.drop_index('ix_evaluations_note_id', table_name='evaluations')
    op.drop_table('evaluations')
