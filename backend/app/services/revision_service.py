from typing import List, Optional, Tuple
from app.dao.revision_dao import RevisionSetDAO, RevisionItemDAO
from app.dao.binder_dao import BinderDAO
from app.models.revision import RevisionSet, RevisionItem
from app.models.study_session import StudySession
from app.schemas.revision_schema import (
    RevisionSetCreate, RevisionSetUpdate, RevisionSetResponse,
    RevisionItemCreate, RevisionItemUpdate, RevisionItemResponse,
    RevisionRunRequest, RevisionRunResult, RevisionRunQuestionResult,
)
from app.services.spaced_repetition import calculate_sm2
from app.middlewares.error_handler import (
    ResourceNotFoundError, ForbiddenError, ValidationError,
)


def validate_item_payload(set_type: str, payload: dict) -> dict:
    """Valide (et normalise légèrement) le payload d'un item selon le type de
    l'ensemble. Lève ValidationError (400) si le contenu est incohérent."""
    if not isinstance(payload, dict):
        raise ValidationError("Le contenu de l'item est invalide.")

    if set_type == "qcm":
        question = (payload.get("question") or "").strip()
        options = payload.get("options")
        if not question:
            raise ValidationError("La question du QCM est obligatoire.")
        if not isinstance(options, list) or len(options) < 2:
            raise ValidationError("Un QCM doit comporter au moins deux options.")
        correct = [o for o in options if isinstance(o, dict) and o.get("correct")]
        if len(correct) < 1:
            raise ValidationError("Un QCM doit comporter au moins une bonne réponse.")
        points = payload.get("points", 1)
        if not isinstance(points, int) or points < 1:
            raise ValidationError("Le barème (points) doit être un entier positif.")

    elif set_type == "vf":
        if not (payload.get("assertion") or "").strip():
            raise ValidationError("L'affirmation est obligatoire.")
        if not isinstance(payload.get("correct"), bool):
            raise ValidationError("Le verdict (vrai/faux) est obligatoire.")

    elif set_type == "association":
        pairs = payload.get("pairs")
        if not isinstance(pairs, list) or len(pairs) < 2:
            raise ValidationError("Une association doit comporter au moins deux paires.")
        for p in pairs:
            if not isinstance(p, dict) or not (p.get("left") or "").strip() or not (p.get("right") or "").strip():
                raise ValidationError("Chaque paire doit avoir un terme et sa correspondance.")

    elif set_type == "definition":
        if not (payload.get("term") or "").strip():
            raise ValidationError("Le terme est obligatoire.")
        if not (payload.get("definition") or "").strip():
            raise ValidationError("La définition est obligatoire.")

    elif set_type == "ordre":
        steps = payload.get("steps")
        if not isinstance(steps, list) or len([s for s in steps if (s or "").strip()]) < 2:
            raise ValidationError("Un exercice d'ordre doit comporter au moins deux étapes.")

    else:
        raise ValidationError(f"Type d'ensemble de révision inconnu : {set_type}.")

    return payload


