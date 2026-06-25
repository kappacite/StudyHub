from unittest.mock import patch

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


def test_element_added_after_share_is_immediately_visible(client, auth_headers, test_user, app):
    """B2 — partage par référence auto-actualisé : un élément ajouté au classeur
    APRÈS le partage est immédiatement visible de l'élève, sans ré-action du prof."""
    binder_uuid, _note, invite_code = _setup_shared_class(client, auth_headers, app, test_user["id"])

    _other_user(app, "eleve_b2@example.com", "eleveb2")
    student = _login(client, "eleve_b2@example.com")
    client.post("/api/v1/groups/join", json={"invite_code": invite_code}, headers=student)

    # Le prof ajoute une NOUVELLE note dans le classeur déjà partagé.
    with app.app_context():
        binder = Binder.query.filter_by(id=binder_uuid).first()
        late_note = Note(
            user_id=test_user["id"], binder_id=binder._id,
            title="Chapitre 2 (ajouté après partage)", content="La mitose",
        )
        db.session.add(late_note)
        # ... et un sous-classeur avec sa propre note (auto-MAJ des descendants).
        child = Binder(user_id=test_user["id"], name="TD", parent_id=binder._id)
        db.session.add(child)
        db.session.commit()
        deep_note = Note(user_id=test_user["id"], binder_id=child._id,
                         title="Exercice 1", content="Énoncé")
        db.session.add(deep_note)
        db.session.commit()
        late_uuid, deep_uuid = late_note.id, deep_note.id

    # L'élève voit les deux nouvelles notes sans que le prof n'ait re-partagé.
    notes = client.get("/api/v1/notes", headers=student).get_json()["data"]
    ids = {n["id"] for n in notes}
    assert late_uuid in ids, "note ajoutée après partage non visible (pas d'auto-MAJ)"
    assert deep_uuid in ids, "note d'un sous-classeur ajouté après partage non visible"
    assert all(n["read_only"] for n in notes if n["id"] in {late_uuid, deep_uuid})


def test_binder_classes_indicator(client, auth_headers, test_user, app):
    """B2 — indicateur « partagé » : un classeur partagé liste ses classes ;
    un classeur non partagé renvoie une liste vide ; isolation propriétaire."""
    binder_uuid, _note, _code = _setup_shared_class(client, auth_headers, app, test_user["id"])

    # Le prof voit la classe à laquelle son classeur est partagé.
    resp = client.get(f"/api/v1/groups/binders/{binder_uuid}/classes", headers=auth_headers)
    assert resp.status_code == 200
    classes = resp.get_json()
    assert len(classes) == 1
    assert classes[0]["name"] == "Classe SVT"
    assert classes[0]["permission"] == "read"

    # Un classeur non partagé renvoie une liste vide.
    with app.app_context():
        solo = Binder(user_id=test_user["id"], name="Privé")
        db.session.add(solo)
        db.session.commit()
        solo_uuid = solo.id
    empty = client.get(f"/api/v1/groups/binders/{solo_uuid}/classes", headers=auth_headers)
    assert empty.status_code == 200
    assert empty.get_json() == []

    # Un autre utilisateur ne peut pas interroger un classeur qui n'est pas le sien.
    _other_user(app, "intrus@example.com", "intrus")
    intruder = _login(client, "intrus@example.com")
    forbidden = client.get(f"/api/v1/groups/binders/{binder_uuid}/classes", headers=intruder)
    assert forbidden.status_code == 404


def test_student_sees_shared_notes_when_filtering_by_binder(client, auth_headers, test_user, app):
    """Régression #5 — les notes d'un classeur partagé ne doivent pas
    « disparaître » lorsqu'on liste les notes scopées à ce classeur."""
    binder_uuid, note_uuid, invite_code = _setup_shared_class(client, auth_headers, app, test_user["id"])

    _other_user(app, "eleve_scope@example.com", "elevescope")
    student = _login(client, "eleve_scope@example.com")
    client.post("/api/v1/groups/join", json={"invite_code": invite_code}, headers=student)

    resp = client.get(f"/api/v1/notes?binder_id={binder_uuid}", headers=student)
    assert resp.status_code == 200
    notes = resp.get_json()["data"]
    note = next((n for n in notes if n["id"] == note_uuid), None)
    assert note is not None, "note du classeur partagé absente du listing scopé au classeur"
    assert note["read_only"] is True


def test_non_member_cannot_list_shared_binder_notes(client, auth_headers, test_user, app):
    """Le scope par classeur partagé reste protégé : un non-membre est refusé."""
    binder_uuid, _note, _code = _setup_shared_class(client, auth_headers, app, test_user["id"])

    _other_user(app, "intrus_scope@example.com", "intrusscope")
    outsider = _login(client, "intrus_scope@example.com")
    resp = client.get(f"/api/v1/notes?binder_id={binder_uuid}", headers=outsider)
    assert resp.status_code in (403, 404)


