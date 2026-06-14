"""
Tests PR3 — Analytics professeur, lacunes IA (data-driven) et notation.

Couvre :
  - vue d'ensemble agrégée + accès réservé au professeur ;
  - notation manuelle d'une soumission (+ interdiction élève) ;
  - lacunes de classe : POST recalcule (eager), GET renvoie le cache + résumé heuristique ;
  - budget de requêtes borné pour /analytics (pas de N+1).
"""
from datetime import datetime, timedelta
from app.models.user import User
from app.extensions import db
from app.utils.sql_profiler import assert_max_queries


def _create_user(app, email, username):
    with app.app_context():
        u = User(email=email, username=username)
        u.set_password("password123")
        db.session.add(u)
        db.session.commit()
        db.session.refresh(u)
        return u.id


def _login(client, email):
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    return {"Authorization": f"Bearer {resp.json['access_token']}"}


def _create_binder(client, headers, name="Cours"):
    return client.post("/api/v1/binders", json={"name": name}, headers=headers).json["id"]


def _create_note(client, headers, title="Note"):
    return client.post("/api/v1/notes", json={"title": title, "content": "x"}, headers=headers).json["id"]


def _class_with_student(client, teacher_headers, app, email):
    resp = client.post("/api/v1/classes", json={"name": "Classe Analytics"}, headers=teacher_headers)
    class_id, invite = resp.json["id"], resp.json["invite_code"]
    student_id = _create_user(app, email, email.split("@")[0])
    sh = _login(client, email)
    client.post("/api/v1/groups/join", json={"invite_code": invite}, headers=sh)
    return class_id, student_id, sh


def test_class_overview_aggregates(client, auth_headers, app):
    class_id, student_id, sh = _class_with_student(client, auth_headers, app, "an1@test.com")
    binder_id = _create_binder(client, auth_headers)
    client.post(f"/api/v1/classes/{class_id}/assignments", json={
        "title": "D1", "tasks": [{"task_type": "flashcards", "ref": binder_id}],
    }, headers=auth_headers)

    resp = client.get(f"/api/v1/classes/{class_id}/analytics", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json
    assert data["students_count"] == 1
    assert data["assignments_count"] == 1
    assert data["completion_rate"] == 0.0
    assert len(data["assignments"]) == 1
    assert data["assignments"][0]["submissions_count"] == 1

    # Élève interdit
    forbidden = client.get(f"/api/v1/classes/{class_id}/analytics", headers=sh)
    assert forbidden.status_code == 403


def test_grade_submission(client, auth_headers, app):
    class_id, student_id, sh = _class_with_student(client, auth_headers, app, "an2@test.com")
    binder_id = _create_binder(client, auth_headers)
    asgn = client.post(f"/api/v1/classes/{class_id}/assignments", json={
        "title": "D-note", "tasks": [{"task_type": "flashcards", "ref": binder_id}],
    }, headers=auth_headers).json
    asgn_id = asgn["id"]

    # Élève ne peut pas noter
    bad = client.patch(
        f"/api/v1/classes/{class_id}/assignments/{asgn_id}/submissions/{student_id}",
        json={"teacher_score": 90}, headers=sh)
    assert bad.status_code == 403

    # Professeur note + commente
    ok = client.patch(
        f"/api/v1/classes/{class_id}/assignments/{asgn_id}/submissions/{student_id}",
        json={"teacher_score": 17.5, "teacher_feedback": "Bon travail"}, headers=auth_headers)
    assert ok.status_code == 200
    assert ok.json["teacher_score"] == 17.5
    assert ok.json["teacher_feedback"] == "Bon travail"
    assert ok.json["graded_at"] is not None

    # Visible dans le détail du devoir
    detail = client.get(f"/api/v1/classes/{class_id}/assignments/{asgn_id}", headers=auth_headers)
    prog = next(p for p in detail.json["progress"] if p["user_id"] == student_id)
    assert prog["teacher_score"] == 17.5


def test_class_insights_weak_topics(client, auth_headers, app):
    from app.models.note import Note
    from app.models.evaluation import Evaluation, EvaluationItem

    class_id, student_id, sh = _class_with_student(client, auth_headers, app, "an3@test.com")
    note_id = _create_note(client, auth_headers, "Mitose difficile")

    # Simuler des réponses majoritairement fausses de l'élève sur cette note.
    with app.app_context():
        note = db.session.query(Note).filter_by(id=note_id).first()
        ev = Evaluation(note_id=note._id, user_id=student_id,
                        score_pct=20.0, completed_at=datetime.utcnow())
        db.session.add(ev)
        db.session.flush()
        for correct in (False, False, False, True):
            db.session.add(EvaluationItem(
                evaluation_id=ev.id, type="qcm", payload={}, is_correct=correct))
        db.session.commit()

    # Recalcul (eager en test) puis lecture du cache.
    refresh = client.post(f"/api/v1/classes/{class_id}/insights", headers=auth_headers)
    assert refresh.status_code in (200, 202)

    got = client.get(f"/api/v1/classes/{class_id}/insights", headers=auth_headers)
    assert got.status_code == 200
    data = got.json
    assert len(data["weak_topics"]) >= 1
    top = data["weak_topics"][0]
    assert top["note_title"] == "Mitose difficile"
    assert top["error_rate"] == 75.0   # 3 fausses / 4
    assert data["summary"]
    assert data["ai"] is False  # pas de clé Gemini en test → résumé heuristique


def test_analytics_query_budget_is_bounded(client, auth_headers, app):
    """La vue d'ensemble ne fait pas de N+1 : le nombre de requêtes ne croît pas
    avec le nombre d'élèves/devoirs."""
    from app.models.group import Group, GroupMember
    from app.models.assignment import Assignment, AssignmentProgress

    def seed(class_name, n_students, n_assignments):
        with app.app_context():
            g = client.post("/api/v1/classes", json={"name": class_name}, headers=auth_headers).json
            gid = g["id"]
            for i in range(n_students):
                u = User(email=f"{class_name}-s{i}@t.co", username=f"{class_name}-s{i}")
                u.set_password("password123")
                db.session.add(u)
                db.session.flush()
                db.session.add(GroupMember(group_id=gid, user_id=u.id, role="member"))
                for a in range(n_assignments):
                    pass
            for a in range(n_assignments):
                asgn = Assignment(group_id=gid, title=f"A{a}", created_by=1)
                db.session.add(asgn)
                db.session.flush()
                for u in db.session.query(GroupMember).filter_by(group_id=gid).all():
                    db.session.add(AssignmentProgress(assignment_id=asgn.id, user_id=u.user_id))
            db.session.commit()
            return gid

    small_id = seed("petit", n_students=2, n_assignments=2)
    with assert_max_queries(12) as small:
        r1 = client.get(f"/api/v1/classes/{small_id}/analytics", headers=auth_headers)
    assert r1.status_code == 200

    big_id = seed("grand", n_students=10, n_assignments=6)
    with assert_max_queries(12) as big:
        r2 = client.get(f"/api/v1/classes/{big_id}/analytics", headers=auth_headers)
    assert r2.status_code == 200

    # Pas de N+1 : le coût en requêtes reste constant.
    assert big.count == small.count
