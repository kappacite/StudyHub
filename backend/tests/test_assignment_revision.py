"""Tests B3 — devoirs ciblant un ensemble de révision typé (qcm/vf/…)."""
from datetime import datetime
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


def _make_class_with_student(client, teacher_headers, app, student_email):
    resp = client.post("/api/v1/classes", json={"name": "Classe Révision"}, headers=teacher_headers)
    class_id, invite_code = resp.json["id"], resp.json["invite_code"]
    student_id = _create_user(app, student_email, student_email.split("@")[0])
    student_headers = _login(client, student_email)
    client.post("/api/v1/groups/join", json={"invite_code": invite_code}, headers=student_headers)
    return class_id, student_id, student_headers


def _qcm_set_with_item(client, headers):
    set_id = client.post("/api/v1/revision/sets", json={"name": "QCM Bio", "type": "qcm"}, headers=headers).json["id"]
    item = client.post(f"/api/v1/revision/sets/{set_id}/items", json={"payload": {
        "question": "ADN ?",
        "options": [{"id": "a", "text": "Acide", "correct": True}, {"id": "b", "text": "Base", "correct": False}],
    }}, headers=headers).json
    return set_id, item


def test_create_revision_task_targets_set(client, auth_headers, app):
    class_id, _, _ = _make_class_with_student(client, auth_headers, app, "rev1@test.com")
    set_id, _ = _qcm_set_with_item(client, auth_headers)

    resp = client.post(f"/api/v1/classes/{class_id}/assignments", json={
        "title": "Faire le QCM",
        "tasks": [{"task_type": "revision", "ref": str(set_id), "goal": {"min_items": 1}}],
    }, headers=auth_headers)
    assert resp.status_code == 201
    task = resp.json["tasks"][0]
    assert task["task_type"] == "revision"
    assert task["ref_id"] == set_id
    assert task["ref_label"] == "QCM Bio"


def test_revision_task_completion_derived_from_study(client, auth_headers, app):
    class_id, student_id, student_headers = _make_class_with_student(
        client, auth_headers, app, "rev2@test.com")
    set_id, item = _qcm_set_with_item(client, auth_headers)

    asgn = client.post(f"/api/v1/classes/{class_id}/assignments", json={
        "title": "Réviser l'ensemble",
        "tasks": [{"task_type": "revision", "ref": str(set_id), "goal": {"min_items": 1}}],
    }, headers=auth_headers).json
    asgn_id, task_id = asgn["id"], asgn["tasks"][0]["id"]

    # Avant étude : todo
    mine = client.get("/api/v1/assignments/mine", headers=student_headers).json
    assert next(a for a in mine if a["id"] == asgn_id)["tasks"][0]["my_status"] == "todo"

    # L'élève étudie l'item (session SM-2 réussie sur l'item de l'ensemble).
    from app.models.study_session import StudySession
    with app.app_context():
        db.session.add(StudySession(
            user_id=student_id, module="flashcard", item_id=item["id"], item_type="qcm",
            grade=5, cards_reviewed=1, cards_correct=1, created_at=datetime.utcnow(),
        ))
        db.session.commit()

    sub = client.post(
        f"/api/v1/classes/{class_id}/assignments/{asgn_id}/tasks/{task_id}/submit",
        json={}, headers=student_headers)
    assert sub.status_code == 200
    assert sub.json["my_status"] == "done"


def test_revision_task_cannot_target_other_users_set(client, auth_headers, app):
    class_id, _, student_headers = _make_class_with_student(
        client, auth_headers, app, "rev3@test.com")
    # Ensemble appartenant à l'élève, pas au prof.
    other_set, _ = _qcm_set_with_item(client, student_headers)

    resp = client.post(f"/api/v1/classes/{class_id}/assignments", json={
        "title": "Illégitime",
        "tasks": [{"task_type": "revision", "ref": str(other_set)}],
    }, headers=auth_headers)
    assert resp.status_code == 404
