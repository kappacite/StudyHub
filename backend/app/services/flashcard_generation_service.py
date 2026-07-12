from app.middlewares.error_handler import (
    ResourceNotFoundError,
    ForbiddenError,
    ValidationError,
)


class FlashcardGenerationService:
    """Génère des flashcards par IA à partir d'une note ou d'un classeur.

    Récupère le contenu côté serveur (avec contrôle d'appartenance), l'agrège
    puis délègue la génération à l'AIService. Ne crée pas les cartes : renvoie
    une liste de dicts {"front", "back"} que la couche appelante persistera.
    """

    # Limite de contenu envoyée à l'IA (sécurité / coût)
    MAX_SOURCE_CHARS = 60000

    def __init__(self, note_dao, binder_dao, ai_service, deck_dao=None, flashcard_dao=None):
        self._note_dao = note_dao
        self._binder_dao = binder_dao
        self._ai_service = ai_service
        self._deck_dao = deck_dao
        self._flashcard_dao = flashcard_dao

    def generate_from_source(
        self, user_id: int, source_type: str, source_id, deck_id=None, coverage=100
    ) -> list:
        if source_type not in ("note", "binder"):
            raise ValidationError("source_type doit valoir 'note' ou 'binder'.")
        if not source_id:
            raise ValidationError("L'identifiant de la source est requis.")

        if source_type == "note":
            source_text, subject = self._note_source(user_id, source_id)
        else:
            source_text, subject = self._binder_source(user_id, source_id)

        if not source_text or not source_text.strip():
            raise ValidationError(
                "La source ne contient aucun texte exploitable. "
                "Ajoutez du contenu à vos notes avant de générer des flashcards."
            )

        # Cartes déjà présentes dans le deck cible : transmises à l'IA pour éviter
        # qu'elle régénère les mêmes (ou de simples variantes de formulation).
        existing_cards = self._existing_cards(user_id, deck_id)

        source_text = source_text[: self.MAX_SOURCE_CHARS]
        return self._ai_service.generate_flashcards(
            source_text, subject=subject, existing_cards=existing_cards, coverage=coverage
        )

    def _existing_cards(self, user_id: int, deck_id) -> list:
        """Cartes originales du deck cible sous forme [{'front', 'back'}].

        Filtrage strict par appartenance : un deck existant d'un autre utilisateur
        déclenche un 403 (isolation des données). Un deck_id absent ou introuvable
        renvoie une liste vide — l'enrichissement du prompt est simplement ignoré.
        """
        if not deck_id or self._deck_dao is None or self._flashcard_dao is None:
            return []
        deck = self._deck_dao.get_by_id(deck_id)
        if not deck:
            return []
        if deck.user_id != user_id:
            raise ForbiddenError("Accès interdit à ce deck.")
        cards = self._flashcard_dao.get_originals_by_deck(deck_id)
        return [{"front": c.front, "back": c.back} for c in cards]

    def _note_source(self, user_id: int, note_id):
        note = self._note_dao.get_by_id(note_id)
        if not note:
            raise ResourceNotFoundError("Note introuvable.")
        if note.user_id != user_id:
            raise ForbiddenError("Accès interdit à cette note.")
        return note.content or "", note.title or "la note"

    def _binder_source(self, user_id: int, binder_id):
        binder = self._binder_dao.get_by_id(binder_id)
        if not binder:
            raise ResourceNotFoundError("Classeur introuvable.")
        if binder.user_id != user_id:
            raise ForbiddenError("Accès interdit à ce classeur.")
        notes = self._note_dao.get_by_binder_for_user(binder._id, user_id)
        text = "\n\n".join(n.content for n in notes if n.content)
        return text, f"classeur {binder.name}"
