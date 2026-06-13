from app.extensions import db
from app.models.user import User
from app.models.binder import Binder
from app.models.note import Note


def _other_user(app, email, username):
    with app.app_context():
        u = User(email=email, username=username)
        u.set_password("password123")
        db.session.add(u)
        db.session.commit()
        return u.id


def _login(client, email):
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    return {"Authorization": f"Bearer {r.json['access_token']}"}


def _setup_shared_class(client, teacher_headers, app, teacher_id):
    # Le prof crée un classeur + une note dedans.
    with app.app_context():
        binder = Binder(user_id=teacher_id, name="Cours de Bio")
        db.session.add(binder)
        db.session.commit()
        note = Note(user_id=teacher_id, binder_id=binder._id, title="Chapitre 1", content="La cellule")
        db.session.add(note)
        db.session.commit()
        binder_uuid = binder.id
        note_uuid = note.id

    # Le prof crée une classe et y partage le classeur.
    cls = client.post("/api/v1/classes", json={"name": "Classe SVT"}, headers=teacher_headers).get_json()
    class_id = cls["id"]
    invite_code = cls["invite_code"]
    share = client.post(
        f"/api/v1/groups/{class_id}/binders",
        json={"binder_id": binder_uuid, "permission": "read"},
        headers=teacher_headers,
    )
    assert share.status_code == 200
    return binder_uuid, note_uuid, invite_code


def test_student_sees_shared_binder_notes_read_only(client, auth_headers, test_user, app):
    binder_uuid, note_uuid, invite_code = _setup_shared_class(client, auth_headers, app, test_user["id"])

    # Un élève rejoint la classe.
    _other_user(app, "eleve@example.com", "eleve")
    student = _login(client, "eleve@example.com")
    join = client.post("/api/v1/groups/join", json={"invite_code": invite_code}, headers=student)
    assert join.status_code == 200

    # L'élève voit le classeur partagé en lecture seule, à la racine de son arbre.
    binders = client.get("/api/v1/binders?all=true", headers=student).get_json()["data"]
    shared = next((b for b in binders if b["id"] == binder_uuid), None)
    assert shared is not None
    assert shared["read_only"] is True
    assert shared["parent_id"] is None

    # L'élève reçoit la note du prof, en lecture seule.
    notes = client.get("/api/v1/notes", headers=student).get_json()["data"]
    note = next((n for n in notes if n["id"] == note_uuid), None)
    assert note is not None
    assert note["read_only"] is True
    assert note["title"] == "Chapitre 1"


def test_get_single_shared_note_is_read_only_for_student(client, auth_headers, test_user, app):
    _binder, note_uuid, invite_code = _setup_shared_class(client, auth_headers, app, test_user["id"])

    _other_user(app, "eleve2@example.com", "eleve2")
    student = _login(client, "eleve2@example.com")
    client.post("/api/v1/groups/join", json={"invite_code": invite_code}, headers=student)

    # L'élève peut ouvrir la note, marquée lecture seule.
    as_student = client.get(f"/api/v1/notes/{note_uuid}", headers=student)
    assert as_student.status_code == 200
    assert as_student.json["read_only"] is True

    # Le prop (prof) la voit en écriture (read_only False).
    as_teacher = client.get(f"/api/v1/notes/{note_uuid}", headers=auth_headers)
    assert as_teacher.json["read_only"] is False


def test_student_can_copy_shared_note_into_personal_space(client, auth_headers, test_user, app):
    _binder, note_uuid, invite_code = _setup_shared_class(client, auth_headers, app, test_user["id"])

    _other_user(app, "copieur@example.com", "copieur")
    student = _login(client, "copieur@example.com")
    client.post("/api/v1/groups/join", json={"invite_code": invite_code}, headers=student)

    copy = client.post(f"/api/v1/notes/{note_uuid}/copy", headers=student)
    assert copy.status_code == 201
    data = copy.json
    assert data["id"] != note_uuid
    assert "copie" in data["title"].lower()
    assert data["read_only"] is False  # la copie appartient à l'élève -> éditable
    assert data["binder_id"] is None

    # La copie est éditable (PUT réussit).
    put = client.put(f"/api/v1/notes/{data['id']}",
                     json={"title": "Ma version", "content": "modifié"}, headers=student)
    assert put.status_code == 200
    assert put.json["title"] == "Ma version"


def test_student_can_hide_shared_note(client, auth_headers, test_user, app):
    _binder, note_uuid, invite_code = _setup_shared_class(client, auth_headers, app, test_user["id"])

    _other_user(app, "masqueur@example.com", "masqueur")
    student = _login(client, "masqueur@example.com")
    client.post("/api/v1/groups/join", json={"invite_code": invite_code}, headers=student)

    # Visible au départ.
    notes = client.get("/api/v1/notes", headers=student).get_json()["data"]
    assert any(n["id"] == note_uuid for n in notes)

    # Masquer la note.
    hide = client.post(f"/api/v1/notes/{note_uuid}/hide", headers=student)
    assert hide.status_code == 204

    # Elle disparaît de la liste de l'élève.
    notes_after = client.get("/api/v1/notes", headers=student).get_json()["data"]
    assert all(n["id"] != note_uuid for n in notes_after)

    # Réafficher.
    unhide = client.delete(f"/api/v1/notes/{note_uuid}/hide", headers=student)
    assert unhide.status_code == 204
    notes_restored = client.get("/api/v1/notes", headers=student).get_json()["data"]
    assert any(n["id"] == note_uuid for n in notes_restored)


def test_user_cannot_hide_own_note(client, auth_headers, test_user, app):
    # Le prof (propriétaire) ne peut pas masquer sa propre note.
    _binder, note_uuid, _code = _setup_shared_class(client, auth_headers, app, test_user["id"])
    resp = client.post(f"/api/v1/notes/{note_uuid}/hide", headers=auth_headers)
    assert resp.status_code == 403


def test_non_member_does_not_see_shared_notes(client, auth_headers, test_user, app):
    _binder, note_uuid, _code = _setup_shared_class(client, auth_headers, app, test_user["id"])

    # Un utilisateur NON membre ne voit pas les notes du classeur partagé.
    _other_user(app, "etranger@example.com", "etranger")
    outsider = _login(client, "etranger@example.com")
    notes = client.get("/api/v1/notes", headers=outsider).get_json()["data"]
    assert all(n["id"] != note_uuid for n in notes)
