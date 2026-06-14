"""add assignment tasks (multi-task assignments rework)

Revision ID: b7d1a2c3e4f5
Revises: a1c2e3f4b5d6
Create Date: 2026-06-14 23:10:00.000000

Refonte « devoir multi-tâches » :
  - étend assignments (instructions, publish_at, allow_late) et rend binder_id nullable ;
  - crée assignment_tasks et assignment_task_progress ;
  - backfill : chaque devoir existant → une tâche flashcards sur son binder_id.

Additif et idempotent (gardes via inspector) pour la rétro-compatibilité.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7d1a2c3e4f5'
down_revision = 'a1c2e3f4b5d6'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    is_postgres = bind.dialect.name == 'postgresql'
    bool_true = 'true' if is_postgres else '1'

    asgn_columns = {
        c["name"] for c in inspector.get_columns("assignments")
    } if "assignments" in tables else set()

    # 1) Étendre la table assignments
    if "assignments" in tables:
        with op.batch_alter_table('assignments', schema=None) as batch_op:
            if "instructions" not in asgn_columns:
                batch_op.add_column(sa.Column('instructions', sa.Text(), nullable=True))
            if "publish_at" not in asgn_columns:
                batch_op.add_column(sa.Column('publish_at', sa.DateTime(), nullable=True))
            if "allow_late" not in asgn_columns:
                batch_op.add_column(sa.Column(
                    'allow_late', sa.Boolean(), nullable=False,
                    server_default=sa.text(bool_true)
                ))
            # binder_id devient nullable (devoir purement multi-tâches autorisé)
            batch_op.alter_column('binder_id', existing_type=sa.Integer(), nullable=True)

    # 2) Table assignment_tasks
    if "assignment_tasks" not in tables:
        op.create_table(
            'assignment_tasks',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('assignment_id', sa.Integer(), nullable=False),
            sa.Column('task_type', sa.String(length=20), nullable=False),
            sa.Column('ref_id', sa.Integer(), nullable=True),
            sa.Column('ref_uuid', sa.String(length=36), nullable=True),
            sa.Column('ref_label', sa.String(length=200), nullable=True),
            sa.Column('goal', sa.JSON(), nullable=True),
            sa.Column('order', sa.Integer(), nullable=False, server_default=sa.text('0')),
            sa.ForeignKeyConstraint(['assignment_id'], ['assignments.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_assignment_tasks_assignment_id', 'assignment_tasks', ['assignment_id'])

    # 3) Table assignment_task_progress
    if "assignment_task_progress" not in tables:
        op.create_table(
            'assignment_task_progress',
            sa.Column('task_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('status', sa.String(length=12), nullable=False, server_default='todo'),
            sa.Column('score_pct', sa.Float(), nullable=True),
            sa.Column('attempts', sa.Integer(), nullable=False, server_default=sa.text('0')),
            sa.Column('submitted_at', sa.DateTime(), nullable=True),
            sa.Column('completed_at', sa.DateTime(), nullable=True),
            sa.Column('payload', sa.JSON(), nullable=True),
            sa.ForeignKeyConstraint(['task_id'], ['assignment_tasks.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('task_id', 'user_id'),
        )

    # 4) Backfill : devoirs existants → une tâche flashcards par binder_id
    if "assignments" in tables and "binders" in tables:
        op.execute(sa.text(
            '''
            INSERT INTO assignment_tasks (assignment_id, task_type, ref_id, ref_uuid, ref_label, "order")
            SELECT a.id, 'flashcards', a.binder_id, b.uuid, b.name, 0
            FROM assignments a
            LEFT JOIN binders b ON b.id = a.binder_id
            WHERE a.binder_id IS NOT NULL
              AND NOT EXISTS (
                SELECT 1 FROM assignment_tasks t WHERE t.assignment_id = a.id
              )
            '''
        ))


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "assignment_task_progress" in tables:
        op.drop_table('assignment_task_progress')
    if "assignment_tasks" in tables:
        op.drop_index('ix_assignment_tasks_assignment_id', table_name='assignment_tasks')
        op.drop_table('assignment_tasks')

    if "assignments" in tables:
        with op.batch_alter_table('assignments', schema=None) as batch_op:
            batch_op.alter_column('binder_id', existing_type=sa.Integer(), nullable=False)
            batch_op.drop_column('allow_late')
            batch_op.drop_column('publish_at')
            batch_op.drop_column('instructions')
