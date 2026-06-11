"""add full text search vectors

Revision ID: f5b331d38432
Revises: ccf1c1fc10a4
Create Date: 2026-06-11 18:42:36.256063

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'f5b331d38432'
down_revision = 'ccf1c1fc10a4'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    search_type = postgresql.TSVECTOR() if bind.dialect.name == 'postgresql' else sa.Text()

    op.add_column('notes', sa.Column('search_vector', search_type, nullable=True))
    op.add_column('decks', sa.Column('search_vector', search_type, nullable=True))
    op.add_column('flashcards', sa.Column('search_vector', search_type, nullable=True))
    op.add_column('diagrams', sa.Column('search_vector', search_type, nullable=True))

    if bind.dialect.name != 'postgresql':
        return
    
    op.execute("CREATE INDEX notes_search_idx ON notes USING GIN(search_vector);")
    op.execute("CREATE INDEX decks_search_idx ON decks USING GIN(search_vector);")
    op.execute("CREATE INDEX flashcards_search_idx ON flashcards USING GIN(search_vector);")
    op.execute("CREATE INDEX diagrams_search_idx ON diagrams USING GIN(search_vector);")
    
    op.execute("""
        CREATE TRIGGER notes_search_update BEFORE INSERT OR UPDATE ON notes
        FOR EACH ROW EXECUTE FUNCTION tsvector_update_trigger(search_vector, 'pg_catalog.french', 'title', 'content');
    """)
    op.execute("""
        CREATE TRIGGER decks_search_update BEFORE INSERT OR UPDATE ON decks
        FOR EACH ROW EXECUTE FUNCTION tsvector_update_trigger(search_vector, 'pg_catalog.french', 'name', 'description');
    """)
    op.execute("""
        CREATE TRIGGER flashcards_search_update BEFORE INSERT OR UPDATE ON flashcards
        FOR EACH ROW EXECUTE FUNCTION tsvector_update_trigger(search_vector, 'pg_catalog.french', 'front', 'back');
    """)
    op.execute("""
        CREATE TRIGGER diagrams_search_update BEFORE INSERT OR UPDATE ON diagrams
        FOR EACH ROW EXECUTE FUNCTION tsvector_update_trigger(search_vector, 'pg_catalog.french', 'title');
    """)


def downgrade():
    bind = op.get_bind()

    if bind.dialect.name == 'postgresql':
        op.execute("DROP TRIGGER IF EXISTS notes_search_update ON notes;")
        op.execute("DROP TRIGGER IF EXISTS decks_search_update ON decks;")
        op.execute("DROP TRIGGER IF EXISTS flashcards_search_update ON flashcards;")
        op.execute("DROP TRIGGER IF EXISTS diagrams_search_update ON diagrams;")

        op.execute("DROP INDEX IF EXISTS notes_search_idx;")
        op.execute("DROP INDEX IF EXISTS decks_search_idx;")
        op.execute("DROP INDEX IF EXISTS flashcards_search_idx;")
        op.execute("DROP INDEX IF EXISTS diagrams_search_idx;")

    op.drop_column('notes', 'search_vector')
    op.drop_column('decks', 'search_vector')
    op.drop_column('flashcards', 'search_vector')
    op.drop_column('diagrams', 'search_vector')
