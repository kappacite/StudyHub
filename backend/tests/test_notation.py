"""Tests de la route /api/v1/notation (notes-ia-planning-corrections, Task 4).
Le service IA (AIService.grade_note) est teste unitairement dans test_ai_service.py --
ici, contrat HTTP, validation, isolation user_id."""

from unittest.mock import patch

from app.extensions import db
from app.models.binder import Binder
from app.models.note import Note
from app.models.note_grade import NoteGrade


@patch("app.services.ai_service.AIService.grade_note")
def test_notation_grade_endpoint(mock_grade_note, client, auth_headers, test_user, app):
    mock_grade_note.return_value = {
        "score": 91,
        "verdict": "Excellente fiche.",
        "points_forts": ["Structure claire"],
        "ameliorations": [],
        "suggestions": "Rien à ajouter.",
    }

    with app.app_context():
        binder = Binder(user_id=test_user["id"], name="Classeur Notation")
        db.session.add(binder)
        db.session.commit()
        note = Note(user_id=test_user["id"], binder_id=binder.id, title="Note N", content="Contenu")
        db.session.add(note)
        db.session.commit()
        note_id = note.id

    resp = client.post("/api/v1/notation/grade", json={"note_id": note_id}, headers=auth_headers)

    assert resp.status_code == 202
    assert "task_id" in resp.json
    task_id = resp.json["task_id"]

    poll = client.get(f"/api/v1/notation/tasks/{task_id}", headers=auth_headers)
    assert poll.status_code == 200
    assert poll.json["status"] == "SUCCESS"
    assert poll.json["result"]["score"] == 91
    assert poll.json["result"]["verdict"] == "Excellente fiche."

    # notes-ia-planning-corrections, Task 12 : persistee, pas seulement renvoyee.
    with app.app_context():
        note = db.session.query(Note).filter_by(id=note_id).first()
        grade = db.session.query(NoteGrade).filter_by(note_id=note._id).first()
        assert grade is not None
        assert grade.score == 91


def test_notation_grade_requires_note_id(client, auth_headers):
    resp = client.post("/api/v1/notation/grade", json={}, headers=auth_headers)
    assert resp.status_code == 400


def test_notation_grade_forbidden_for_other_user_note(client, auth_headers, app):
    with app.app_context():
        from app.models.user import User
        other = User(email="other-notation@example.com", username="other_notation")
        other.set_password("password123")
        db.session.add(other)
        db.session.commit()
        binder = Binder(user_id=other.id, name="Pas a moi")
        db.session.add(binder)
        db.session.commit()
        note = Note(user_id=other.id, binder_id=binder.id, title="N", content="C")
        db.session.add(note)
        db.session.commit()
        note_id = note.id

    resp = client.post("/api/v1/notation/grade", json={"note_id": note_id}, headers=auth_headers)
    assert resp.status_code == 403


def test_notation_grade_note_not_found(client, auth_headers):
    resp = client.post("/api/v1/notation/grade", json={"note_id": 999999}, headers=auth_headers)
    assert resp.status_code == 404


# --- GET /api/v1/notation/<note_id> (Task 12, route get_existing_grade) -------------


def test_get_notation_404_when_not_yet_graded(client, auth_headers, test_user, app):
    with app.app_context():
        binder = Binder(user_id=test_user["id"], name="Classeur")
        db.session.add(binder)
        db.session.commit()
        note = Note(user_id=test_user["id"], binder_id=binder.id, title="N", content="C")
        db.session.add(note)
        db.session.commit()
        note_id = note.id

    resp = client.get(f"/api/v1/notation/{note_id}", headers=auth_headers)
    assert resp.status_code == 404


def test_get_notation_returns_existing_grade(client, auth_headers, test_user, app):
    with app.app_context():
        binder = Binder(user_id=test_user["id"], name="Classeur")
        db.session.add(binder)
        db.session.commit()
        note = Note(user_id=test_user["id"], binder_id=binder.id, title="N", content="C")
        db.session.add(note)
        db.session.commit()
        note_id = note.id
        note_internal_id = note._id
        grade = NoteGrade(
            note_id=note_internal_id, user_id=test_user["id"], score=75,
            verdict="Bien.", points_forts=["A"], ameliorations=["B"], suggestions="S",
        )
        db.session.add(grade)
        db.session.commit()

    resp = client.get(f"/api/v1/notation/{note_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json["score"] == 75
    assert resp.json["verdict"] == "Bien."


def test_get_notation_forbidden_for_other_user_note(client, auth_headers, app):
    with app.app_context():
        from app.models.user import User
        other = User(email="other-get-notation@example.com", username="other_get_notation")
        other.set_password("password123")
        db.session.add(other)
        db.session.commit()
        binder = Binder(user_id=other.id, name="Pas a moi")
        db.session.add(binder)
        db.session.commit()
        note = Note(user_id=other.id, binder_id=binder.id, title="N", content="C")
        db.session.add(note)
        db.session.commit()
        note_id = note.id

    resp = client.get(f"/api/v1/notation/{note_id}", headers=auth_headers)
    assert resp.status_code == 403


def test_get_notation_note_not_found(client, auth_headers):
    resp = client.get("/api/v1/notation/999999", headers=auth_headers)
    assert resp.status_code == 404
