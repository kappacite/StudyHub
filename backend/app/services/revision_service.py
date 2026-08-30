from app.dao.binder_dao import BinderDAO
from app.dao.revision_dao import RevisionItemDAO, RevisionSetDAO
from app.models.revision import RevisionItem, RevisionSet
from app.models.study_session import StudySession
from app.schemas.revision_schema import (
    RevisionGradeResult,
    RevisionItemCreate,
    RevisionItemResponse,
    RevisionItemUpdate,
    RevisionQcmAnswerResult,
    RevisionQcmCheckResult,
    RevisionSetCreate,
    RevisionSetResponse,
    RevisionSetUpdate,
)

# Types corrigés automatiquement à l'étude (la définition reste en auto-évaluation).
GRADABLE_TYPES = ("vf", "association", "ordre")
from app.middlewares.error_handler import (
    ForbiddenError,
    ResourceNotFoundError,
    ValidationError,
)
from app.services.spaced_repetition import calculate_sm2


def validate_item_payload(item_type: str, payload: dict) -> dict:
    """Valide (et normalise légèrement) le payload d'un item selon son
    propre type. Lève ValidationError (400) si le contenu est incohérent."""
    if not isinstance(payload, dict):
        raise ValidationError("Le contenu de l'item est invalide.")

    if item_type == "qcm":
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

    elif item_type == "vf":
        if not (payload.get("assertion") or "").strip():
            raise ValidationError("L'affirmation est obligatoire.")
        if not isinstance(payload.get("correct"), bool):
            raise ValidationError("Le verdict (vrai/faux) est obligatoire.")

    elif item_type == "association":
        pairs = payload.get("pairs")
        if not isinstance(pairs, list) or len(pairs) < 2:
            raise ValidationError("Une association doit comporter au moins deux paires.")
        for p in pairs:
            if (
                not isinstance(p, dict)
                or not (p.get("left") or "").strip()
                or not (p.get("right") or "").strip()
            ):
                raise ValidationError("Chaque paire doit avoir un terme et sa correspondance.")

    elif item_type == "definition":
        if not (payload.get("term") or "").strip():
            raise ValidationError("Le terme est obligatoire.")
        if not (payload.get("definition") or "").strip():
            raise ValidationError("La définition est obligatoire.")

    elif item_type == "ordre":
        steps = payload.get("steps")
        if not isinstance(steps, list) or len([s for s in steps if (s or "").strip()]) < 2:
            raise ValidationError("Un exercice d'ordre doit comporter au moins deux étapes.")

    elif item_type == "flashcard":
        if not (payload.get("front") or "").strip():
            raise ValidationError("Le recto de la flashcard est obligatoire.")
        if not (payload.get("back") or "").strip():
            raise ValidationError("Le verso de la flashcard est obligatoire.")

    else:
        raise ValidationError(f"Type d'item de révision inconnu : {item_type}.")

    return payload