class RevisionService:
    def __init__(
        self,
        set_dao: RevisionSetDAO,
        item_dao: RevisionItemDAO,
        binder_dao: BinderDAO,
    ):
        self._set_dao = set_dao
        self._item_dao = item_dao
        self._binder_dao = binder_dao

    # --- Helpers d'accès -----------------------------------------------------

    def _resolve_binder(self, binder_id, user_id: int, write_required: bool = True) -> int:
        from app.utils.security import check_binder_access
        binder = check_binder_access(self._set_dao.db, binder_id, user_id, write_required=write_required)
        return binder._id

    def _to_set_response(self, rset: RevisionSet, item_count: int) -> RevisionSetResponse:
        resp = RevisionSetResponse.model_validate(rset)
        resp.item_count = item_count
        return resp

    def _get_set_or_404(self, set_id: int, user_id: int, write_required: bool = False) -> RevisionSet:
        rset = self._set_dao.get_by_id(set_id)
        if not rset:
            raise ResourceNotFoundError("Ensemble de révision introuvable.")
        if rset.user_id != user_id:
            if rset.binder_id:
                from app.utils.security import check_binder_access
                check_binder_access(self._set_dao.db, rset.binder_id, user_id, write_required=write_required)
            else:
                raise ForbiddenError("Accès interdit à cet ensemble.")
        elif write_required and rset.binder_id:
            from app.utils.security import check_binder_access
            check_binder_access(self._set_dao.db, rset.binder_id, user_id, write_required=True)
        return rset

    def _get_item_or_404(self, item_id: int, set_id: int, user_id: int, write_required: bool = False) -> RevisionItem:
        self._get_set_or_404(set_id, user_id, write_required=write_required)
        item = self._item_dao.get_by_id(item_id)
        if not item or item.set_id != set_id:
            raise ResourceNotFoundError("Item de révision introuvable dans cet ensemble.")
        return item

    # --- Ensembles -----------------------------------------------------------

    def create_set(self, user_id: int, data: RevisionSetCreate) -> RevisionSetResponse:
        binder_id_internal = None
        if data.binder_id is not None:
            binder_id_internal = self._resolve_binder(data.binder_id, user_id, write_required=True)

        rset = RevisionSet(
            name=data.name,
            description=data.description,
            type=data.type,
            user_id=user_id,
            binder_id=binder_id_internal,
            tuning_default=data.tuning_default,
        )
        created = self._set_dao.create(rset)
        return self._to_set_response(created, 0)

    def get_sets(
        self,
        user_id: int,
        set_type: Optional[str] = None,
        binder_id: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[RevisionSetResponse], int]:
        binder_internal = None
        if binder_id is not None:
            binder_internal = self._resolve_binder(binder_id, user_id, write_required=False)

        offset = (page - 1) * per_page
        sets = self._set_dao.search_sets(user_id, set_type, binder_internal, search, limit=per_page, offset=offset)
        total = self._set_dao.count_sets(user_id, set_type, binder_internal, search)
        counts = self._set_dao.count_items_by_sets([s.id for s in sets])
        return [self._to_set_response(s, counts.get(s.id, 0)) for s in sets], total

    def get_set(self, user_id: int, set_id: int) -> RevisionSetResponse:
        rset = self._get_set_or_404(set_id, user_id, write_required=False)
        counts = self._set_dao.count_items_by_sets([rset.id])
        return self._to_set_response(rset, counts.get(rset.id, 0))

    def update_set(self, user_id: int, set_id: int, data: RevisionSetUpdate) -> RevisionSetResponse:
        rset = self._get_set_or_404(set_id, user_id, write_required=True)
        if data.name is not None:
            rset.name = data.name
        if data.description is not None:
            rset.description = data.description
        if data.tuning_default is not None:
            rset.tuning_default = data.tuning_default
        if data.binder_id is not None:
            rset.binder_id = self._resolve_binder(data.binder_id, user_id, write_required=True)
        elif "binder_id" in data.model_fields_set and data.binder_id is None:
            rset.binder_id = None
        updated = self._set_dao.update(rset)
        counts = self._set_dao.count_items_by_sets([updated.id])
        return self._to_set_response(updated, counts.get(updated.id, 0))

    def delete_set(self, user_id: int, set_id: int) -> None:
        rset = self._get_set_or_404(set_id, user_id, write_required=True)
        self._set_dao.delete(rset)

    # --- Items ---------------------------------------------------------------

    def create_item(self, user_id: int, set_id: int, data: RevisionItemCreate) -> RevisionItemResponse:
        rset = self._get_set_or_404(set_id, user_id, write_required=True)
        payload = validate_item_payload(rset.type, data.payload)
        item = RevisionItem(
            set_id=set_id,
            payload=payload,
            tuning=data.tuning,
            position=data.position,
        )
        created = self._item_dao.create(item)
        return RevisionItemResponse.model_validate(created)

    def get_items(self, user_id: int, set_id: int) -> List[RevisionItemResponse]:
        self._get_set_or_404(set_id, user_id, write_required=False)
        items = self._item_dao.get_by_set(set_id)
        return [RevisionItemResponse.model_validate(i) for i in items]

    def update_item(self, user_id: int, set_id: int, item_id: int, data: RevisionItemUpdate) -> RevisionItemResponse:
        rset = self._get_set_or_404(set_id, user_id, write_required=True)
        item = self._get_item_or_404(item_id, set_id, user_id, write_required=True)
        if "payload" in data.model_fields_set and data.payload is not None:
            item.payload = validate_item_payload(rset.type, data.payload)
        if data.tuning is not None:
            item.tuning = data.tuning
        if data.position is not None:
            item.position = data.position
        updated = self._item_dao.update(item)
        return RevisionItemResponse.model_validate(updated)

    def delete_item(self, user_id: int, set_id: int, item_id: int) -> None:
        item = self._get_item_or_404(item_id, set_id, user_id, write_required=True)
        self._item_dao.delete(item)

    # --- Étude (SM-2) --------------------------------------------------------

    def get_study_items(self, user_id: int, set_id: int) -> List[RevisionItemResponse]:
        self._get_set_or_404(set_id, user_id, write_required=False)
        items = self._item_dao.get_items_to_study(set_id)
        return [RevisionItemResponse.model_validate(i) for i in items]

    def answer_item(self, user_id: int, set_id: int, item_id: int, score: int) -> RevisionItemResponse:
        rset = self._get_set_or_404(set_id, user_id, write_required=False)
        item = self._get_item_or_404(item_id, set_id, user_id, write_required=False)

        tuning = (rset.tuning_default or 1.0) * (item.tuning or 1.0)
        ease_factor, interval, repetitions, next_review = calculate_sm2(
            score=score,
            ease_factor=item.ease_factor,
            interval=item.interval,
            repetitions=item.repetitions,
            tuning=tuning,
        )
        item.ease_factor = ease_factor
        item.interval = interval
        item.repetitions = repetitions
        item.next_review = next_review
        updated = self._item_dao.update(item)

        # Historique unifié (D5) : on renseigne item_id + item_type.
        study_session = StudySession(
            user_id=user_id,
            module=rset.type,
            duration_seconds=0,
            cards_reviewed=1,
            cards_correct=1 if score >= 3 else 0,
            item_id=item.id,
            item_type=rset.type,
            grade=score,
        )
        self._item_dao.db.add(study_session)
        self._item_dao.db.commit()

        return RevisionItemResponse.model_validate(updated)

    def run_qcm(self, user_id: int, set_id: int, data: RevisionRunRequest) -> RevisionRunResult:
        """Passage scoré d'un QCM (D6) : correction pondérée par points, tout-ou-rien
        sur les réponses multiples, et mise à jour SM-2 par question."""
        rset = self._get_set_or_404(set_id, user_id, write_required=False)
        if rset.type != "qcm":
            raise ValidationError("Le passage scoré n'est disponible que pour les QCM.")

        items = {i.id: i for i in self._item_dao.get_by_set(set_id)}
        tuning = (rset.tuning_default or 1.0)
        score = 0
        max_score = 0
        results = []

        for answer in data.answers:
            item = items.get(answer.item_id)
            if item is None:
                raise ValidationError("Une réponse cible une question hors de cet ensemble.")

            payload = item.payload or {}
            options = payload.get("options", [])
            points = payload.get("points", 1)
            correct_ids = sorted(o["id"] for o in options if o.get("correct"))
            selected_ids = sorted(set(answer.selected_option_ids))
            is_correct = selected_ids == correct_ids
            earned = points if is_correct else 0

            score += earned
            max_score += points
            results.append(RevisionRunQuestionResult(
                item_id=item.id,
                correct=is_correct,
                earned=earned,
                points=points,
                correct_option_ids=correct_ids,
                selected_option_ids=selected_ids,
            ))

            # Mise à jour SM-2 par question (réussi → 5, raté → 1).
            grade = 5 if is_correct else 1
            ease_factor, interval, repetitions, next_review = calculate_sm2(
                score=grade,
                ease_factor=item.ease_factor,
                interval=item.interval,
                repetitions=item.repetitions,
                tuning=tuning * (item.tuning or 1.0),
            )
            item.ease_factor = ease_factor
            item.interval = interval
            item.repetitions = repetitions
            item.next_review = next_review
            self._item_dao.db.add(StudySession(
                user_id=user_id,
                module=rset.type,
                duration_seconds=0,
                cards_reviewed=1,
                cards_correct=1 if is_correct else 0,
                item_id=item.id,
                item_type=rset.type,
                grade=grade,
            ))

        self._item_dao.db.commit()

        percentage = round(score / max_score * 100, 1) if max_score else 0.0
        return RevisionRunResult(score=score, max_score=max_score, percentage=percentage, results=results)
