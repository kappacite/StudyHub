import pytest
from unittest.mock import MagicMock

from app.extensions import db
from app.models.user import User
from app.models.note import Note
from app.models.deck import Deck
from app.models.flashcard import Flashcard
from app.dao.evaluation_dao import EvaluationDAO
from app.dao.note_dao import NoteDAO
from app.dao.deck_dao import DeckDAO
from app.dao.flashcard_dao import FlashcardDAO
from app.services.evaluation_service import EvaluationService
from app.middlewares.error_handler import ForbiddenError


AI_ITEMS = {
    "items": [
        {
            "type": "qcm",
            "question": "Capitale de la France ?",
            "options": [
                {"id": "a", "text": "Lyon", "correct": False},
                {"id": "b", "text": "Paris", "correct": True},
                {"id": "c", "text": "Nice", "correct": False},
                {"id": "d", "text": "Lille", "correct": False},
            ],
        },
        {"type": "vf", "assertion": "L'eau bout à 100°C.", "correct": True, "justification": "Au niveau de la mer."},
        {"type": "trou", "text_with_blank": "La cellule produit l'énergie dans la [...].", "answer": "Mitochondrie"},
        {"type": "open", "question": "Expliquez la photosynthèse.", "model_answer": "Lumière -> énergie chimique.", "key_points": ["lumière", "glucose"]},
    ]
}

# Note avec balises : un qcm (manual) + une définition (-> open manual)
NOTE_CONTENT = (
    "Introduction.\n"
    "{{qcm::Auteur des Misérables ?::Zola|*Victor Hugo*|Maupassant}}\n"
    "[ADN]{def:Acide désoxyribonucléique}"
)


def _make_user_note(app, content=NOTE_CONTENT, email="ev@example.com", username="ev"):
    with app.app_context():
        user = User(email=email, username=username)
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        note = Note(user_id=user.id, title="Cours", content=content)
        db.session.add(note)
        db.session.commit()
        return user.id, note.id  # note.id = uuid public


def _service(ai_return=AI_ITEMS):
    ai = MagicMock()
    ai.generate_evaluation.return_value = ai_return
    return EvaluationService(EvaluationDAO(db.session), NoteDAO(db.session), ai), ai


def _service_full(ai_return=AI_ITEMS):
    """Service avec deck/flashcard DAOs : active le bouclage SM-2."""
    ai = MagicMock()
    ai.generate_evaluation.return_value = ai_return
    service = EvaluationService(
        EvaluationDAO(db.session),
        NoteDAO(db.session),
        ai,
        deck_dao=DeckDAO(db.session),
        flashcard_dao=FlashcardDAO(db.session),
    )
    return service, ai


def _phantom_cards(note_uuid):
    note = NoteDAO(db.session).get_by_id(note_uuid)
    deck = db.session.query(Deck).filter_by(note_id=note._id).first()
    if not deck:
        return []
    return db.session.query(Flashcard).filter_by(deck_id=deck.id).all()


def test_generate_merges_ai_and_manual_items_sanitized(app):
    user_id, note_uuid = _make_user_note(app)
    with app.app_context():
        service, ai = _service()
        resp = service.generate_evaluation(user_id, note_uuid, item_count=4)

        ai.generate_evaluation.assert_called_once()
        # 4 items IA + 2 items balises (qcm + def->open)
        assert len(resp.items) == 6
        sources = sorted(set(i.source for i in resp.items))
        assert sources == ["ai", "manual"]

        # Vue question : aucune clé de correction ne fuit
        for it in resp.items:
            if it.type == "qcm":
                for opt in it.payload["options"]:
                    assert "correct" not in opt
            if it.type == "vf":
                assert "correct" not in it.payload
            if it.type == "trou":
                assert "answer" not in it.payload
            if it.type == "open":
                assert "model_answer" not in it.payload
            assert it.is_correct is None  # caché avant complétion


def test_cache_reuses_items_without_calling_ai_again(app):
    user_id, note_uuid = _make_user_note(app)
    with app.app_context():
        service, ai = _service()
        first = service.generate_evaluation(user_id, note_uuid)
        second = service.generate_evaluation(user_id, note_uuid)  # même contenu -> cache

        assert ai.generate_evaluation.call_count == 1  # IA non rappelée
        assert first.id != second.id  # nouvelle tentative (clone)
        assert len(second.items) == len(first.items)


def test_force_regenerates_calls_ai_again(app):
    user_id, note_uuid = _make_user_note(app)
    with app.app_context():
        service, ai = _service()
        service.generate_evaluation(user_id, note_uuid)
        service.generate_evaluation(user_id, note_uuid, force=True)
        assert ai.generate_evaluation.call_count == 2


