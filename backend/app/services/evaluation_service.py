import re
import hashlib
import unicodedata
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from app.dao.evaluation_dao import EvaluationDAO
from app.dao.note_dao import NoteDAO
from app.models.evaluation import Evaluation, EvaluationItem
from app.models.deck import Deck
from app.models.flashcard import Flashcard
from app.services.ai_service import AIService
from app.schemas.evaluation_schema import (
    EvaluationResponse,
    EvaluationItemResponse,
    EvaluationAnswerResponse,
)
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError
from app.utils.placeholder_parser import extract_placeholders_from_text
from app.utils.evaluation_builder import placeholder_to_eval_item

_VALID_TYPES = ("qcm", "vf", "trou", "open")


def _normalize(text: str) -> str:
    """Normalisation tolérante pour comparer une réponse de texte à trous."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return re.sub(r"\s+", " ", text)


class EvaluationService:
    def __init__(
        self,
        evaluation_dao: EvaluationDAO,
        note_dao: NoteDAO,
        ai_service: AIService,
        deck_dao=None,
        flashcard_dao=None,
    ):
        self._evaluation_dao = evaluation_dao
        self._note_dao = note_dao
        self._ai_service = ai_service
        # Optionnels : requis seulement pour le bouclage SM-2 à la complétion.
        self._deck_dao = deck_dao
        self._flashcard_dao = flashcard_dao

    # --- Accès / sécurité ---

    def _get_note_or_403(self, note_id, user_id: int):
        note = self._note_dao.get_by_id(note_id)
        if not note:
            raise ResourceNotFoundError("Note introuvable.")
        if note.user_id != user_id:
            raise ForbiddenError("Accès interdit à cette note.")
        return note

    def _get_eval_or_403(self, evaluation_id: int, user_id: int) -> Evaluation:
        evaluation = self._evaluation_dao.get_by_id(evaluation_id)
        if not evaluation:
            raise ResourceNotFoundError("Évaluation introuvable.")
        if evaluation.user_id != user_id:
            raise ForbiddenError("Accès interdit à cette évaluation.")
        return evaluation

    # --- Génération ---

    def generate_evaluation(
        self, user_id: int, note_id, item_count: int = 8, force: bool = False
    ) -> EvaluationResponse:
        # Robustesse : un appelant interne (ou un body avec item_count nul) ne doit
        # pas propager une valeur invalide jusqu'au prompt IA.
        if not isinstance(item_count, int) or not (4 <= item_count <= 20):
            item_count = 8
        note = self._get_note_or_403(note_id, user_id)
        content_hash = hashlib.sha256((note.content or "").encode("utf-8")).hexdigest()

        # Cache : tant que le contenu de la note n'a pas changé, on réutilise les
        # items déjà générés (clone d'une nouvelle tentative) sans rappeler l'IA.
        if not force:
            prior = self._evaluation_dao.get_latest_by_content_hash(note._id, user_id, content_hash)
            if prior is not None:
                cloned = self._clone_as_new_attempt(prior)
                return self._serialize(cloned, reveal=False)

        ai_result = self._ai_service.generate_evaluation(note.content or "", item_count=item_count)

        evaluation = Evaluation(note_id=note._id, user_id=user_id, content_hash=content_hash)

        # Items IA (clé de correction embarquée dans le payload).
        for raw in ai_result.get("items", []):
            item_type = raw.get("type")
            if item_type not in _VALID_TYPES:
                continue
            payload = {k: v for k, v in raw.items() if k != "type"}
            evaluation.items.append(EvaluationItem(type=item_type, source="ai", payload=payload))

        # Items issus des balises de la note (corrigés automatiquement, sans IA).
        for ph in extract_placeholders_from_text(note.content or "", note._id):
            converted = placeholder_to_eval_item(ph)
            if converted:
                t, payload = converted
                evaluation.items.append(EvaluationItem(type=t, source="manual", payload=payload))

        created = self._evaluation_dao.create(evaluation)
        return self._serialize(created, reveal=False)

    def has_valid_cache(self, user_id: int, note_id) -> bool:
        """Lecture seule : une évaluation réutilisable existe-t-elle pour le contenu
        actuel de la note ? Sert à exempter les cache-hits du rate-limit Gemini."""
        note = self._note_dao.get_by_id(note_id)
        if not note or note.user_id != user_id:
            return False
        content_hash = hashlib.sha256((note.content or "").encode("utf-8")).hexdigest()
        return (
            self._evaluation_dao.get_latest_by_content_hash(note._id, user_id, content_hash)
            is not None
        )

    def _clone_as_new_attempt(self, prior: Evaluation) -> Evaluation:
        clone = Evaluation(
            note_id=prior.note_id, user_id=prior.user_id, content_hash=prior.content_hash
        )
        for it in prior.items:
            # Copie du payload (pas de partage de référence entre items source et clone).
            clone.items.append(
                EvaluationItem(type=it.type, source=it.source, payload=dict(it.payload))
            )
        return self._evaluation_dao.create(clone)

    # --- Lecture / réponse / complétion ---

    def get_evaluation(self, user_id: int, evaluation_id: int) -> EvaluationResponse:
        evaluation = self._get_eval_or_403(evaluation_id, user_id)
        return self._serialize(evaluation, reveal=evaluation.completed_at is not None)

    def answer_item(
        self,
        user_id: int,
        evaluation_id: int,
        item_id: int,
        value: Any,
        self_grade: Optional[str],
    ) -> EvaluationAnswerResponse:
        evaluation = self._get_eval_or_403(evaluation_id, user_id)
        if evaluation.completed_at is not None:
            raise ForbiddenError("Cette évaluation est déjà complétée.")

        item = self._evaluation_dao.get_item(item_id)
        if not item or item.evaluation_id != evaluation.id:
            raise ResourceNotFoundError("Item introuvable dans cette évaluation.")

        is_correct, user_answer = self._grade(item.type, item.payload, value, self_grade)
        item.user_answer = user_answer
        item.is_correct = is_correct
        self._evaluation_dao.save_item(item)

        return EvaluationAnswerResponse(
            item_id=item.id,
            is_correct=is_correct,
            correction=self._correction(item.type, item.payload),
        )

    def complete_evaluation(self, user_id: int, evaluation_id: int) -> EvaluationResponse:
        evaluation = self._get_eval_or_403(evaluation_id, user_id)
        if evaluation.completed_at is None:
            total = len(evaluation.items)
            correct = sum(1 for it in evaluation.items if it.is_correct)
            evaluation.score_pct = (correct / total * 100) if total else 0.0
            evaluation.completed_at = datetime.utcnow()
            self._evaluation_dao.update(evaluation)
            # Bouclage SM-2 : les items ratés deviennent des flashcards révisables.
            self._reinforce_missed_items(evaluation)
        return self._serialize(evaluation, reveal=True)

    # --- Bouclage SM-2 ---

    def _reinforce_missed_items(self, evaluation: Evaluation) -> int:
        """Crée des flashcards (source='ai') dans le deck fantôme de la note pour
        chaque item raté, afin de les réviser en répétition espacée. Idempotent
        via un hash de contenu : pas de doublon entre tentatives."""
        if not self._deck_dao or not self._flashcard_dao:
            return 0

        note = self._note_dao.get_by_id(evaluation.note_id)
        if not note:
            return 0

        deck = self._find_or_create_phantom_deck(note)
        existing_hashes = {
            c.placeholder_hash
            for c in self._flashcard_dao.db.query(Flashcard)
            .filter_by(deck_id=deck.id)
            .all()
            if c.placeholder_hash
        }

        created = 0
        for it in evaluation.items:
            if it.is_correct is not False:  # on ne renforce que les items ratés
                continue
            front, back = self._card_front_back(it.type, it.payload)
            if not front or not back:
                continue
            p_hash = hashlib.sha256(
                f"eval:{note._id}:{it.type}:{front}".encode("utf-8")
            ).hexdigest()
            if p_hash in existing_hashes:
                continue
            self._flashcard_dao.create(
                Flashcard(
                    deck_id=deck.id,
                    front=front,
                    back=back,
                    source="ai",
                    placeholder_hash=p_hash,
                    original_text=f"[eval:{evaluation.id}]",
                )
            )
            existing_hashes.add(p_hash)
            created += 1
        return created

    def _find_or_create_phantom_deck(self, note) -> Deck:
        deck = self._deck_dao.db.query(Deck).filter_by(note_id=note._id).first()
        if deck:
            return deck
        deck = Deck(
            name=f"[Phantom] Note: {note.title}",
            description=f"Deck de révision active pour la note: {note.title}",
            user_id=note.user_id,
            note_id=note._id,
            binder_id=note.binder_id,
        )
        return self._deck_dao.create(deck)

    def _card_front_back(self, item_type: str, payload: Dict[str, Any]):
        if item_type == "qcm":
            correct = next((o for o in payload.get("options", []) if o.get("correct")), None)
            return payload.get("question"), (correct.get("text") if correct else None)
        if item_type == "vf":
            verdict = "Vrai" if payload.get("correct") else "Faux"
            justification = payload.get("justification") or ""
            back = f"{verdict} — {justification}".strip(" —")
            return f"Vrai ou Faux : {payload.get('assertion')}", back
        if item_type == "trou":
            return payload.get("text_with_blank"), payload.get("answer")
        if item_type == "open":
            return payload.get("question"), payload.get("model_answer")
        return None, None

    # --- Correction (par type) ---

    def _grade(
        self, item_type: str, payload: Dict[str, Any], value: Any, self_grade: Optional[str]
    ) -> Tuple[Optional[bool], Dict[str, Any]]:
        user_answer: Dict[str, Any] = {"value": value}
        if self_grade is not None:
            user_answer["self_grade"] = self_grade

        if item_type == "qcm":
            correct_id = next((o["id"] for o in payload.get("options", []) if o.get("correct")), None)
            return (value == correct_id), user_answer
        if item_type == "vf":
            return (bool(value) == bool(payload.get("correct"))), user_answer
        if item_type == "trou":
            return (_normalize(str(value or "")) == _normalize(str(payload.get("answer", "")))), user_answer
        if item_type == "open":
            # Auto-évaluation de l'étudiant face à la réponse-modèle révélée.
            return (self_grade == "acquired"), user_answer
        return None, user_answer

    def _correction(self, item_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if item_type == "qcm":
            return {
                "correct_option_id": next(
                    (o["id"] for o in payload.get("options", []) if o.get("correct")), None
                ),
                "options": payload.get("options", []),
            }
        if item_type == "vf":
            return {"correct": payload.get("correct"), "justification": payload.get("justification")}
        if item_type == "trou":
            return {"answer": payload.get("answer")}
        if item_type == "open":
            return {"model_answer": payload.get("model_answer"), "key_points": payload.get("key_points", [])}
        return {}

    def _sanitize_payload(self, item_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Vue question : retire les clés de correction pour éviter la triche."""
        if item_type == "qcm":
            return {
                "question": payload.get("question"),
                "options": [{"id": o.get("id"), "text": o.get("text")} for o in payload.get("options", [])],
            }
        if item_type == "vf":
            return {"assertion": payload.get("assertion")}
        if item_type == "trou":
            return {"text_with_blank": payload.get("text_with_blank")}
        if item_type == "open":
            return {"question": payload.get("question")}
        return dict(payload)

    # --- Sérialisation ---

    def _serialize(self, evaluation: Evaluation, reveal: bool) -> EvaluationResponse:
        items = []
        for it in evaluation.items:
            payload = dict(it.payload) if reveal else self._sanitize_payload(it.type, it.payload)
            items.append(
                EvaluationItemResponse(
                    id=it.id,
                    type=it.type,
                    source=it.source,
                    payload=payload,
                    user_answer=it.user_answer,
                    is_correct=it.is_correct if reveal else None,
                )
            )
        return EvaluationResponse(
            id=evaluation.id,
            note_id=evaluation.note_uuid,
            user_id=evaluation.user_id,
            score_pct=evaluation.score_pct,
            created_at=evaluation.created_at,
            completed_at=evaluation.completed_at,
            items=items,
        )
