"""
Régressions prof/élève :
- un ensemble de révision d'un classeur partagé est visible (lecture seule) de l'élève (#5) ;
- un devoir ciblant un ensemble VIDE n'est pas marqué « fait » (#4).
"""
from app.extensions import db
from app.models.user import User
from app.models.binder import Binder


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
    resp = client.post("/api/v1/classes", json={"name": "Classe Bio"}, headers=teacher_headers)
    class_id, invite = resp.json["id"], resp.json["invite_code"]
    sid = _create_user(app, email, email.split("@")[0])
    sh = _login(client, email)
    client.post("/api/v1/groups/join", json={"invite_code": invite}, headers=sh)
    return class_id, sid, sh


def test_shared_revision_set_visible_to_student_read_only(client, auth_headers, test_user, app):
    """#5 — un ensemble rangé dans un classeur partagé à la classe remonte à l'élève."""
    class_id, _sid, sh = _class_with_student(client, auth_headers, app, "eleve_rs@test.com")

    # Le prof crée un classeur + un ensemble de révision dedans, puis partage le classeur.
    with app.app_context():
        binder = Binder(user_id=test_user["id"], name="Cours Bio")
        db.session.add(binder)
        db.session.commit()
        binder_uuid = binder.id

    set_id = client.post("/api/v1/revision/sets", json={
        "name": "QCM partagé", "type": "qcm", "binder_id": binder_uuid,
    }, headers=auth_headers).json["id"]
    client.post(f"/api/v1/revision/sets/{set_id}/items", json={"payload": {
        "question": "ADN ?",
        "options": [{"id": "a", "text": "Acide", "correct": True}, {"id": "b", "text": "Base", "correct": False}],
    }}, headers=auth_headers)

    share = client.post(f"/api/v1/groups/{class_id}/binders",
                        json={"binder_id": binder_uuid, "permission": "read"}, headers=auth_headers)
    assert share.status_code == 200

    # L'élève voit l'ensemble dans son listing, en lecture seule.
    sets = client.get("/api/v1/revision/sets", headers=sh).get_json()["data"]
    shared = next((s for s in sets if s["id"] == set_id), None)
    assert shared is not None, "l'ensemble partagé n'apparaît pas pour l'élève"
    assert shared["read_only"] is True
    assert shared["item_count"] == 1

    # Il peut aussi l'ouvrir (étude).
    one = client.get(f"/api/v1/revision/sets/{set_id}", headers=sh)
    assert one.status_code == 200
    assert one.json["read_only"] is True

    # Un non-membre ne le voit pas.
    _create_user(app, "horsclasse_rs@test.com", "horsrs")
    outsider = _login(client, "horsclasse_rs@test.com")
    out_sets = client.get("/api/v1/revision/sets", headers=outsider).get_json()["data"]
    assert all(s["id"] != set_id for s in out_sets)


def test_student_can_study_all_items_of_shared_set(client, auth_headers, test_user, app):
    """L'élève révise TOUS les items d'un ensemble partagé même si le prof les a
    déjà planifiés au futur ; sa notation n'altère pas l'échéancier du prof."""
    class_id, _sid, sh = _class_with_student(client, auth_headers, app, "eleve_study@test.com")

    with app.app_context():
        binder = Binder(user_id=test_user["id"], name="Cours Histoire")
        db.session.add(binder)
        db.session.commit()
        binder_uuid = binder.id

    set_id = client.post("/api/v1/revision/sets", json={
        "name": "Vrai/Faux Histoire", "type": "vf", "binder_id": binder_uuid,
    }, headers=auth_headers).json["id"]
    item = client.post(f"/api/v1/revision/sets/{set_id}/items", json={"payload": {
        "assertion": "La Révolution française a commencé en 1789.", "correct": True,
    }}, headers=auth_headers).json
    client.post(f"/api/v1/groups/{class_id}/binders",
                json={"binder_id": binder_uuid, "permission": "read"}, headers=auth_headers)

    # Le prof révise son item (bonne réponse) → next_review poussé au futur.
    client.post(f"/api/v1/revision/sets/{set_id}/study/grade/{item['id']}",
                json={"answer": {"value": True}}, headers=auth_headers)

    # L'élève voit quand même l'item à étudier (état SM-2 du prof ignoré).
    to_study = client.get(f"/api/v1/revision/sets/{set_id}/study", headers=sh)
    assert to_study.status_code == 200
    assert any(i["id"] == item["id"] for i in to_study.json), "l'élève ne voit aucun item à réviser"

    # Échéancier du prof avant notation élève.
    from app.models.revision import RevisionItem
    with app.app_context():
        before = db.session.get(RevisionItem, item["id"]).next_review

    # L'élève note l'item : sa StudySession est créée, l'item du prof est inchangé.
    graded = client.post(f"/api/v1/revision/sets/{set_id}/study/grade/{item['id']}",
                         json={"answer": {"value": False}}, headers=sh)
    assert graded.status_code == 200

    with app.app_context():
        after = db.session.get(RevisionItem, item["id"]).next_review
        assert after == before, "la notation de l'élève ne doit pas modifier l'échéancier du prof"


def test_assignment_on_empty_revision_set_is_todo(client, auth_headers, app):
    """#4 — un devoir ciblant un ensemble VIDE ne doit pas être marqué « fait »."""
    class_id, _sid, sh = _class_with_student(client, auth_headers, app, "eleve_empty@test.com")

    # Ensemble créé sans aucun item.
    set_id = client.post("/api/v1/revision/sets", json={"name": "Vide", "type": "qcm"}, headers=auth_headers).json["id"]

    asgn = client.post(f"/api/v1/classes/{class_id}/assignments", json={
        "title": "Réviser (vide)",
        "tasks": [{"task_type": "revision", "ref": str(set_id)}],
    }, headers=auth_headers).json

    mine = client.get("/api/v1/assignments/mine", headers=sh).json
    task = next(a for a in mine if a["id"] == asgn["id"])["tasks"][0]
    assert task["my_status"] == "todo", "un ensemble vide ne doit pas être 'done'"
