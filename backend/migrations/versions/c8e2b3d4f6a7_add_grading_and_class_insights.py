"""add teacher grading fields and class_insights table

Revision ID: c8e2b3d4f6a7
Revises: b7d1a2c3e4f5
Create Date: 2026-06-14 23:55:00.000000

Analytics professeur (PR 3) :
  - notation manuelle sur assignment_progress (teacher_score/feedback/graded_by/graded_at) ;
  - table class_insights (cache des lacunes de classe : data + résumé IA).

Additif et idempotent.
"""
from alembic import op
import sqlalchemy as sa


revision = 'c8e2b3d4f6a7'
down_revision = 'b7d1a2c3e4f5'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    prog_cols = {
        c["name"] for c in inspector.get_columns("assignment_progress")
    } if "assignment_progress" in tables else set()
    prog_fk_cols = {
        tuple(fk["constrained_columns"]) for fk in inspector.get_foreign_keys("assignment_progress")
    } if "assignment_progress" in tables else set()

    if "assignment_progress" in tables:
        with op.batch_alter_table('assignment_progress', schema=None) as batch_op:
            if "teacher_score" not in prog_cols:
                batch_op.add_column(sa.Column('teacher_score', sa.Float(), nullable=True))
            if "teacher_feedback" not in prog_cols:
                batch_op.add_column(sa.Column('teacher_feedback', sa.Text(), nullable=True))
            if "graded_by" not in prog_cols:
                batch_op.add_column(sa.Column('graded_by', sa.Integer(), nullable=True))
            if "graded_at" not in prog_cols:
                batch_op.add_column(sa.Column('graded_at', sa.DateTime(), nullable=True))
            if ("graded_by",) not in prog_fk_cols:
                batch_op.create_foreign_key(
                    'fk_assignment_progress_graded_by_users',
                    'users', ['graded_by'], ['id'], ondelete='SET NULL',
                )

    if "class_insights" not in tables:
        op.create_table(
            'class_insights',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('group_id', sa.Integer(), nullable=False),
            sa.Column('payload', sa.JSON(), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
            sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_class_insights_group_id', 'class_insights', ['group_id'])


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "class_insights" in tables:
        op.drop_index('ix_class_insights_group_id', table_name='class_insights')
        op.drop_table('class_insights')

    if "assignment_progress" in tables:
        with op.batch_alter_table('assignment_progress', schema=None) as batch_op:
            batch_op.drop_column('graded_at')
            batch_op.drop_column('graded_by')
            batch_op.drop_column('teacher_feedback')
            batch_op.drop_column('teacher_score')
