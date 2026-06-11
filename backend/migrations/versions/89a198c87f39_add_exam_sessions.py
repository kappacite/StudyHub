"""add exam_sessions table

Revision ID: 89a198c87f39
Revises: 829088a87a63
Create Date: 2026-06-11 19:25:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '89a198c87f39'
down_revision = '829088a87a63'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('exam_sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('binder_id', sa.Integer(), nullable=True),
    sa.Column('duration_seconds', sa.Integer(), nullable=False),
    sa.Column('started_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('score_pct', sa.Float(), nullable=True),
    sa.Column('flashcard_score', sa.Float(), nullable=True),
    sa.Column('qcm_score', sa.Float(), nullable=True),
    sa.Column('time_taken_seconds', sa.Integer(), nullable=True),
    sa.Column('items_snapshot', sa.JSON(), nullable=False),
    sa.ForeignKeyConstraint(['binder_id'], ['binders.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('exam_sessions')
