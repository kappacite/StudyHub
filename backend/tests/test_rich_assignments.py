"""
Tests PR2 — Devoirs riches multi-supports.

Couvre :
  - création d'un devoir multi-tâches (flashcards + quiz + read) ;
  - exposition des tâches côté élève (/assignments/mine) ;
  - soumission d'une tâche de lecture → done ;
  - complétion d'une tâche quiz dérivée de l'état du module ;
  - validation : devoir sans cible rejeté ;
  - isolation : une tâche ne peut cibler une ressource d'un autre utilisateur.
"""
from datetime import datetime, timedelta
from app.models.user import User
from app.extensions import db


def _create_user(app, email, username):
    with app.app_context():
        u = User(email=email, username=username)
        u.set_password("password123")
        db.session.add(u)
        db.session.commit()
        db.session.refresh(u)
        return u.id


def _login(client, email, password="password123"):
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {resp.json['access_token']}"}


def _create_binder(client, headers, name="Cours"):
    resp = client.post("/api/v1/binders", json={"name": name}, headers=headers)
    assert resp.status_code == 201
    return resp.json["id"]


def _create_note(client, headers, title="Note", binder_id=None):
    body = {"title": title, "content": "Contenu"}
    if binder_id:
        body["binder_id"] = binder_id
    resp = client.post("/api/v1/notes", json=body, headers=headers)
    assert resp.status_code == 201
    return resp.json["id"]


def _make_class_with_student(client, teacher_headers, app, student_email):
    resp = client.post("/api/v1/classes", json={"name": "Classe Riche"}, headers=teacher_headers)
    class_id = resp.json["id"]
    invite_code = resp.json["invite_code"]
    student_id = _create_user(app, student_email, student_email.split("@")[0])
    student_headers = _login(client, student_email)
    client.post("/api/v1/groups/join", json={"invite_code": invite_code}, headers=student_headers)
    return class_id, student_id, student_headers


def test_create_multitask_assignment(client, auth_headers, app):
    class_id, student_id, student_headers = _make_class_with_student(
        client, auth_headers, app, "rich1@test.com")

    binder_id = _create_binder(client, auth_headers, "Bio")
    note_id = _create_note(client, auth_headers, "Mitose")

    resp = client.post(f"/api/v1/classes/{class_id}/assignments", json={
        "title": "Révision complète",
        "tasks": [
            {"task_type": "flashcards", "ref": binder_id, "goal": {"min_cards": 5}},
            {"task_type": "quiz", "ref": note_id},
            {"task_type": "read", "ref": note_id},
        ],
        "due_date": (datetime.utcnow() + timedelta(days=4)).isoformat(),
    }, headers=auth_headers)

    assert resp.status_code == 201
    data = resp.json
    assert len(data["tasks"]) == 3
    types = [t["task_type"] for t in data["tasks"]]
    assert types == ["flashcards", "quiz", "read"]
    # binder_id « principal » dérivé de la tâche flashcards (rétro-compat affichage)
    assert data["binder_id"] == binder_id
    # le goal est conservé
    fc = next(t for t in data["tasks"] if t["task_type"] == "flashcards")
    assert fc["goal"]["min_cards"] == 5


def test_student_sees_tasks_and_can_complete_read(client, auth_headers, app):
    class_id, student_id, student_headers = _make_class_with_student(
        client, auth_headers, app, "rich2@test.com")
    note_id = _create_note(client, auth_headers, "Lecture")

    asgn = client.post(f"/api/v1/classes/{class_id}/assignments", json={
        "title": "Lire le cours",
        "tasks": [{"task_type": "read", "ref": note_id}],
    }, headers=auth_headers).json
    asgn_id = asgn["id"]
    task_id = asgn["tasks"][0]["id"]

    # L'élève voit la tâche dans ses devoirs, statut todo
    mine = client.get("/api/v1/assignments/mine", headers=student_headers).json
    target = next(a for a in mine if a["id"] == asgn_id)
    assert len(target["tasks"]) == 1
    assert target["tasks"][0]["my_status"] == "todo"
    assert target["status"] == "todo"

    # L'élève soumet la tâche de lecture → done
    sub = client.post(
        f"/api/v1/classes/{class_id}/assignments/{asgn_id}/tasks/{task_id}/submit",
        json={}, headers=student_headers)
    assert sub.status_code == 200
    assert sub.json["my_status"] == "done"

    # Le devoir entier devient terminé (une seule tâche, faite)
    mine2 = client.get("/api/v1/assignments/mine", headers=student_headers).json
    target2 = next(a for a in mine2 if a["id"] == asgn_id)
    assert target2["status"] == "done"


def test_quiz_task_completion_derived_from_module(client, auth_headers, app):
    """Une tâche quiz devient 'done' quand l'élève a complété un quiz sur la note."""
    from app.models.note import Note
    from app.models.quiz import Quiz

    class_id, student_id, student_headers = _make_class_with_student(
        client, auth_headers, app, "rich3@test.com")
    note_id = _create_note(client, auth_headers, "Quiz source")

    asgn = client.post(f"/api/v1/classes/{class_id}/assignments", json={
        "title": "Passe le QCM",
        "tasks": [{"task_type": "quiz", "ref": note_id}],
    }, headers=auth_headers).json
    asgn_id = asgn["id"]
    task_id = asgn["tasks"][0]["id"]

    # Simuler un quiz complété par l'élève sur cette note.
    with app.app_context():
        note = db.session.query(Note).filter_by(id=note_id).first()
        quiz = Quiz(note_id=note._id, user_id=student_id,
                    score_pct=88.0, completed_at=datetime.utcnow())
        db.session.add(quiz)
        db.session.commit()

    sub = client.post(
        f"/api/v1/classes/{class_id}/assignments/{asgn_id}/tasks/{task_id}/submit",
        json={}, headers=student_headers)
    assert sub.status_code == 200
    assert sub.json["my_status"] == "done"
    assert sub.json["my_score_pct"] == 88.0


def test_assignment_requires_target(client, auth_headers, app):
    resp = client.post("/api/v1/classes", json={"name": "Vide"}, headers=auth_headers)
    class_id = resp.json["id"]
    bad = client.post(f"/api/v1/classes/{class_id}/assignments", json={
        "title": "Sans cible",
    }, headers=auth_headers)
    assert bad.status_code == 400


def test_task_cannot_target_other_users_resource(client, auth_headers, app):
    """Le prof ne peut pas cibler la note d'un autre utilisateur."""
    class_id, student_id, student_headers = _make_class_with_student(
        client, auth_headers, app, "rich4@test.com")
    # Note appartenant à l'élève, pas au prof
    student_note = _create_note(client, student_headers, "Note privée élève")

    resp = client.post(f"/api/v1/classes/{class_id}/assignments", json={
        "title": "Devoir illégitime",
        "tasks": [{"task_type": "read", "ref": student_note}],
    }, headers=auth_headers)
    assert resp.status_code == 404
