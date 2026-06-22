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

    def __init__(self, note_dao, binder_dao, ai_service):
        self._note_dao = note_dao
        self._binder_dao = binder_dao
        self._ai_service = ai_service

    def generate_from_source(self, user_id: int, source_type: str, source_id) -> list:
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

        source_text = source_text[: self.MAX_SOURCE_CHARS]
        return self._ai_service.generate_flashcards(source_text, subject=subject)

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
