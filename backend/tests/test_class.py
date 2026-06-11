"""
Tests pour la Feature 10 — Système Professeur (Classes + Devoirs).

Cas couverts :
  - test_class_type_group_creation
  - test_only_teacher_can_create_assignment
  - test_teacher_progress_view_forbidden_for_student
  - test_assignment_due_date_appears_in_focus_today
  - test_progress_aggregation_correct
  - test_student_cannot_see_other_student_flashcard_content (isolation des données)
"""
from datetime import datetime, timedelta
from app.models.user import User
from app.models.group import Group, GroupMember
from app.models.binder import Binder
from app.extensions import db


# ─── Helpers ─────────────────────────────────────────────────────────────────

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


def _create_binder(client, headers, name="Cours de Biologie"):
    resp = client.post("/api/v1/binders", json={"name": name}, headers=headers)
    assert resp.status_code == 201
    return resp.json["id"]


# ─── Tests ────────────────────────────────────────────────────────────────────

def test_class_type_group_creation(client, auth_headers, test_user):
    """Créer une classe doit retourner type='class' et is_class=True."""
    resp = client.post("/api/v1/classes", json={
        "name": "PACES Biologie 2025",
        "description": "Espace de cours pour les PACES"
    }, headers=auth_headers)

    assert resp.status_code == 201
    data = resp.json
    assert data["is_class"] is True
    assert data["type"] == "class"
    assert "invite_code" in data
    assert len(data["invite_code"]) == 8


def test_only_teacher_can_create_assignment(client, auth_headers, test_user, app):
    """Un simple member ne peut pas créer de devoir — seul owner/admin le peut."""
    # Teacher crée la classe
    resp = client.post("/api/v1/classes", json={"name": "Cours Chimie"}, headers=auth_headers)
    assert resp.status_code == 201
    class_id = resp.json["id"]
    invite_code = resp.json["invite_code"]

    binder_id = _create_binder(client, auth_headers)

    # Créer un élève et le faire rejoindre
    student_id = _create_user(app, "student@test.com", "student")
    student_headers = _login(client, "student@test.com")
    join_resp = client.post("/api/v1/groups/join", json={"invite_code": invite_code},
                            headers=student_headers)
    assert join_resp.status_code == 200

    # L'élève ne peut PAS créer un devoir → 403
    asgn_resp = client.post(f"/api/v1/classes/{class_id}/assignments", json={
        "binder_id": binder_id,
        "title": "Devoir 1",
        "due_date": (datetime.utcnow() + timedelta(days=5)).isoformat()
    }, headers=student_headers)
    assert asgn_resp.status_code == 403

    # Le professeur PEUT créer un devoir → 201
    teacher_resp = client.post(f"/api/v1/classes/{class_id}/assignments", json={
        "binder_id": binder_id,
        "title": "Devoir 1",
        "due_date": (datetime.utcnow() + timedelta(days=5)).isoformat()
    }, headers=auth_headers)
    assert teacher_resp.status_code == 201
    assert teacher_resp.json["title"] == "Devoir 1"
    assert teacher_resp.json["binder_id"] == binder_id


def test_teacher_progress_view_forbidden_for_student(client, auth_headers, test_user, app):
    """L'endpoint de progression individuelle est réservé au professeur."""
    # Créer la classe
    resp = client.post("/api/v1/classes", json={"name": "Cours Maths"}, headers=auth_headers)
    assert resp.status_code == 201
    class_id = resp.json["id"]
    invite_code = resp.json["invite_code"]

    binder_id = _create_binder(client, auth_headers)

    # Élève rejoint
    student_id = _create_user(app, "student2@test.com", "student2")
    student_headers = _login(client, "student2@test.com")
    client.post("/api/v1/groups/join", json={"invite_code": invite_code},
                headers=student_headers)

    # L'élève essaie de voir la progression d'un autre → 403
    prog_resp = client.get(
        f"/api/v1/classes/{class_id}/students/{test_user['id']}/progress",
        headers=student_headers
    )
    assert prog_resp.status_code == 403

    # Le professeur peut voir la progression → 200
    teacher_prog = client.get(
        f"/api/v1/classes/{class_id}/students/{student_id}/progress",
        headers=auth_headers
    )
    assert teacher_prog.status_code == 200
    assert isinstance(teacher_prog.json, list)


