"""
Tests PR5 — Gestion de classe : roster, régénération d'invitation, distribution.
"""
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


def _login(client, email):
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    return {"Authorization": f"Bearer {r.json['access_token']}"}


def _class_with_student(client, teacher_headers, app, email):
    resp = client.post("/api/v1/classes", json={"name": "Classe Gestion"}, headers=teacher_headers)
    class_id, invite = resp.json["id"], resp.json["invite_code"]
    sid = _create_user(app, email, email.split("@")[0])
    sh = _login(client, email)
    client.post("/api/v1/groups/join", json={"invite_code": invite}, headers=sh)
    return class_id, invite, sid, sh


def test_my_classes_exposes_role(client, auth_headers, app, test_user):
    """GET /classes expose le rôle de l'utilisateur (sépare prof/élève côté UI)."""
    class_id, _invite, _sid, sh = _class_with_student(client, auth_headers, app, "rolecheck@test.com")

    teacher_list = client.get("/api/v1/classes", headers=auth_headers).json
    assert next(c for c in teacher_list if c["id"] == class_id)["my_role"] == "owner"

    student_list = client.get("/api/v1/classes", headers=sh).json
    assert next(c for c in student_list if c["id"] == class_id)["my_role"] == "member"


def test_roster_lists_members(client, auth_headers, app, test_user):
    class_id, invite, sid, sh = _class_with_student(client, auth_headers, app, "mg1@test.com")

    roster = client.get(f"/api/v1/classes/{class_id}/members", headers=auth_headers)
    assert roster.status_code == 200
    by_id = {r["user_id"]: r for r in roster.json}
    assert by_id[test_user["id"]]["role"] == "owner"
    assert by_id[sid]["role"] == "member"
    assert "completed_assignments" in by_id[sid]

    # Un élève ne peut pas consulter le roster.
    forbidden = client.get(f"/api/v1/classes/{class_id}/members", headers=sh)
    assert forbidden.status_code == 403


def test_regenerate_invite_invalidates_old_code(client, auth_headers, app):
    class_id, old_invite, sid, sh = _class_with_student(client, auth_headers, app, "mg2@test.com")

    # Élève interdit de régénérer.
    bad = client.post(f"/api/v1/classes/{class_id}/invite/regenerate", headers=sh)
    assert bad.status_code == 403

    # Le prof régénère → nouveau code.
    resp = client.post(f"/api/v1/classes/{class_id}/invite/regenerate", headers=auth_headers)
    assert resp.status_code == 200
    new_invite = resp.json["invite_code"]
    assert new_invite != old_invite
    assert len(new_invite) == 8

    # L'ancien code ne permet plus de rejoindre.
    other_id = _create_user(app, "mg2b@test.com", "mg2b")
    oh = _login(client, "mg2b@test.com")
    join_old = client.post("/api/v1/groups/join", json={"invite_code": old_invite}, headers=oh)
    assert join_old.status_code != 200
    # Le nouveau code fonctionne.
    join_new = client.post("/api/v1/groups/join", json={"invite_code": new_invite}, headers=oh)
    assert join_new.status_code == 200


def test_distribute_binder_clones_to_students(client, auth_headers, app):
    class_id, invite, sid, sh = _class_with_student(client, auth_headers, app, "mg3@test.com")

    # Le prof crée un classeur avec une note.
    binder_id = client.post("/api/v1/binders", json={"name": "Cours à distribuer"}, headers=auth_headers).json["id"]
    client.post("/api/v1/notes", json={"title": "Leçon 1", "content": "x", "binder_id": binder_id}, headers=auth_headers)

    # L'élève n'a pas encore ce classeur.
    before = client.get("/api/v1/binders", headers=sh).json
    before_names = [b["name"] for b in (before["data"] if isinstance(before, dict) else before)]
    assert "Cours à distribuer" not in before_names

    # Distribution.
    resp = client.post(f"/api/v1/classes/{class_id}/distribute", json={"binder_id": binder_id}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json["distributed"] == 1

    # L'élève a reçu une copie + une notification.
    after = client.get("/api/v1/binders", headers=sh).json
    after_names = [b["name"] for b in (after["data"] if isinstance(after, dict) else after)]
    assert "Cours à distribuer" in after_names

    notifs = client.get("/api/v1/notifications", headers=sh).json
    assert any(n["type"] == "course_shared" for n in notifs)


def test_distribute_forbidden_and_not_found(client, auth_headers, app):
    class_id, invite, sid, sh = _class_with_student(client, auth_headers, app, "mg4@test.com")
    binder_id = client.post("/api/v1/binders", json={"name": "B"}, headers=auth_headers).json["id"]

    # Élève interdit.
    bad = client.post(f"/api/v1/classes/{class_id}/distribute", json={"binder_id": binder_id}, headers=sh)
    assert bad.status_code == 403

    # Classeur d'un autre utilisateur → 404.
    other_binder = client.post("/api/v1/binders", json={"name": "Autre"}, headers=sh).json["id"]
    nf = client.post(f"/api/v1/classes/{class_id}/distribute", json={"binder_id": other_binder}, headers=auth_headers)
    assert nf.status_code == 404
