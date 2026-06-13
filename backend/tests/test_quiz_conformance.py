import json
import os
from unittest.mock import patch, MagicMock

import pytest

from app.extensions import db
from app.models.note import Note
from app.models.deck import Deck
from app.models.user import User
from app.services.ai_service import AIService

MOCK_QUESTIONS = [
    {"question": "Q1 ?", "options": [
        {"id": "a", "text": "x", "correct": False},
        {"id": "b", "text": "y", "correct": True},
        {"id": "c", "text": "z", "correct": False},
        {"id": "d", "text": "w", "correct": False}]},
    {"question": "Q2 ?", "options": [
        {"id": "a", "text": "x", "correct": True},
        {"id": "b", "text": "y", "correct": False},
        {"id": "c", "text": "z", "correct": False},
        {"id": "d", "text": "w", "correct": False}]},
]


def _make_note(app, user_id):
    with app.app_context():
        note = Note(user_id=user_id, title="Note QCM", content="Contenu de cours à réviser.")
        db.session.add(note)
        db.session.commit()
        return note.id


def _generate_quiz(client, headers, note_id, count=2):
    with patch("app.services.ai_service.AIService.generate_quiz", return_value=MOCK_QUESTIONS[:count]):
        return client.post(
            "/api/v1/quizzes/generate",
            json={"note_id": note_id, "question_count": count},
            headers=headers,
        )


def _login(client, email):
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    return {"Authorization": f"Bearer {r.json['access_token']}"}


def test_generate_quiz_creates_quiz_and_questions(client, auth_headers, test_user, app):
    note_id = _make_note(app, test_user["id"])
    resp = _generate_quiz(client, auth_headers, note_id, count=2)
    assert resp.status_code == 201
    assert resp.json["note_id"] == note_id
    assert len(resp.json["questions"]) == 2


def test_answer_question_returns_correct_flag(client, auth_headers, test_user, app):
    note_id = _make_note(app, test_user["id"])
    quiz = _generate_quiz(client, auth_headers, note_id, count=2).json
    q1, q2 = quiz["questions"]

    good = client.post(f"/api/v1/quizzes/{quiz['id']}/questions/{q1['id']}/answer",
                       json={"answer_id": "b"}, headers=auth_headers)
    assert good.status_code == 200
    assert good.json["is_correct"] is True
    assert good.json["correct_answer_id"] == "b"

    bad = client.post(f"/api/v1/quizzes/{quiz['id']}/questions/{q2['id']}/answer",
                      json={"answer_id": "b"}, headers=auth_headers)
    assert bad.json["is_correct"] is False
    assert bad.json["correct_answer_id"] == "a"


def test_complete_quiz_calculates_score(client, auth_headers, test_user, app):
    note_id = _make_note(app, test_user["id"])
    quiz = _generate_quiz(client, auth_headers, note_id, count=2).json
    q1, q2 = quiz["questions"]
    client.post(f"/api/v1/quizzes/{quiz['id']}/questions/{q1['id']}/answer",
                json={"answer_id": "b"}, headers=auth_headers)  # juste
    client.post(f"/api/v1/quizzes/{quiz['id']}/questions/{q2['id']}/answer",
                json={"answer_id": "b"}, headers=auth_headers)  # faux (correct = a)
    resp = client.post(f"/api/v1/quizzes/{quiz['id']}/complete", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json["score_pct"] == 50.0


def test_create_flashcards_from_wrong_answers(client, auth_headers, test_user, app):
    note_id = _make_note(app, test_user["id"])
    quiz = _generate_quiz(client, auth_headers, note_id, count=2).json
    with app.app_context():
        deck = Deck(user_id=test_user["id"], name="Deck QCM")
        db.session.add(deck)
        db.session.commit()
        deck_id = deck.id
    q1, q2 = quiz["questions"]
    client.post(f"/api/v1/quizzes/{quiz['id']}/questions/{q1['id']}/answer",
                json={"answer_id": "b"}, headers=auth_headers)  # juste
    client.post(f"/api/v1/quizzes/{quiz['id']}/questions/{q2['id']}/answer",
                json={"answer_id": "b"}, headers=auth_headers)  # faux
    client.post(f"/api/v1/quizzes/{quiz['id']}/complete", headers=auth_headers)

    resp = client.post(f"/api/v1/quizzes/{quiz['id']}/create-flashcards",
                       json={"deck_id": deck_id, "question_ids": [q1["id"], q2["id"]]},
                       headers=auth_headers)
    assert resp.status_code == 201
    # Seule la question ratée produit une flashcard.
    assert len(resp.json) == 1


def test_quiz_belongs_to_note_user_only(client, auth_headers, test_user, app):
    note_id = _make_note(app, test_user["id"])
    quiz = _generate_quiz(client, auth_headers, note_id).json

    with app.app_context():
        b = User(email="quizb@example.com", username="quizb")
        b.set_password("password123")
        db.session.add(b)
        db.session.commit()
    b_headers = _login(client, "quizb@example.com")

    # Un autre utilisateur ne peut pas accéder au quiz.
    assert client.get(f"/api/v1/quizzes/{quiz['id']}", headers=b_headers).status_code == 403


def test_generate_quiz_rate_limit_enforced(app):
    # Le rate limiting est désactivé globalement dans la config de test (sinon il
    # rendrait toute la suite flaky). On vérifie donc que la limite « 10 per hour »
    # est bien DÉCLARÉE par flask-limiter sur l'endpoint generate (conformité 7.2.6).
    from app.extensions import limiter

    decorated = limiter.limit_manager._decorated_limits
    key = next((k for k in decorated if "quizzes.generate_quiz" in k), None)
    assert key is not None, "Aucune limite déclarée sur l'endpoint quizzes.generate_quiz"
    providers = [str(lg.limit_provider) for lg in decorated[key]]
    assert any("10 per hour" in p for p in providers)


def test_ai_service_handles_gemini_invalid_json(app):
    os.environ.setdefault("GEMINI_API_KEY", "test-key")
    svc = AIService()

    fake_response = MagicMock()
    fake_response.read.return_value = json.dumps({
        "candidates": [{"content": {"parts": [{"text": "ceci n'est pas du JSON valide !"}]}}]
    }).encode("utf-8")
    fake_response.__enter__.return_value = fake_response
    fake_response.__exit__.return_value = False

    with patch("urllib.request.urlopen", return_value=fake_response):
        with pytest.raises(RuntimeError):
            svc.generate_quiz("contenu de cours", count=3)
