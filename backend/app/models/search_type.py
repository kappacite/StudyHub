from sqlalchemy.types import TypeDecorator, Text
from sqlalchemy.dialects.postgresql import TSVECTOR

class TSVectorType(TypeDecorator):
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(TSVECTOR())
        else:
            return dialect.type_descriptor(Text())
