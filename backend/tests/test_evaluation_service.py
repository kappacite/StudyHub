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


def _make_deck(user_id, name="Mes révisions"):
    deck = Deck(user_id=user_id, name=name)
    db.session.add(deck)
    db.session.commit()
    return deck.id


def _deck_cards(deck_id):
    return db.session.query(Flashcard).filter_by(deck_id=deck_id).all()


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


def test_generate_clamps_invalid_item_count(app):
    user_id, note_uuid = _make_user_note(app)
    with app.app_context():
        service, ai = _service()
        # item_count nul/hors-bornes ne doit jamais atteindre le prompt IA tel quel.
        service.generate_evaluation(user_id, note_uuid, item_count=None, force=True)  # type: ignore[arg-type]
        assert ai.generate_evaluation.call_args.kwargs["item_count"] == 8

        service.generate_evaluation(user_id, note_uuid, item_count=999, force=True)
        assert ai.generate_evaluation.call_args.kwargs["item_count"] == 8


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


def test_completion_proposes_missed_items_without_creating_cards(app):
    user_id, note_uuid = _make_user_note(app)
    with app.app_context():
        service, _ = _service_full()
        resp = service.generate_evaluation(user_id, note_uuid)
        qcm = next(i for i in resp.items if i.type == "qcm" and i.source == "ai")
        open_ai = next(i for i in resp.items if i.type == "open" and i.source == "ai")

        # QCM raté (mauvaise option), open auto-évalué 'acquired' (réussi)
        service.answer_item(user_id, resp.id, qcm.id, value="a", self_grade=None)
        service.answer_item(user_id, resp.id, open_ai.id, value="x", self_grade="acquired")
        result = service.complete_evaluation(user_id, resp.id)

        # On PROPOSE des cartes pour les items ratés ; rien n'est créé en base.
        fronts = [c.front for c in result.proposed_cards]
        assert "Capitale de la France ?" in fronts
        backs = {c.front: c.back for c in result.proposed_cards}
        assert backs["Capitale de la France ?"] == "Paris"  # bonne réponse
        assert "Expliquez la photosynthèse." not in fronts  # réussi -> pas de proposition

        # Aucune flashcard n'a été persistée automatiquement.
        assert db.session.query(Flashcard).count() == 0


def test_create_flashcards_from_missed_adds_to_chosen_deck(app):
    user_id, note_uuid = _make_user_note(app)
    with app.app_context():
        service, _ = _service_full()
        resp = service.generate_evaluation(user_id, note_uuid)
        qcm = next(i for i in resp.items if i.type == "qcm" and i.source == "ai")
        service.answer_item(user_id, resp.id, qcm.id, value="a", self_grade=None)
        service.complete_evaluation(user_id, resp.id)

        deck_id = _make_deck(user_id)
        created = service.create_flashcards_from_missed(user_id, resp.id, [qcm.id], deck_id)
        assert created == 1
        cards = _deck_cards(deck_id)
        assert len(cards) == 1
        assert cards[0].front == "Capitale de la France ?"
        assert cards[0].back == "Paris"
        assert cards[0].source == "ai"

        # Idempotent : ré-ajouter les mêmes items au même deck ne duplique pas.
        again = service.create_flashcards_from_missed(user_id, resp.id, [qcm.id], deck_id)
        assert again == 0
        assert len(_deck_cards(deck_id)) == 1


def test_create_flashcards_rejects_foreign_deck(app):
    user_id, note_uuid = _make_user_note(app)
    other_id, _ = _make_user_note(app, email="other2@example.com", username="other2")
    with app.app_context():
        service, _ = _service_full()
        resp = service.generate_evaluation(user_id, note_uuid)
        qcm = next(i for i in resp.items if i.type == "qcm" and i.source == "ai")
        service.answer_item(user_id, resp.id, qcm.id, value="a", self_grade=None)
        service.complete_evaluation(user_id, resp.id)

        foreign_deck_id = _make_deck(other_id)
        with pytest.raises(ForbiddenError):
            service.create_flashcards_from_missed(user_id, resp.id, [qcm.id], foreign_deck_id)


def test_user_isolation_on_get(app):
    owner_id, note_uuid = _make_user_note(app)
    other_id, _ = _make_user_note(app, email="other@example.com", username="other")
    with app.app_context():
        service, _ = _service()
        resp = service.generate_evaluation(owner_id, note_uuid)
        with pytest.raises(ForbiddenError):
            service.get_evaluation(other_id, resp.id)


def test_duplicate_items_are_deduplicated(app):
    """L'IA répète parfois une question (variantes quasi-identiques) : on n'en garde qu'une."""
    user_id, note_uuid = _make_user_note(app, content="Cours sans balise.", email="dup@example.com", username="dup")
    dup_ai = {"items": [
        {"type": "open", "question": "Expliquez la photosynthèse.", "model_answer": "x", "key_points": []},
        {"type": "open", "question": "Expliquez la photosynthèse.", "model_answer": "y", "key_points": []},
        {"type": "open", "question": "  expliquez la photosynthèse ?  ", "model_answer": "z", "key_points": []},
        {"type": "vf", "assertion": "L'eau bout à 100°C.", "correct": True, "justification": "x"},
    ]}
    with app.app_context():
        service, _ = _service(dup_ai)
        resp = service.generate_evaluation(user_id, note_uuid, item_count=4)
        opens = [i for i in resp.items if i.type == "open"]
        assert len(opens) == 1  # les 3 variantes fusionnées
        assert len(resp.items) == 2  # 1 open + 1 vf


def test_ordre_and_assoc_open_questions_expose_elements(app):
    """Les balises ordre/assoc deviennent des items 'open' dont l'ÉNONCÉ liste les
    éléments (sinon l'étudiant ne voit qu'un titre sans rien à ordonner/associer)."""
    content = (
        "{{ordre::Cycle de l'eau::Évaporation > Condensation > Précipitation}}\n"
        "{{assoc::Capitales::France=Paris | Espagne=Madrid}}"
    )
    user_id, note_uuid = _make_user_note(app, content=content, email="oa@example.com", username="oa")
    with app.app_context():
        service, _ = _service({"items": []})  # uniquement les items issus des balises
        resp = service.generate_evaluation(user_id, note_uuid, item_count=4)
        opens = [i for i in resp.items if i.type == "open"]
        assert len(opens) == 2
        joined = " ".join(i.payload["question"] for i in opens)
        for step in ("Évaporation", "Condensation", "Précipitation"):
            assert step in joined
        for el in ("France", "Espagne", "Paris", "Madrid"):
            assert el in joined
