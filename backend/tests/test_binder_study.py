"""Réviser un dossier entier — agrégation des cartes dues sur tous les decks
d'un classeur (GET /binders/<id>/study)."""


def _binder(client, headers, name="Cours"):
    return client.post("/api/v1/binders", json={"name": name}, headers=headers).json["id"]


def _deck_in_binder(client, headers, binder_id, name):
    return client.post("/api/v1/decks", json={"name": name, "binder_id": binder_id}, headers=headers).json["id"]


def _card(client, headers, deck_id, front, back):
    return client.post(f"/api/v1/decks/{deck_id}/cards", json={"front": front, "back": back}, headers=headers).json["id"]


def test_binder_study_aggregates_due_cards_across_decks(client, auth_headers):
    binder_id = _binder(client, auth_headers)
    d1 = _deck_in_binder(client, auth_headers, binder_id, "Deck A")
    d2 = _deck_in_binder(client, auth_headers, binder_id, "Deck B")
    c1 = _card(client, auth_headers, d1, "Q1", "R1")
    c2 = _card(client, auth_headers, d2, "Q2", "R2")

    resp = client.get(f"/api/v1/binders/{binder_id}/study", headers=auth_headers)
    assert resp.status_code == 200
    ids = {c["id"] for c in resp.json}
    assert ids == {c1, c2}
    # Chaque carte porte son deck_id d'origine (le front notifie la réponse via ce deck).
    deck_ids = {c["deck_id"] for c in resp.json}
    assert deck_ids == {d1, d2}


def test_binder_study_excludes_other_binders_decks(client, auth_headers):
    target = _binder(client, auth_headers, "Cible")
    other = _binder(client, auth_headers, "Autre")
    d_in = _deck_in_binder(client, auth_headers, target, "Dans")
    d_out = _deck_in_binder(client, auth_headers, other, "Dehors")
    c_in = _card(client, auth_headers, d_in, "Q", "R")
    _card(client, auth_headers, d_out, "Q", "R")

    resp = client.get(f"/api/v1/binders/{target}/study", headers=auth_headers)
    assert resp.status_code == 200
    assert {c["id"] for c in resp.json} == {c_in}


def test_binder_study_isolation_other_user(client, auth_headers):
    client.post("/api/v1/auth/register", json={"email": "bs@example.com", "username": "bsuser", "password": "password123"})
    other = client.post("/api/v1/auth/login", json={"email": "bs@example.com", "password": "password123"}).json["access_token"]
    other_binder = client.post("/api/v1/binders", json={"name": "Pas à moi"},
                               headers={"Authorization": f"Bearer {other}"}).json["id"]

    resp = client.get(f"/api/v1/binders/{other_binder}/study", headers=auth_headers)
    assert resp.status_code in (403, 404)
