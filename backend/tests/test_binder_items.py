"""Tests C1 — rattacher/détacher des éléments existants à un classeur."""


def _binder(client, headers, name="Classeur"):
    return client.post("/api/v1/binders", json={"name": name}, headers=headers).json["id"]


def test_attach_existing_items_moves_them_into_binder(client, auth_headers):
    binder_id = _binder(client, auth_headers)
    # Éléments créés SANS classeur.
    note = client.post("/api/v1/notes", json={"title": "N", "content": "x"}, headers=auth_headers).json
    deck = client.post("/api/v1/decks", json={"name": "D"}, headers=auth_headers).json
    set_id = client.post("/api/v1/revision/sets", json={"name": "S", "type": "vf"}, headers=auth_headers).json["id"]

    resp = client.post(f"/api/v1/binders/{binder_id}/items", json={"items": [
        {"type": "note", "id": note["id"]},
        {"type": "deck", "id": deck["id"]},
        {"type": "set", "id": set_id},
    ]}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json["attached"] == 3

    # Les éléments apparaissent désormais filtrés par ce classeur.
    assert any(n["id"] == note["id"] for n in client.get(f"/api/v1/notes?binder_id={binder_id}", headers=auth_headers).json["data"])
    assert any(d["id"] == deck["id"] for d in client.get(f"/api/v1/decks?binder_id={binder_id}", headers=auth_headers).json["data"])


def test_detach_keeps_element_but_removes_from_binder(client, auth_headers):
    binder_id = _binder(client, auth_headers)
    note = client.post("/api/v1/notes", json={"title": "N", "content": "x", "binder_id": binder_id}, headers=auth_headers).json

    resp = client.post(f"/api/v1/binders/{binder_id}/items/detach",
                       json={"items": [{"type": "note", "id": note["id"]}]}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json["detached"] == 1

    # La note existe toujours (non supprimée) mais n'est plus dans le classeur.
    still_there = client.get(f"/api/v1/notes/{note['id']}", headers=auth_headers)
    assert still_there.status_code == 200
    in_binder = client.get(f"/api/v1/notes?binder_id={binder_id}", headers=auth_headers).json["data"]
    assert all(n["id"] != note["id"] for n in in_binder)


def test_attach_rejects_unknown_type(client, auth_headers):
    binder_id = _binder(client, auth_headers)
    resp = client.post(f"/api/v1/binders/{binder_id}/items",
                       json={"items": [{"type": "pdfx", "id": "1"}]}, headers=auth_headers)
    assert resp.status_code == 400


def test_attach_isolation_other_users_item(client, auth_headers):
    binder_id = _binder(client, auth_headers)
    # Élément d'un autre utilisateur.
    client.post("/api/v1/auth/register", json={"email": "c1@example.com", "username": "c1user", "password": "password123"})
    other = client.post("/api/v1/auth/login", json={"email": "c1@example.com", "password": "password123"}).json["access_token"]
    other_deck = client.post("/api/v1/decks", json={"name": "Pas à moi"}, headers={"Authorization": f"Bearer {other}"}).json

    resp = client.post(f"/api/v1/binders/{binder_id}/items",
                       json={"items": [{"type": "deck", "id": other_deck["id"]}]}, headers=auth_headers)
    assert resp.status_code in (403, 404)


def test_attach_to_other_users_binder_forbidden(client, auth_headers):
    my_deck = client.post("/api/v1/decks", json={"name": "Mon deck"}, headers=auth_headers).json
    client.post("/api/v1/auth/register", json={"email": "c1b@example.com", "username": "c1buser", "password": "password123"})
    other = client.post("/api/v1/auth/login", json={"email": "c1b@example.com", "password": "password123"}).json["access_token"]
    other_binder = client.post("/api/v1/binders", json={"name": "Classeur d'autrui"},
                               headers={"Authorization": f"Bearer {other}"}).json["id"]

    resp = client.post(f"/api/v1/binders/{other_binder}/items",
                       json={"items": [{"type": "deck", "id": my_deck["id"]}]}, headers=auth_headers)
    assert resp.status_code in (403, 404)
