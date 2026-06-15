"""Tests B4 — questions des élèves (Q&A) dans une classe."""
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


def _class_with_student(client, teacher_headers, app, email):
    resp = client.post("/api/v1/classes", json={"name": "Classe QA"}, headers=teacher_headers)
    class_id, invite = resp.json["id"], resp.json["invite_code"]
    _create_user(app, email, email.split("@")[0])
    student_headers = _login(client, email)
    client.post("/api/v1/groups/join", json={"invite_code": invite}, headers=student_headers)
    return class_id, student_headers


def test_student_posts_question_teacher_sees_it(client, auth_headers, app):
    class_id, student_headers = _class_with_student(client, auth_headers, app, "qa1@test.com")

    posted = client.post(f"/api/v1/classes/{class_id}/questions",
                         json={"body": "Quelle est la différence entre mitose et méiose ?"},
                         headers=student_headers)
    assert posted.status_code == 201
    assert posted.json["status"] == "open"

    # Le professeur voit la question.
    teacher_list = client.get(f"/api/v1/classes/{class_id}/questions", headers=auth_headers).json
    assert len(teacher_list) == 1
    assert teacher_list[0]["body"].startswith("Quelle est la différence")

    # L'élève voit sa propre question.
    student_list = client.get(f"/api/v1/classes/{class_id}/questions", headers=student_headers).json
    assert len(student_list) == 1


def test_question_isolation_between_students(client, auth_headers, app):
    class_id, s1 = _class_with_student(client, auth_headers, app, "qa2a@test.com")
    _create_user(app, "qa2b@test.com", "qa2b")
    s2 = _login(client, "qa2b@test.com")
    client.post("/api/v1/groups/join",
                json={"invite_code": client.get("/api/v1/classes", headers=auth_headers).json[0]["invite_code"]},
                headers=s2)

    client.post(f"/api/v1/classes/{class_id}/questions", json={"body": "Question de S1"}, headers=s1)

    # S2 ne voit pas la question de S1.
    s2_list = client.get(f"/api/v1/classes/{class_id}/questions", headers=s2).json
    assert all(q["body"] != "Question de S1" for q in s2_list)


def test_teacher_answers_question(client, auth_headers, app):
    class_id, student_headers = _class_with_student(client, auth_headers, app, "qa3@test.com")
    q = client.post(f"/api/v1/classes/{class_id}/questions", json={"body": "Pourquoi ?"},
                    headers=student_headers).json

    ans = client.post(f"/api/v1/classes/{class_id}/questions/{q['id']}/answer",
                      json={"body": "Parce que."}, headers=auth_headers)
    assert ans.status_code == 200
    assert ans.json["status"] == "answered"
    assert ans.json["answer"] == "Parce que."

    # L'élève reçoit une notification de réponse.
    notifs = client.get("/api/v1/notifications", headers=student_headers).json
    assert any(n["type"] == "answer" for n in notifs)


def test_student_cannot_answer(client, auth_headers, app):
    class_id, student_headers = _class_with_student(client, auth_headers, app, "qa4@test.com")
    q = client.post(f"/api/v1/classes/{class_id}/questions", json={"body": "Q"},
                    headers=student_headers).json
    resp = client.post(f"/api/v1/classes/{class_id}/questions/{q['id']}/answer",
                       json={"body": "Tentative"}, headers=student_headers)
    assert resp.status_code == 403


def test_post_question_notifies_teacher(client, auth_headers, app):
    class_id, student_headers = _class_with_student(client, auth_headers, app, "qa5@test.com")
    client.post(f"/api/v1/classes/{class_id}/questions", json={"body": "Une question"}, headers=student_headers)

    notifs = client.get("/api/v1/notifications", headers=auth_headers).json
    assert any(n["type"] == "question" for n in notifs)
