from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.extensions import db


note_tags = Table(
    "note_tags",
    db.metadata,
    Column("note_id", Integer, ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

deck_tags = Table(
    "deck_tags",
    db.metadata,
    Column("deck_id", Integer, ForeignKey("decks.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

diagram_tags = Table(
    "diagram_tags",
    db.metadata,
    Column("diagram_id", Integer, ForeignKey("diagrams.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

pdf_tags = Table(
    "pdf_tags",
    db.metadata,
    Column("pdf_id", Integer, ForeignKey("pdf_documents.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

binder_tags = Table(
    "binder_tags",
    db.metadata,
    Column("binder_id", Integer, ForeignKey("binders.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(db.Model):
    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint("name", "user_id", name="uq_tags_name_user_id"),)

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    color = Column(String(7), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="tags")
    notes = relationship("Note", secondary=note_tags, back_populates="tags")
    decks = relationship("Deck", secondary=deck_tags, back_populates="tags")
    diagrams = relationship("Diagram", secondary=diagram_tags, back_populates="tags")
    pdfs = relationship("PDFDocument", secondary=pdf_tags, back_populates="tags")
    binders = relationship("Binder", secondary=binder_tags, back_populates="tags")
