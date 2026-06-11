from sqlalchemy.orm import Session
from typing import Dict, Any, List

class SearchDAO:
    def __init__(self, db: Session):
        self.db = db

    def search_all(self, user_id: int, query: str, types: List[str], limit: int = 20) -> Dict[str, List[tuple]]:
        """
        Détecte le moteur de base de données (PostgreSQL vs SQLite) et utilise la stratégie appropriée.
        """
        is_postgresql = self.db.get_bind().dialect.name == "postgresql"
        if is_postgresql:
            return self._pg_search(user_id, query, types, limit)
        else:
            return self._sqlite_search(user_id, query, types, limit)

    def _sqlite_search(self, user_id: int, query: str, types: List[str], limit: int = 20) -> Dict[str, List[tuple]]:
        from app.models.note import Note
        from app.models.deck import Deck
        from app.models.flashcard import Flashcard
        from app.models.diagram import Diagram
        
        results = {
            "notes": [],
            "decks": [],
            "flashcards": [],
            "diagrams": []
        }
        
        search_pattern = f"%{query}%"
        
        if "note" in types:
            notes = (
                self.db.query(Note)
                .filter(
                    Note.user_id == user_id,
                    (Note.title.ilike(search_pattern) | Note.content.ilike(search_pattern))
                )
                .limit(limit)
                .all()
            )
            for note in notes:
                score = 1.5 if query.lower() in note.title.lower() else 1.0
                results["notes"].append((note, score))
                
        if "deck" in types:
            decks = (
                self.db.query(Deck)
                .filter(
                    Deck.user_id == user_id,
                    (Deck.name.ilike(search_pattern) | Deck.description.ilike(search_pattern))
                )
                .limit(limit)
                .all()
            )
            for deck in decks:
                score = 1.5 if query.lower() in deck.name.lower() else 1.0
                results["decks"].append((deck, score))
                
        if "flashcard" in types:
            flashcards = (
                self.db.query(Flashcard)
                .join(Deck)
                .filter(
                    Deck.user_id == user_id,
                    (Flashcard.front.ilike(search_pattern) | Flashcard.back.ilike(search_pattern))
                )
                .limit(limit)
                .all()
            )
            for flashcard in flashcards:
                score = 1.5 if query.lower() in flashcard.front.lower() else 1.0
                results["flashcards"].append((flashcard, score))
                
        if "diagram" in types:
            diagrams = (
                self.db.query(Diagram)
                .filter(
                    Diagram.user_id == user_id,
                    (Diagram.title.ilike(search_pattern) | Diagram.code.ilike(search_pattern))
                )
                .limit(limit)
                .all()
            )
            for diagram in diagrams:
                score = 1.5 if query.lower() in diagram.title.lower() else 1.0
                results["diagrams"].append((diagram, score))
                
        return results

    def _pg_search(self, user_id: int, query: str, types: List[str], limit: int = 20) -> Dict[str, List[tuple]]:
        from sqlalchemy import func
        from app.models.note import Note
        from app.models.deck import Deck
        from app.models.flashcard import Flashcard
        from app.models.diagram import Diagram
        
        results = {
            "notes": [],
            "decks": [],
            "flashcards": [],
            "diagrams": []
        }
        
        query_ts = func.plainto_tsquery('french', query)
        
        if "note" in types:
            notes = (
                self.db.query(Note, func.ts_rank(Note.search_vector, query_ts).label("rank"))
                .filter(
                    Note.user_id == user_id,
                    Note.search_vector.op("@@")(query_ts)
                )
                .order_by(func.ts_rank(Note.search_vector, query_ts).desc())
                .limit(limit)
                .all()
            )
            results["notes"] = [(note, rank) for note, rank in notes]
            
        if "deck" in types:
            decks = (
                self.db.query(Deck, func.ts_rank(Deck.search_vector, query_ts).label("rank"))
                .filter(
                    Deck.user_id == user_id,
                    Deck.search_vector.op("@@")(query_ts)
                )
                .order_by(func.ts_rank(Deck.search_vector, query_ts).desc())
                .limit(limit)
                .all()
            )
            results["decks"] = [(deck, rank) for deck, rank in decks]
            
        if "flashcard" in types:
            flashcards = (
                self.db.query(Flashcard, func.ts_rank(Flashcard.search_vector, query_ts).label("rank"))
                .join(Deck)
                .filter(
                    Deck.user_id == user_id,
                    Flashcard.search_vector.op("@@")(query_ts)
                )
                .order_by(func.ts_rank(Flashcard.search_vector, query_ts).desc())
                .limit(limit)
                .all()
            )
            results["flashcards"] = [(card, rank) for card, rank in flashcards]
            
        if "diagram" in types:
            diagrams = (
                self.db.query(Diagram, func.ts_rank(Diagram.search_vector, query_ts).label("rank"))
                .filter(
                    Diagram.user_id == user_id,
                    Diagram.search_vector.op("@@")(query_ts)
                )
                .order_by(func.ts_rank(Diagram.search_vector, query_ts).desc())
                .limit(limit)
                .all()
            )
            results["diagrams"] = [(diagram, rank) for diagram, rank in diagrams]
            
        return results