def test_answer_and_complete_scores_each_type(app):
    user_id, note_uuid = _make_user_note(app)
    with app.app_context():
        service, _ = _service()
        resp = service.generate_evaluation(user_id, note_uuid)
        eval_id = resp.id
        by_type = {}
        for it in resp.items:
            by_type.setdefault(it.type, []).append(it)

        # QCM IA : bonne réponse 'b' (Paris)
        qcm_ai = next(i for i in by_type["qcm"] if i.source == "ai")
        a = service.answer_item(user_id, eval_id, qcm_ai.id, value="b", self_grade=None)
        assert a.is_correct is True
        assert a.correction["correct_option_id"] == "b"

        # VF : correct True
        vf = by_type["vf"][0]
        assert service.answer_item(user_id, eval_id, vf.id, value=True, self_grade=None).is_correct is True

        # Trou : normalisation tolérante (casse/accents)
        trou = by_type["trou"][0]
        assert service.answer_item(user_id, eval_id, trou.id, value="mitochondrie", self_grade=None).is_correct is True

        # Open : auto-évaluation 'acquired' => correct
        open_ai = next(i for i in by_type["open"] if i.source == "ai")
        assert service.answer_item(user_id, eval_id, open_ai.id, value="ma réponse", self_grade="acquired").is_correct is True

        result = service.complete_evaluation(user_id, eval_id)
        assert result.completed_at is not None
        # 4 corrects / 6 items
        assert round(result.score_pct, 1) == round(4 / 6 * 100, 1)
        # Après complétion, les corrections sont révélées
        revealed_qcm = next(i for i in result.items if i.id == qcm_ai.id)
        assert any(o.get("correct") for o in revealed_qcm.payload["options"])


def test_trou_wrong_answer_is_incorrect(app):
    user_id, note_uuid = _make_user_note(app)
    with app.app_context():
        service, _ = _service()
        resp = service.generate_evaluation(user_id, note_uuid)
        trou = next(i for i in resp.items if i.type == "trou")
        a = service.answer_item(user_id, resp.id, trou.id, value="noyau", self_grade=None)
        assert a.is_correct is False
        assert a.correction["answer"] == "Mitochondrie"


def test_completion_reinforces_missed_items_as_ai_cards(app):
    user_id, note_uuid = _make_user_note(app)
    with app.app_context():
        service, _ = _service_full()
        resp = service.generate_evaluation(user_id, note_uuid)
        qcm = next(i for i in resp.items if i.type == "qcm" and i.source == "ai")
        open_ai = next(i for i in resp.items if i.type == "open" and i.source == "ai")

        # QCM raté (mauvaise option), open auto-évalué 'acquired' (réussi)
        service.answer_item(user_id, resp.id, qcm.id, value="a", self_grade=None)
        service.answer_item(user_id, resp.id, open_ai.id, value="x", self_grade="acquired")
        service.complete_evaluation(user_id, resp.id)

        cards = _phantom_cards(note_uuid)
        ai_cards = [c for c in cards if c.source == "ai"]
        # Le QCM raté génère une carte ; l'item open réussi n'en génère pas.
        fronts = [c.front for c in ai_cards]
        assert "Capitale de la France ?" in fronts
        backs = {c.front: c.back for c in ai_cards}
        assert backs["Capitale de la France ?"] == "Paris"  # bonne réponse
        assert all(c.source == "ai" for c in ai_cards)
        assert "Expliquez la photosynthèse." not in fronts  # réussi -> pas de carte


def test_reinforcement_is_idempotent_across_attempts(app):
    user_id, note_uuid = _make_user_note(app)
    with app.app_context():
        service, _ = _service_full()

        # Tentative 1 : QCM raté -> 1 carte
        r1 = service.generate_evaluation(user_id, note_uuid)
        qcm1 = next(i for i in r1.items if i.type == "qcm" and i.source == "ai")
        service.answer_item(user_id, r1.id, qcm1.id, value="a", self_grade=None)
        service.complete_evaluation(user_id, r1.id)
        count1 = len([c for c in _phantom_cards(note_uuid) if c.front == "Capitale de la France ?"])
        assert count1 == 1

        # Tentative 2 (cache/clone) : même QCM raté -> pas de doublon
        r2 = service.generate_evaluation(user_id, note_uuid)
        qcm2 = next(i for i in r2.items if i.type == "qcm" and i.source == "ai")
        service.answer_item(user_id, r2.id, qcm2.id, value="a", self_grade=None)
        service.complete_evaluation(user_id, r2.id)
        count2 = len([c for c in _phantom_cards(note_uuid) if c.front == "Capitale de la France ?"])
        assert count2 == 1


def test_user_isolation_on_get(app):
    owner_id, note_uuid = _make_user_note(app)
    other_id, _ = _make_user_note(app, email="other@example.com", username="other")
    with app.app_context():
        service, _ = _service()
        resp = service.generate_evaluation(owner_id, note_uuid)
        with pytest.raises(ForbiddenError):
            service.get_evaluation(other_id, resp.id)
