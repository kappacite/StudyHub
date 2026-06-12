"""add_uuid_columns

Revision ID: bbc025114df0
Revises: a3f1e7c09b22
Create Date: 2026-06-12 17:02:55.548658

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bbc025114df0'
down_revision = 'a3f1e7c09b22'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add columns as nullable=True
    with op.batch_alter_table('binders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('uuid', sa.String(length=36), nullable=True))

    with op.batch_alter_table('notes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('uuid', sa.String(length=36), nullable=True))

    with op.batch_alter_table('pdf_documents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('uuid', sa.String(length=36), nullable=True))

    # 2. Populate UUIDs for existing rows
    import uuid
    connection = op.get_bind()

    # Binders
    binders = connection.execute(sa.text("SELECT id FROM binders")).fetchall()
    for binder in binders:
        connection.execute(
            sa.text("UPDATE binders SET uuid = :uuid WHERE id = :id"),
            {"uuid": str(uuid.uuid4()), "id": binder[0]}
        )

    # Notes
    notes = connection.execute(sa.text("SELECT id FROM notes")).fetchall()
    for note in notes:
        connection.execute(
            sa.text("UPDATE notes SET uuid = :uuid WHERE id = :id"),
            {"uuid": str(uuid.uuid4()), "id": note[0]}
        )

    # PDF Documents
    pdfs = connection.execute(sa.text("SELECT id FROM pdf_documents")).fetchall()
    for pdf in pdfs:
        connection.execute(
            sa.text("UPDATE pdf_documents SET uuid = :uuid WHERE id = :id"),
            {"uuid": str(uuid.uuid4()), "id": pdf[0]}
        )

    # 3. Make columns nullable=False and add unique constraint
    with op.batch_alter_table('binders', schema=None) as batch_op:
        batch_op.alter_column('uuid', nullable=False, existing_type=sa.String(length=36))
        batch_op.create_unique_constraint('uq_binders_uuid', ['uuid'])

    with op.batch_alter_table('notes', schema=None) as batch_op:
        batch_op.alter_column('uuid', nullable=False, existing_type=sa.String(length=36))
        batch_op.create_unique_constraint('uq_notes_uuid', ['uuid'])

    with op.batch_alter_table('pdf_documents', schema=None) as batch_op:
        batch_op.alter_column('uuid', nullable=False, existing_type=sa.String(length=36))
        batch_op.create_unique_constraint('uq_pdfs_uuid', ['uuid'])


def downgrade():
    with op.batch_alter_table('pdf_documents', schema=None) as batch_op:
        batch_op.drop_constraint('uq_pdfs_uuid', type_='unique')
        batch_op.drop_column('uuid')

    with op.batch_alter_table('notes', schema=None) as batch_op:
        batch_op.drop_constraint('uq_notes_uuid', type_='unique')
        batch_op.drop_column('uuid')

    with op.batch_alter_table('binders', schema=None) as batch_op:
        batch_op.drop_constraint('uq_binders_uuid', type_='unique')
        batch_op.drop_column('uuid')

    # ### end Alembic commands ###
