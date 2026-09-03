"""notes-ia-planning-corrections, Task 12 : persistance de la Notation IA --
une NoteGrade par note, ecrasee a la reevaluation (pas d'historique, meme patron
que Evaluation)."""

from app.extensions import db
from app.dao.note_grade_dao import NoteGradeDAO
from app.models.note import Note
from app.models.note_grade import NoteGrade


def _make_note(app, user_id):
    with app.app_context():
        note = Note(user_id=user_id, title="Note", content="Contenu")
        db.session.add(note)
        db.session.commit()
        return note._id


def test_get_by_note_returns_none_when_no_grade_yet(app, test_user):
    with app.app_context():
        note_internal_id = _make_note(app, test_user["id"])
        dao = NoteGradeDAO(db.session)
        assert dao.get_by_note(note_internal_id) is None


def test_upsert_creates_then_overwrites_on_reevaluation(app, test_user):
    with app.app_context():
        note_internal_id = _make_note(app, test_user["id"])
        dao = NoteGradeDAO(db.session)

        first = dao.upsert(note_internal_id, test_user["id"], {
            "score": 60, "verdict": "Correct.", "points_forts": ["A"],
            "ameliorations": ["B"], "suggestions": "Suggestion 1",
        })
        assert first.score == 60

        second = dao.upsert(note_internal_id, test_user["id"], {
            "score": 90, "verdict": "Excellent.", "points_forts": ["C", "D"],
            "ameliorations": [], "suggestions": "Suggestion 2",
        })
        assert second.id == first.id  # meme ligne ecrasee, pas de doublon
        assert second.score == 90
        assert second.ameliorations == []

        assert db.session.query(NoteGrade).filter_by(note_id=note_internal_id).count() == 1