def test_assignment_due_date_appears_in_focus_today(client, auth_headers, test_user, app):
    """Un devoir avec deadline dans 2 jours doit apparaître dans /focus/today."""
    # Professeur crée la classe
    resp = client.post("/api/v1/classes", json={"name": "Cours Focus"}, headers=auth_headers)
    assert resp.status_code == 201
    class_id = resp.json["id"]
    invite_code = resp.json["invite_code"]

    binder_id = _create_binder(client, auth_headers)

    # Élève rejoint la classe
    student_id = _create_user(app, "student3@test.com", "student3")
    student_headers = _login(client, "student3@test.com")
    client.post("/api/v1/groups/join", json={"invite_code": invite_code},
                headers=student_headers)

    # Professeur crée un devoir avec deadline dans 2 jours
    due = (datetime.utcnow() + timedelta(days=2)).isoformat()
    client.post(f"/api/v1/classes/{class_id}/assignments", json={
        "binder_id": binder_id,
        "title": "Devoir Focus",
        "due_date": due
    }, headers=auth_headers)

    # Le focus de l'élève doit inclure ce devoir
    focus_resp = client.get("/api/v1/focus/today", headers=student_headers)
    assert focus_resp.status_code == 200
    data = focus_resp.json
    assert data["assignment_count"] >= 1
    assignment_items = [i for i in data["items"] if i["type"] == "assignment"]
    assert len(assignment_items) >= 1
    assert "Devoir Focus" in assignment_items[0]["title"]


def test_progress_aggregation_correct(client, auth_headers, test_user, app):
    """Vérifier la cohérence des données de progression par élève."""
    resp = client.post("/api/v1/classes", json={"name": "Cours Stats"}, headers=auth_headers)
    assert resp.status_code == 201
    class_id = resp.json["id"]
    invite_code = resp.json["invite_code"]

    binder_id = _create_binder(client, auth_headers)

    student_id = _create_user(app, "student4@test.com", "student4")
    student_headers = _login(client, "student4@test.com")
    client.post("/api/v1/groups/join", json={"invite_code": invite_code},
                headers=student_headers)

    # Créer devoir
    asgn_resp = client.post(f"/api/v1/classes/{class_id}/assignments", json={
        "binder_id": binder_id,
        "title": "Devoir Stats"
    }, headers=auth_headers)
    assert asgn_resp.status_code == 201

    # L'élève consulte ses devoirs (mine)
    mine_resp = client.get("/api/v1/assignments/mine", headers=student_headers)
    assert mine_resp.status_code == 200
    mine_data = mine_resp.json
    assert len(mine_data) >= 1

    matching = [a for a in mine_data if a["title"] == "Devoir Stats"]
    assert len(matching) == 1
    assert matching[0]["status"] == "todo"
    assert matching[0]["my_cards_reviewed"] == 0

    # Le prof consulte la progression de cet élève
    prog_resp = client.get(
        f"/api/v1/classes/{class_id}/students/{student_id}/progress",
        headers=auth_headers
    )
    assert prog_resp.status_code == 200
    prog_data = prog_resp.json
    assert len(prog_data) >= 1
    assert prog_data[0]["user_id"] == student_id
    assert prog_data[0]["cards_reviewed"] == 0


def test_student_cannot_see_other_student_flashcard_content(client, auth_headers, test_user, app):
    """La progression individuelle ne doit jamais exposer le contenu des flashcards."""
    resp = client.post("/api/v1/classes", json={"name": "Cours Isolation"}, headers=auth_headers)
    assert resp.status_code == 201
    class_id = resp.json["id"]
    invite_code = resp.json["invite_code"]

    binder_id = _create_binder(client, auth_headers)

    student_a_id = _create_user(app, "studentA@test.com", "studentA")
    student_b_id = _create_user(app, "studentB@test.com", "studentB")
    headers_a = _login(client, "studentA@test.com")
    headers_b = _login(client, "studentB@test.com")

    client.post("/api/v1/groups/join", json={"invite_code": invite_code}, headers=headers_a)
    client.post("/api/v1/groups/join", json={"invite_code": invite_code}, headers=headers_b)

    asgn_resp = client.post(f"/api/v1/classes/{class_id}/assignments", json={
        "binder_id": binder_id,
        "title": "Devoir Isolation"
    }, headers=auth_headers)
    assert asgn_resp.status_code == 201

    # Student A demande la progression de Student B → 403
    prog_resp = client.get(
        f"/api/v1/classes/{class_id}/students/{student_b_id}/progress",
        headers=headers_a
    )
    assert prog_resp.status_code == 403

    # Vérifier que /assignments/mine ne retourne que ses propres données
    mine_resp = client.get("/api/v1/assignments/mine", headers=headers_a)
    assert mine_resp.status_code == 200
    for item in mine_resp.json:
        # Chaque item ne doit avoir que des champs de progression propres à user A
        assert "my_cards_reviewed" in item
        assert "progress" not in item  # pas de liste de progression des autres élèves
