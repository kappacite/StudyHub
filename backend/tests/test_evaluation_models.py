from app.extensions import db
from app.models.user import User
from app.models.note import Note
from app.models.evaluation import Evaluation, EvaluationItem


def _make_user_and_note(app):
    with app.app_context():
        user = User(email="eval@example.com", username="evaluser")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        note = Note(user_id=user.id, title="Note Eval", content="Contenu du cours")
        db.session.add(note)
        db.session.commit()
        return user.id, note.id


def test_evaluation_persists_items_with_payload(app):
    user_id, note_id = _make_user_and_note(app)
    with app.app_context():
        evaluation = Evaluation(note_id=note_id, user_id=user_id, content_hash="abc123")
        evaluation.items.append(
            EvaluationItem(
                type="qcm",
                payload={
                    "question": "Capitale de la France ?",
                    "options": [
                        {"id": "a", "text": "Lyon", "correct": False},
                        {"id": "b", "text": "Paris", "correct": True},
                    ],
                },
            )
        )
        evaluation.items.append(
            EvaluationItem(
                type="open",
                payload={"question": "Expliquez X", "model_answer": "...", "key_points": ["a", "b"]},
            )
        )
        db.session.add(evaluation)
        db.session.commit()
        eval_id = evaluation.id

    with app.app_context():
        stored = db.session.get(Evaluation, eval_id)
        assert stored is not None
        assert stored.score_pct is None  # non complétée
        assert len(stored.items) == 2
        assert stored.items[0].type == "qcm"
        assert stored.items[0].source == "ai"  # défaut
        assert stored.items[0].payload["options"][1]["correct"] is True
        assert stored.items[1].payload["key_points"] == ["a", "b"]


def test_evaluation_cascade_deletes_items(app):
    user_id, note_id = _make_user_and_note(app)
    with app.app_context():
        evaluation = Evaluation(note_id=note_id, user_id=user_id)
        evaluation.items.append(EvaluationItem(type="vf", payload={"assertion": "x", "correct": True}))
        db.session.add(evaluation)
        db.session.commit()
        eval_id = evaluation.id

    with app.app_context():
        evaluation = db.session.get(Evaluation, eval_id)
        db.session.delete(evaluation)
        db.session.commit()

    with app.app_context():
        assert db.session.query(EvaluationItem).filter_by(evaluation_id=eval_id).count() == 0
