"""Tests A1 — flashcard avancée : mode inversé (D7), tuning SM-2 (D4), historique."""


def _new_deck(client, auth_headers, **kw):
    payload = {"name": "Deck"}
    payload.update(kw)
    return client.post("/api/v1/decks", json=payload, headers=auth_headers).json


def test_deck_defaults_not_reversed(client, auth_headers):
    deck = _new_deck(client, auth_headers)
    assert deck["reversed"] is False
    assert deck["tuning_default"] == 1.0


def test_reversed_deck_materializes_mirror_card(client, auth_headers):
    deck = _new_deck(client, auth_headers, name="Inversé", reversed=True)
    deck_id = deck["id"]
    client.post(f"/api/v1/decks/{deck_id}/cards", json={"front": "chat", "back": "cat"}, headers=auth_headers)

    # La liste de gestion ne montre que l'originale...
    listed = client.get(f"/api/v1/decks/{deck_id}/cards", headers=auth_headers)
    assert listed.json["pagination"]["total"] == 1
    # ...mais l'étude planifie l'originale ET son miroir (verso→recto).
    study = client.get(f"/api/v1/decks/{deck_id}/study", headers=auth_headers)
    assert len(study.json) == 2
    fronts = sorted(c["front"] for c in study.json)
    assert fronts == ["cat", "chat"]


def test_toggle_reversed_on_then_off(client, auth_headers):
    deck = _new_deck(client, auth_headers, name="Toggle")
    deck_id = deck["id"]
    client.post(f"/api/v1/decks/{deck_id}/cards", json={"front": "uno", "back": "one"}, headers=auth_headers)

    # Activer le mode inversé crée le miroir.
    client.put(f"/api/v1/decks/{deck_id}", json={"reversed": True}, headers=auth_headers)
    assert len(client.get(f"/api/v1/decks/{deck_id}/study", headers=auth_headers).json) == 2

    # Le désactiver retire les miroirs.
    client.put(f"/api/v1/decks/{deck_id}", json={"reversed": False}, headers=auth_headers)
    assert len(client.get(f"/api/v1/decks/{deck_id}/study", headers=auth_headers).json) == 1


def test_deleting_original_deletes_mirror(client, auth_headers):
    deck = _new_deck(client, auth_headers, name="Del", reversed=True)
    deck_id = deck["id"]
    card = client.post(f"/api/v1/decks/{deck_id}/cards", json={"front": "a", "back": "b"}, headers=auth_headers).json
    client.delete(f"/api/v1/decks/{deck_id}/cards/{card['id']}", headers=auth_headers)
    assert client.get(f"/api/v1/decks/{deck_id}/study", headers=auth_headers).json == []


def test_card_tuning_lengthens_interval(client, auth_headers):
    # Deck normal (tuning 1.0) vs deck espacé (tuning_default 3.0) : intervalle plus long.
    d1 = _new_deck(client, auth_headers, name="Normal")["id"]
    d2 = _new_deck(client, auth_headers, name="Espacé", tuning_default=3.0)["id"]
    c1 = client.post(f"/api/v1/decks/{d1}/cards", json={"front": "x", "back": "y"}, headers=auth_headers).json
    c2 = client.post(f"/api/v1/decks/{d2}/cards", json={"front": "x", "back": "y"}, headers=auth_headers).json

    # 2 révisions réussies pour passer en phase « interval * ease ».
    for _ in range(3):
        r1 = client.post(f"/api/v1/decks/{d1}/study/answer/{c1['id']}", json={"score": 5}, headers=auth_headers).json
        r2 = client.post(f"/api/v1/decks/{d2}/study/answer/{c2['id']}", json={"score": 5}, headers=auth_headers).json
    assert r2["interval"] > r1["interval"]


def test_history_endpoint_returns_grades(client, auth_headers):
    deck_id = _new_deck(client, auth_headers, name="Hist")["id"]
    card = client.post(f"/api/v1/decks/{deck_id}/cards", json={"front": "q", "back": "a"}, headers=auth_headers).json
    client.post(f"/api/v1/decks/{deck_id}/study/answer/{card['id']}", json={"score": 4}, headers=auth_headers)
    client.post(f"/api/v1/decks/{deck_id}/study/answer/{card['id']}", json={"score": 2}, headers=auth_headers)

    hist = client.get(f"/api/v1/decks/{deck_id}/cards/{card['id']}/history", headers=auth_headers)
    assert hist.status_code == 200
    grades = [e["grade"] for e in hist.json["data"]]
    assert grades == [4, 2]
