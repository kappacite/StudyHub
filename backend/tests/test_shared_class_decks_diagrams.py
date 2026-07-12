"""Visibilité du contenu d'un classeur partagé (cours) : les decks (flashcards)
et les diagrammes doivent remonter en LECTURE SEULE à un membre, comme les
notes/PDF/ensembles. Régression : un classeur partagé en groupe « vide » côté
élève parce que decks/diagrammes n'étaient pas inclus dans le listing global."""

from app.extensions import db
from app.models.user import User
from app.models.binder import Binder
from app.models.deck import Deck
from app.models.diagram import Diagram


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
    with app.app_context():
        binder = Binder(user_id=teacher_id, name="Cours d'Histoire")
        db.session.add(binder)
        db.session.commit()
        deck = Deck(user_id=teacher_id, binder_id=binder._id, name="Dates clés")
        diagram = Diagram(user_id=teacher_id, binder_id=binder._id, title="Frise", code="graph TD;A-->B")
        db.session.add_all([deck, diagram])
        db.session.commit()
        ids = (binder.id, deck.id, diagram.id)

    cls = client.post("/api/v1/classes", json={"name": "Classe Histoire"}, headers=teacher_headers).get_json()
    share = client.post(
        f"/api/v1/groups/{cls['id']}/binders",
        json={"binder_id": ids[0], "permission": "read"},
        headers=teacher_headers,
    )
    assert share.status_code == 200
    return (*ids, cls["invite_code"])


def _join(client, app, email, username, invite_code):
    _other_user(app, email, username)
    headers = _login(client, email)
    assert client.post("/api/v1/groups/join", json={"invite_code": invite_code}, headers=headers).status_code == 200
    return headers


def test_student_sees_shared_binder_deck_read_only(client, auth_headers, test_user, app):
    _binder, deck_id, _diagram, code = _setup_shared_class(client, auth_headers, app, test_user["id"])
    student = _join(client, app, "eleve_deck@example.com", "elevedeck", code)

    decks = client.get("/api/v1/decks", headers=student).get_json()["data"]
    deck = next((d for d in decks if d["id"] == deck_id), None)
    assert deck is not None, "deck du classeur partagé absent du listing de l'élève"
    assert deck["read_only"] is True
    assert deck["name"] == "Dates clés"


def test_student_sees_shared_binder_diagram_read_only(client, auth_headers, test_user, app):
    _binder, _deck, diagram_id, code = _setup_shared_class(client, auth_headers, app, test_user["id"])
    student = _join(client, app, "eleve_diag@example.com", "elevediag", code)

    diagrams = client.get("/api/v1/diagrams", headers=student).get_json()["data"]
    diagram = next((d for d in diagrams if d["id"] == diagram_id), None)
    assert diagram is not None, "diagramme du classeur partagé absent du listing de l'élève"
    assert diagram["read_only"] is True

    # L'élève peut ouvrir le diagramme partagé (pas de 403).
    single = client.get(f"/api/v1/diagrams/{diagram_id}", headers=student)
    assert single.status_code == 200


def test_owner_sees_own_deck_and_diagram_writable(client, auth_headers, test_user, app):
    _binder, deck_id, diagram_id, _code = _setup_shared_class(client, auth_headers, app, test_user["id"])

    decks = client.get("/api/v1/decks", headers=auth_headers).get_json()["data"]
    deck = next((d for d in decks if d["id"] == deck_id), None)
    assert deck is not None and deck["read_only"] is False

    diagrams = client.get("/api/v1/diagrams", headers=auth_headers).get_json()["data"]
    diagram = next((d for d in diagrams if d["id"] == diagram_id), None)
    assert diagram is not None and diagram["read_only"] is False


def test_non_member_does_not_see_shared_deck_or_diagram(client, auth_headers, test_user, app):
    _binder, deck_id, diagram_id, _code = _setup_shared_class(client, auth_headers, app, test_user["id"])

    _other_user(app, "etranger_dd@example.com", "etrangerdd")
    outsider = _login(client, "etranger_dd@example.com")

    decks = client.get("/api/v1/decks", headers=outsider).get_json()["data"]
    assert all(d["id"] != deck_id for d in decks)
    diagrams = client.get("/api/v1/diagrams", headers=outsider).get_json()["data"]
    assert all(d["id"] != diagram_id for d in diagrams)