@patch("app.services.ai_service.AIService.generate_quiz")
def test_student_can_run_ai_quiz_on_shared_note(mock_gen, client, auth_headers, test_user, app):
    """Régression #6 — la révision active IA (QCM) doit être possible sur une note
    partagée non possédée ; le quiz produit appartient à l'élève (isolation)."""
    mock_gen.return_value = [{
        "question": "Q ?",
        "options": [
            {"id": "a", "text": "x", "correct": True},
            {"id": "b", "text": "y", "correct": False},
        ],
    }]
    _binder, note_uuid, invite_code = _setup_shared_class(client, auth_headers, app, test_user["id"])

    _other_user(app, "revise@example.com", "revise")
    student = _login(client, "revise@example.com")
    client.post("/api/v1/groups/join", json={"invite_code": invite_code}, headers=student)

    gen = client.post(
        "/api/v1/quizzes/generate",
        json={"note_id": note_uuid, "question_count": 1},
        headers=student,
    )
    assert gen.status_code == 201, gen.json

    # Le prof (propriétaire) ne voit pas le quiz de l'élève (isolation par user_id).
    teacher_quizzes = client.get(f"/api/v1/quizzes/note/{note_uuid}", headers=auth_headers).json
    assert teacher_quizzes == [] or all(q["id"] != gen.json["id"] for q in teacher_quizzes)
    # L'élève voit son propre quiz.
    student_quizzes = client.get(f"/api/v1/quizzes/note/{note_uuid}", headers=student).json
    assert any(q["id"] == gen.json["id"] for q in student_quizzes)


@patch("app.services.ai_service.AIService.generate_quiz")
def test_non_member_cannot_run_ai_quiz_on_shared_note(mock_gen, client, auth_headers, test_user, app):
    mock_gen.return_value = [{"question": "Q ?", "options": [
        {"id": "a", "text": "x", "correct": True}, {"id": "b", "text": "y", "correct": False}]}]
    _binder, note_uuid, _code = _setup_shared_class(client, auth_headers, app, test_user["id"])

    _other_user(app, "intrus_ai@example.com", "intrusai")
    outsider = _login(client, "intrus_ai@example.com")
    resp = client.post(
        "/api/v1/quizzes/generate",
        json={"note_id": note_uuid, "question_count": 1},
        headers=outsider,
    )
    assert resp.status_code in (403, 404)


def test_deleting_shared_binder_does_not_destroy_original(client, auth_headers, test_user, app):
    """Régression #3 — un destinataire qui « supprime » un classeur partagé ne
    détruit PAS l'original ; il est seulement retiré de sa propre vue."""
    binder_uuid, note_uuid, invite_code = _setup_shared_class(client, auth_headers, app, test_user["id"])

    _other_user(app, "suppr@example.com", "suppr")
    student = _login(client, "suppr@example.com")
    client.post("/api/v1/groups/join", json={"invite_code": invite_code}, headers=student)

    # L'élève voit le classeur partagé.
    binders = client.get("/api/v1/binders?all=true", headers=student).get_json()["data"]
    assert any(b["id"] == binder_uuid for b in binders)

    # L'élève « supprime » le classeur partagé -> succès (204), mais masquage seulement.
    resp = client.delete(f"/api/v1/binders/{binder_uuid}", headers=student)
    assert resp.status_code == 204

    # Côté élève : le classeur (et ses notes) ont disparu de SA vue.
    binders_after = client.get("/api/v1/binders?all=true", headers=student).get_json()["data"]
    assert all(b["id"] != binder_uuid for b in binders_after)
    notes_after = client.get("/api/v1/notes", headers=student).get_json()["data"]
    assert all(n["id"] != note_uuid for n in notes_after)

    # Côté propriétaire (prof) : l'original est intact.
    owner_binders = client.get("/api/v1/binders?all=true", headers=auth_headers).get_json()["data"]
    assert any(b["id"] == binder_uuid for b in owner_binders)
    owner_note = client.get(f"/api/v1/notes/{note_uuid}", headers=auth_headers)
    assert owner_note.status_code == 200
    assert owner_note.json["read_only"] is False


def test_owner_can_still_delete_own_binder(client, auth_headers, test_user, app):
    binder_uuid, _note, _code = _setup_shared_class(client, auth_headers, app, test_user["id"])
    resp = client.delete(f"/api/v1/binders/{binder_uuid}", headers=auth_headers)
    assert resp.status_code == 204
    # Réellement supprimé pour le propriétaire (absent de son arborescence).
    binders = client.get("/api/v1/binders?all=true", headers=auth_headers).get_json()["data"]
    assert all(b["id"] != binder_uuid for b in binders)


def test_non_member_does_not_see_shared_notes(client, auth_headers, test_user, app):
    _binder, note_uuid, _code = _setup_shared_class(client, auth_headers, app, test_user["id"])

    # Un utilisateur NON membre ne voit pas les notes du classeur partagé.
    _other_user(app, "etranger@example.com", "etranger")
    outsider = _login(client, "etranger@example.com")
    notes = client.get("/api/v1/notes", headers=outsider).get_json()["data"]
    assert all(n["id"] != note_uuid for n in notes)
