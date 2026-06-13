from datetime import datetime, timedelta

from app.extensions import db
from app.models.binder import Binder
from app.models.deck import Deck
from app.models.flashcard import Flashcard
from app.models.note import Note
from app.models.quiz import Quiz, QuizQuestion
from app.models.exam import ExamSession


def _binder_with_card(app, user_id):
    with app.app_context():
        binder = Binder(user_id=user_id, name="Classeur Exam")
        db.session.add(binder)
        db.session.commit()
        deck = Deck(user_id=user_id, name="Deck Exam", binder_id=binder._id)
        db.session.add(deck)
        db.session.commit()
        db.session.add(Flashcard(deck_id=deck.id, front="Front", back="Back"))
        db.session.commit()
        return binder.id, deck.id  # binder.id = UUID utilisé par l'API


def test_start_exam_creates_session_with_snapshot(client, auth_headers, test_user, app):
    binder_id, _ = _binder_with_card(app, test_user["id"])
    resp = client.post("/api/v1/exam/start", json={"binder_id": binder_id}, headers=auth_headers)
    assert resp.status_code == 201
    session_id = resp.json["id"]
    assert len(resp.json["items"]) == 1

    with app.app_context():
        session = db.session.get(ExamSession, session_id)
        assert session.items_snapshot is not None
        assert len(session.items_snapshot) == 1
        assert session.items_snapshot[0]["item_type"] == "flashcard"


def test_exam_snapshot_immutable_after_start(client, auth_headers, test_user, app):
    binder_id, deck_id = _binder_with_card(app, test_user["id"])
    start = client.post("/api/v1/exam/start", json={"binder_id": binder_id}, headers=auth_headers)
    session_id = start.json["id"]
    assert len(start.json["items"]) == 1

    # Ajouter une carte au deck APRÈS le démarrage ne doit pas modifier le snapshot.
    with app.app_context():
        db.session.add(Flashcard(deck_id=deck_id, front="Nouvelle", back="Carte"))
        db.session.commit()

    with app.app_context():
        session = db.session.get(ExamSession, session_id)
        assert len(session.items_snapshot) == 1


def test_complete_exam_calculates_composite_score(client, auth_headers, test_user, app):
    with app.app_context():
        binder = Binder(user_id=test_user["id"], name="Classeur Composite")
        db.session.add(binder)
        db.session.commit()
        binder_id = binder.id
        note = Note(user_id=test_user["id"], binder_id=binder._id, title="N", content="c")
        db.session.add(note)
        db.session.commit()
        quiz = Quiz(note_id=note._id, user_id=test_user["id"])
        db.session.add(quiz)
        db.session.commit()
        db.session.add(QuizQuestion(quiz_id=quiz.id, question_text="Q ?", options=[
            {"id": "a", "text": "x", "correct": True},
            {"id": "b", "text": "y", "correct": False},
        ]))
        deck = Deck(user_id=test_user["id"], name="D", binder_id=binder._id)
        db.session.add(deck)
        db.session.commit()
        db.session.add(Flashcard(deck_id=deck.id, front="f", back="b"))
        db.session.commit()

    start = client.post("/api/v1/exam/start", json={"binder_id": binder_id}, headers=auth_headers).json
    session_id = start["id"]
    for item in start["items"]:
        if item["item_type"] == "qcm":
            client.post(f"/api/v1/exam/{session_id}/questions/{item['id']}/answer",
                        json={"answer": "a"}, headers=auth_headers)  # juste
        else:
            client.post(f"/api/v1/exam/{session_id}/questions/{item['id']}/answer",
                        json={"answer": "incorrect"}, headers=auth_headers)  # faux

    resp = client.post(f"/api/v1/exam/{session_id}/complete", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json["qcm_score"] == 100.0
    assert resp.json["flashcard_score"] == 0.0
    assert resp.json["score_pct"] == 50.0


def test_exam_expired_session_rejected(client, auth_headers, test_user, app):
    binder_id, _ = _binder_with_card(app, test_user["id"])
    start = client.post("/api/v1/exam/start",
                        json={"binder_id": binder_id, "duration_minutes": 15},
                        headers=auth_headers).json
    session_id = start["id"]
    item_id = start["items"][0]["id"]

    # Forcer l'expiration en reculant started_at au-delà de la durée (15 min).
    with app.app_context():
        session = db.session.get(ExamSession, session_id)
        session.started_at = datetime.utcnow() - timedelta(minutes=20)
        db.session.commit()

    resp = client.post(f"/api/v1/exam/{session_id}/questions/{item_id}/answer",
                       json={"answer": "correct"}, headers=auth_headers)
    assert resp.status_code == 403
