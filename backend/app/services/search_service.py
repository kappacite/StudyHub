import re
from typing import Dict, Any, List
from app.dao.search_dao import SearchDAO
from app.schemas.tag_schema import TagResponseSchema

class SearchService:
    def __init__(self, search_dao: SearchDAO):
        self._search_dao = search_dao

    def sanitize_query(self, query: str) -> str:
        """
        Nettoie la requête : strip, limite la longueur et retire les caractères spéciaux.
        """
        if not query:
            return ""
        # Limite à 100 caractères
        query = query[:100]
        # Conserve lettres, chiffres, espaces, tirets et caractères accentués
        query = re.sub(r'[^\w\s\-\u00C0-\u00FF]', '', query)
        return query.strip()

    def make_excerpt(self, text: str, query: str, length: int = 150) -> str:
        """
        Formate un extrait de 150 caractères autour du premier match, avec <mark> autour du terme trouvé.
        """
        if not text:
            return ""
            
        # Recherche insensible à la casse
        text_lower = text.lower()
        query_lower = query.lower()
        
        idx = text_lower.find(query_lower)
        if idx == -1:
            # Si le terme n'est pas dans le corps de texte, retourner le début
            excerpt = text[:length]
            if len(text) > length:
                excerpt += "..."
            return excerpt
            
        # Centre l'extrait autour du premier match trouvé
        start = max(0, idx - 70)
        end = min(len(text), idx + 80)
        
        excerpt = text[start:end]
        
        # Ajout des points de suspension
        prefix = "..." if start > 0 else ""
        suffix = "..." if end < len(text) else ""
        
        full_excerpt = prefix + excerpt + suffix
        
        # Remplacement avec balise <mark> insensible à la casse
        try:
            pattern = re.compile(rf"({re.escape(query)})", re.IGNORECASE)
            highlighted = pattern.sub(r"<mark>\1</mark>", full_excerpt)
            return highlighted
        except Exception:
            return full_excerpt

    def search(self, user_id: int, query: str, types: List[str] = None, limit: int = 20) -> Dict[str, Any]:
        """
        Exécute la recherche globale et assemble les résultats enrichis.
        """
        if not types:
            types = ["note", "deck", "flashcard", "diagram"]
            
        sanitized_query = self.sanitize_query(query)
        if len(sanitized_query) < 2:
            return {
                "query": query,
                "results": {
                    "notes": [],
                    "decks": [],
                    "flashcards": [],
                    "diagrams": []
                },
                "total": 0
            }
            
        raw_results = self._search_dao.search_all(user_id, sanitized_query, types, limit)
        
        formatted_results = {
            "notes": [],
            "decks": [],
            "flashcards": [],
            "diagrams": []
        }
        
        total_count = 0
        
        # 1. Notes
        for note, score in raw_results.get("notes", []):
            excerpt = self.make_excerpt(note.content, sanitized_query)
            formatted_results["notes"].append({
                "id": note.id,
                "title": note.title,
                "excerpt": excerpt,
                "binder_id": note.binder_id,
                "tags": [TagResponseSchema.model_validate(t).model_dump() for t in note.tags],
                "score": float(score)
            })
            total_count += 1
            
        # 2. Decks
        for deck, score in raw_results.get("decks", []):
            excerpt = self.make_excerpt(deck.description or "", sanitized_query)
            formatted_results["decks"].append({
                "id": deck.id,
                "name": deck.name,
                "excerpt": excerpt,
                "binder_id": deck.binder_id,
                "tags": [TagResponseSchema.model_validate(t).model_dump() for t in deck.tags],
                "score": float(score)
            })
            total_count += 1
            
        # 3. Flashcards
        for card, score in raw_results.get("flashcards", []):
            formatted_results["flashcards"].append({
                "id": card.id,
                "front": card.front,
                "deck_id": card.deck_id,
                "deck_name": card.deck.name if card.deck else "Deck",
                "score": float(score)
            })
            total_count += 1
            
        # 4. Diagrams
        for diagram, score in raw_results.get("diagrams", []):
            formatted_results["diagrams"].append({
                "id": diagram.id,
                "title": diagram.title,
                "binder_id": diagram.binder_id,
                "score": float(score)
            })
            total_count += 1
            
        return {
            "query": sanitized_query,
            "results": formatted_results,
            "total": total_count
        }
