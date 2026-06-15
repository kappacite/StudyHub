"""
Tests B1 — Dépôt de cours : classeur de cours de classe (course-binder) et
visibilité en lecture seule des notes/PDF déposés (réutilise GroupBinder).
"""
from app.extensions import db
from app.models.user import User
from app.models.binder import Binder
from app.models.pdf_document import PDFDocument


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
    assert "access_token" in r.json, f"login {email} -> {r.status_code} {r.json}"
    return {"Authorization": f"Bearer {r.json['access_token']}"}


def _class_with_student(client, teacher_headers, app, email):
    resp = client.post("/api/v1/classes", json={"name": "Bio"}, headers=teacher_headers)
    class_id, invite = resp.json["id"], resp.json["invite_code"]
    sid = _create_user(app, email, email.split("@")[0])
    sh = _login(client, email)
    client.post("/api/v1/groups/join", json={"invite_code": invite}, headers=sh)
    return class_id, sid, sh


def test_course_binder_created_and_idempotent(client, auth_headers, app, test_user):
    class_id, _sid, _sh = _class_with_student(client, auth_headers, app, "eleve1@test.com")

    first = client.post(f"/api/v1/classes/{class_id}/course-binder", headers=auth_headers)
    assert first.status_code == 200
    assert first.json["created"] is True
    assert first.json["name"] == "Cours — Bio"
    binder_uuid = first.json["binder_id"]

    # Idempotent : un second appel renvoie le même classeur sans le recréer.
    second = client.post(f"/api/v1/classes/{class_id}/course-binder", headers=auth_headers)
    assert second.status_code == 200
    assert second.json["binder_id"] == binder_uuid
    assert second.json["created"] is False


def test_only_teacher_can_resolve_course_binder(client, auth_headers, app):
    class_id, _sid, sh = _class_with_student(client, auth_headers, app, "eleve2@test.com")
    resp = client.post(f"/api/v1/classes/{class_id}/course-binder", headers=sh)
    assert resp.status_code == 403


def test_deposited_note_visible_to_student_read_only(client, auth_headers, app, test_user):
    """Une note créée dans le classeur de cours après partage est visible de l'élève."""
    class_id, _sid, sh = _class_with_student(client, auth_headers, app, "eleve3@test.com")
    binder_uuid = client.post(f"/api/v1/classes/{class_id}/course-binder", headers=auth_headers).json["binder_id"]

    # Le prof dépose une note de cours via l'endpoint notes existant.
    created = client.post("/api/v1/notes", json={
        "title": "Chapitre 1", "content": "La cellule", "binder_id": binder_uuid,
    }, headers=auth_headers)
    assert created.status_code == 201

    notes = client.get("/api/v1/notes", headers=sh).get_json()["data"]
    note = next((n for n in notes if n["title"] == "Chapitre 1"), None)
    assert note is not None
    assert note["read_only"] is True


def test_deposited_pdf_visible_to_student_read_only(client, auth_headers, app, test_user):
    """Un PDF déposé dans le classeur de cours est visible de l'élève en lecture
    seule (listing + ouverture), mais l'élève ne peut pas le supprimer."""
    class_id, _sid, sh = _class_with_student(client, auth_headers, app, "eleve4@test.com")
    binder_uuid = client.post(f"/api/v1/classes/{class_id}/course-binder", headers=auth_headers).json["binder_id"]

    with app.app_context():
        binder = Binder.query.filter_by(id=binder_uuid).first()
        pdf = PDFDocument(
            name="Polycopié", filename="poly.pdf",
            user_id=test_user["id"], binder_id=binder._id,
        )
        db.session.add(pdf)
        db.session.commit()
        pdf_uuid = pdf.id

    # Visible en lecture seule dans le listing global de l'élève.
    listing = client.get("/api/v1/pdfs", headers=sh).get_json()["data"]
    shared = next((p for p in listing if p["id"] == pdf_uuid), None)
    assert shared is not None
    assert shared["read_only"] is True

    # Ouverture autorisée (read_only), suppression refusée.
    assert client.get(f"/api/v1/pdfs/{pdf_uuid}", headers=sh).json["read_only"] is True
    assert client.delete(f"/api/v1/pdfs/{pdf_uuid}", headers=sh).status_code == 403

    # Un non-membre ne voit pas le PDF de cours.
    _create_user(app, "horsclasse@test.com", "horsclasse")
    outsider = _login(client, "horsclasse@test.com")
    out_list = client.get("/api/v1/pdfs", headers=outsider).get_json()["data"]
    assert all(p["id"] != pdf_uuid for p in out_list)
