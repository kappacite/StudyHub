"""C1 — rattacher/détacher des éléments existants à un classeur.

Orchestration transverse : un seul point d'entrée pour déplacer notes, decks,
ensembles de révision, diagrammes et PDF vers/hors d'un classeur, sans suppression.
La cohérence de couche est respectée (le service n'écrit pas de SQL : il passe par
les DAO et `binder_id`)."""
from typing import List
from app.utils.security import check_binder_access
from app.middlewares.error_handler import (
    ResourceNotFoundError, ForbiddenError, ValidationError,
)

# Types d'éléments rattachables et libellés (pour les messages).
ITEM_TYPES = ("note", "deck", "set", "diagram", "pdf")


class BinderItemsService:
    def __init__(self, binder_dao, note_dao, deck_dao, revision_set_dao, diagram_dao, pdf_dao):
        self._binder_dao = binder_dao
        self._db = binder_dao.db
        self._daos = {
            "note": note_dao,
            "deck": deck_dao,
            "set": revision_set_dao,
            "diagram": diagram_dao,
            "pdf": pdf_dao,
        }

    def _get_owned(self, item_type: str, item_id, user_id: int):
        dao = self._daos.get(item_type)
        if dao is None:
            raise ValidationError(f"Type d'élément inconnu : {item_type}")
        # deck / diagram / set sont identifiés par un entier ; note / pdf par UUID.
        if item_type in ("deck", "diagram", "set"):
            try:
                item_id = int(item_id)
            except (TypeError, ValueError):
                raise ValidationError("Identifiant d'élément invalide.")
        entity = dao.get_by_id(item_id)
        if not entity:
            raise ResourceNotFoundError("Élément introuvable.")
        if entity.user_id != user_id:
            raise ForbiddenError("Accès interdit à cet élément.")
        return entity

    def attach(self, user_id: int, binder_id, items: List) -> int:
        """Rattache les éléments au classeur (déplacement, pas de copie)."""
        binder = check_binder_access(self._db, binder_id, user_id, write_required=True)
        entities = [self._get_owned(it.type, it.id, user_id) for it in items]
        for entity in entities:
            entity.binder_id = binder._id
        self._db.commit()
        return len(entities)

    def detach(self, user_id: int, items: List) -> int:
        """Détache les éléments de leur classeur (binder_id = NULL), sans suppression."""
        entities = [self._get_owned(it.type, it.id, user_id) for it in items]
        for entity in entities:
            entity.binder_id = None
        self._db.commit()
        return len(entities)