def check_answer(item_type: str, payload: dict, answer: dict) -> bool:
    """Correction d'une réponse à l'étude pour les types auto-corrigeables.
    "flashcard" (comme "definition") n'est jamais auto-corrige -- retombe
    sur le defaut False ci-dessous (auto-evaluation cote client)."""
    if item_type == "vf":
        return isinstance(answer.get("value"), bool) and answer["value"] is bool(
            payload.get("correct")
        )

    if item_type == "association":
        expected = {p["left"]: p["right"] for p in payload.get("pairs", [])}
        submitted = answer.get("matches")
        # Appariement complet et exact (ordre indifférent) ; un appariement
        # partiel ou erroné est considéré faux.
        return isinstance(submitted, dict) and submitted == expected

    if item_type == "ordre":
        expected = [s for s in payload.get("steps", []) if str(s).strip()]
        return answer.get("order") == expected

    return False


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

        binder = check_binder_access(
            self._set_dao.db, binder_id, user_id, write_required=write_required
        )
        return binder._id

    def _to_set_response(self, rset: RevisionSet, item_count: int) -> RevisionSetResponse:
        resp = RevisionSetResponse.model_validate(rset)
        resp.item_count = item_count
        return resp

    def _get_set_or_404(
        self, set_id: int, user_id: int, write_required: bool = False
    ) -> RevisionSet:
        rset = self._set_dao.get_by_id(set_id)
        if not rset:
            raise ResourceNotFoundError("Ensemble de révision introuvable.")
        if rset.user_id != user_id:
            if rset.binder_id:
                from app.utils.security import check_binder_access

                check_binder_access(
                    self._set_dao.db, rset.binder_id, user_id, write_required=write_required
                )
            else:
                raise ForbiddenError("Accès interdit à cet ensemble.")
        elif write_required and rset.binder_id:
            from app.utils.security import check_binder_access

            check_binder_access(self._set_dao.db, rset.binder_id, user_id, write_required=True)
        return rset

    def _get_item_or_404(
        self, item_id: int, set_id: int, user_id: int, write_required: bool = False
    ) -> RevisionItem:
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
        set_type: str | None = None,
        binder_id: str | None = None,
        search: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[RevisionSetResponse], int]:
        binder_internal = None
        if binder_id is not None:
            binder_internal = self._resolve_binder(binder_id, user_id, write_required=False)

        offset = (page - 1) * per_page
        sets = self._set_dao.search_sets(
            user_id, set_type, binder_internal, search, limit=per_page, offset=offset
        )
        total = self._set_dao.count_sets(user_id, set_type, binder_internal, search)
        counts = self._set_dao.count_items_by_sets([s.id for s in sets])
        responses = [self._to_set_response(s, counts.get(s.id, 0)) for s in sets]

        # Inclure les ensembles des classeurs partagés (cours), en LECTURE SEULE —
        # symétrique des notes/PDF (listing global, sans filtre binder ni recherche).
        if binder_id is None and search is None:
            shared_ids: list = []
            for root in self._binder_dao.get_shared_root_binders(user_id):
                shared_ids.append(root._id)
                shared_ids.extend(d._id for d in self._binder_dao.get_descendants(root._id))
            if shared_ids:
                shared_sets = self._set_dao.get_by_binders(shared_ids)
                if set_type:
                    shared_sets = [s for s in shared_sets if s.type == set_type]
                shared_counts = self._set_dao.count_items_by_sets([s.id for s in shared_sets])
                for s in shared_sets:
                    resp = self._to_set_response(s, shared_counts.get(s.id, 0))
                    resp.read_only = True
                    responses.append(resp)
                total = len(responses)

        return responses, total

    def get_set(self, user_id: int, set_id: int) -> RevisionSetResponse:
        rset = self._get_set_or_404(set_id, user_id, write_required=False)
        counts = self._set_dao.count_items_by_sets([rset.id])
        resp = self._to_set_response(rset, counts.get(rset.id, 0))
        resp.read_only = rset.user_id != user_id
        return resp

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

    def create_item(
        self, user_id: int, set_id: int, data: RevisionItemCreate
    ) -> RevisionItemResponse:
        rset = self._get_set_or_404(set_id, user_id, write_required=True)
        item_type = data.type if data.type is not None else rset.type
        payload = validate_item_payload(item_type, data.payload)
        item = RevisionItem(
            set_id=set_id,
            type=item_type,
            payload=payload,
            tuning=data.tuning,
            position=data.position,
        )
        created = self._item_dao.create(item)
        return RevisionItemResponse.model_validate(created)

    def get_items(self, user_id: int, set_id: int) -> list[RevisionItemResponse]:
        self._get_set_or_404(set_id, user_id, write_required=False)
        items = self._item_dao.get_by_set(set_id)
        return [RevisionItemResponse.model_validate(i) for i in items]

    def update_item(
        self, user_id: int, set_id: int, item_id: int, data: RevisionItemUpdate
    ) -> RevisionItemResponse:
        self._get_set_or_404(set_id, user_id, write_required=True)
        item = self._get_item_or_404(item_id, set_id, user_id, write_required=True)
        if "payload" in data.model_fields_set and data.payload is not None:
            item.payload = validate_item_payload(item.type, data.payload)
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

    def get_study_items(self, user_id: int, set_id: int) -> list[RevisionItemResponse]:
        rset = self._get_set_or_404(set_id, user_id, write_required=False)
        if rset.user_id == user_id:
            items = self._item_dao.get_items_to_study(set_id)
        else:
            # Ensemble partagé (cours) : l'état SM-2 par item (next_review) appartient
            # au propriétaire. L'élève révise donc TOUS les items ; sa progression est
            # suivie séparément via StudySession (par utilisateur).
            items = self._item_dao.get_by_set(set_id)
        return [RevisionItemResponse.model_validate(i) for i in items]

    def answer_item(
        self,
        user_id: int,
        set_id: int,
        item_id: int,
        score: int,
        duration_seconds: int = 0,
    ) -> RevisionItemResponse:
        rset = self._get_set_or_404(set_id, user_id, write_required=False)
        item = self._get_item_or_404(item_id, set_id, user_id, write_required=False)

        # L'état SM-2 par item n'est planifié que pour le propriétaire de l'ensemble.
        # Un élève qui révise un ensemble partagé (cours) ne doit pas modifier
        # l'échéancier du prof — seule sa StudySession est enregistrée.
        if rset.user_id == user_id:
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
        else:
            updated = item

        # Historique unifié (D5) : on renseigne item_id + item_type.
        # module ne peut pas rester rset.type tel quel : None pour un ensemble
        # hétérogène (D8), violerait la contrainte NOT NULL -- item.type retombe
        # toujours sur une valeur concrète (cf. Task 3 du chantier bibliotheque-ensembles).
        study_session = StudySession(
            user_id=user_id,
            module=rset.type or item.type,
            duration_seconds=duration_seconds,
            cards_reviewed=1,
            cards_correct=1 if score >= 3 else 0,
            item_id=item.id,
            item_type=item.type,
            grade=score,
        )
        self._item_dao.db.add(study_session)
        self._item_dao.db.commit()

        return RevisionItemResponse.model_validate(updated)

    def _score_qcm_answer(
        self, item: RevisionItem, selected_option_ids: list[str]
    ) -> tuple[bool, int, int, list[str]]:
        """Correction pure d'une reponse a une question de QCM : pondération par
        points, tout-ou-rien sur les réponses multiples. Sans effet de bord --
        reutilisee par check_qcm_answer (lecture seule) et answer_qcm_item
        (defense-in-depth, recalculee independamment du score fourni)."""
        payload = item.payload or {}
        options = payload.get("options", [])
        points = payload.get("points", 1)
        correct_ids = sorted(o["id"] for o in options if o.get("correct"))
        selected_ids = sorted(set(selected_option_ids))
        is_correct = selected_ids == correct_ids
        earned = points if is_correct else 0
        return is_correct, earned, points, correct_ids

    def check_qcm_answer(
        self, user_id: int, set_id: int, item_id: int, selected_option_ids: list[str]
    ) -> RevisionQcmCheckResult:
        """Corrige une réponse à une question de QCM SANS aucun effet de bord
        (pas d'écriture DB) -- permet au client d'afficher la correction avant
        que l'utilisateur choisisse sa note SM-2 via answer_qcm_item (scission
        check/commit, Task 2 revision-flexibilite -- même principe que
        check_item_answer/grade_item pour vf/association/ordre, Task 1)."""
        rset = self._get_set_or_404(set_id, user_id, write_required=False)
        if rset.type != "qcm":
            raise ValidationError("Le passage scoré n'est disponible que pour les QCM.")
        item = self._get_item_or_404(item_id, set_id, user_id, write_required=False)

        is_correct, earned, points, correct_ids = self._score_qcm_answer(item, selected_option_ids)
        return RevisionQcmCheckResult(
            correct=is_correct, earned=earned, points=points, correct_option_ids=correct_ids
        )

    def answer_qcm_item(
        self,
        user_id: int,
        set_id: int,
        item_id: int,
        selected_option_ids: list[str],
        score: int,
        duration_seconds: int = 0,
    ) -> RevisionQcmAnswerResult:
        """Valide la note SM-2 choisie par l'utilisateur pour une question de
        QCM après qu'il a vu la correction (cf. check_qcm_answer). `score` est
        fourni par l'appelant -- plus jamais déduit binairement de la
        correction (réussi → 5, raté → 1, cf. ancien run_qcm). La correction
        réelle (is_correct/earned/points) est recalculée ici (defense-in-depth),
        indépendamment de `score`."""
        rset = self._get_set_or_404(set_id, user_id, write_required=False)
        if rset.type != "qcm":
            raise ValidationError("Le passage scoré n'est disponible que pour les QCM.")
        item = self._get_item_or_404(item_id, set_id, user_id, write_required=False)

        is_correct, earned, points, correct_ids = self._score_qcm_answer(item, selected_option_ids)

        # L'état SM-2 par item n'est planifié que pour le propriétaire de l'ensemble.
        # Un élève qui révise un ensemble partagé (cours) ne doit pas modifier
        # l'échéancier du prof — seule sa StudySession est enregistrée.
        if rset.user_id == user_id:
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
        else:
            updated = item

        self._item_dao.db.add(
            StudySession(
                user_id=user_id,
                module=rset.type or item.type,
                duration_seconds=duration_seconds,
                cards_reviewed=1,
                cards_correct=1 if is_correct else 0,
                item_id=item.id,
                item_type=item.type,
                grade=score,
            )
        )
        self._item_dao.db.commit()

        return RevisionQcmAnswerResult(
            correct=is_correct,
            earned=earned,
            points=points,
            correct_option_ids=correct_ids,
            item=RevisionItemResponse.model_validate(updated),
        )

    def check_item_answer(
        self,
        user_id: int,
        set_id: int,
        item_id: int,
        answer: dict,
    ) -> bool:
        """Corrige une réponse à un item auto-corrigeable (vf/association/ordre)
        SANS aucun effet de bord (pas d'écriture DB) -- permet au client
        d'afficher la correction avant que l'utilisateur choisisse sa note
        SM-2 via grade_item (scission check/commit, Task 1 revision-flexibilite)."""
        item = self._get_item_or_404(item_id, set_id, user_id, write_required=False)
        if item.type not in GRADABLE_TYPES:
            raise ValidationError("Ce type d'item n'est pas corrigé automatiquement.")

        return check_answer(item.type, item.payload or {}, answer or {})

    def grade_item(
        self,
        user_id: int,
        set_id: int,
        item_id: int,
        answer: dict,
        score: int,
        duration_seconds: int = 0,
    ) -> RevisionGradeResult:
        """Valide la note SM-2 choisie par l'utilisateur pour un item auto-
        corrigeable (vf/association/ordre) après qu'il a vu la correction
        (cf. check_item_answer). `score` est fourni par l'appelant -- plus
        jamais déduit binairement de la correction. La correction réelle est
        recalculée ici (defense-in-depth) pour `correct`/`cards_correct`,
        indépendamment de `score`. La définition reste en self-eval."""
        rset = self._get_set_or_404(set_id, user_id, write_required=False)
        item = self._get_item_or_404(item_id, set_id, user_id, write_required=False)
        if item.type not in GRADABLE_TYPES:
            raise ValidationError("Ce type d'item n'est pas corrigé automatiquement.")

        is_correct = check_answer(item.type, item.payload or {}, answer or {})

        # L'état SM-2 par item n'est planifié que pour le propriétaire de l'ensemble.
        # Un élève qui révise un ensemble partagé (cours) ne doit pas modifier
        # l'échéancier du prof — seule sa StudySession est enregistrée.
        if rset.user_id == user_id:
            ease_factor, interval, repetitions, next_review = calculate_sm2(
                score=score,
                ease_factor=item.ease_factor,
                interval=item.interval,
                repetitions=item.repetitions,
                tuning=(rset.tuning_default or 1.0) * (item.tuning or 1.0),
            )
            item.ease_factor = ease_factor
            item.interval = interval
            item.repetitions = repetitions
            item.next_review = next_review
            updated = self._item_dao.update(item)
        else:
            updated = item

        self._item_dao.db.add(
            StudySession(
                user_id=user_id,
                # cf. answer_item : rset.type est None pour un ensemble hétérogène (D8).
                module=rset.type or item.type,
                duration_seconds=duration_seconds,
                cards_reviewed=1,
                cards_correct=1 if is_correct else 0,
                item_id=item.id,
                item_type=item.type,
                grade=score,
            )
        )
        self._item_dao.db.commit()

        return RevisionGradeResult(
            correct=is_correct, item=RevisionItemResponse.model_validate(updated)
        )
