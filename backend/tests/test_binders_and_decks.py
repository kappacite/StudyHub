def test_create_binder_root(client, auth_headers):
    response = client.post("/api/v1/binders", json={
        "name": "Chimie"
    }, headers=auth_headers)
    assert response.status_code == 201
    assert response.json["name"] == "Chimie"
    assert response.json["parent_id"] is None

def test_create_binder_subfolder(client, auth_headers):
    # Créer le parent
    p_resp = client.post("/api/v1/binders", json={"name": "Chimie"}, headers=auth_headers)
    parent_id = p_resp.json["id"]
    
    # Créer l'enfant
    c_resp = client.post("/api/v1/binders", json={
        "name": "Chimie Organique",
        "parent_id": parent_id
    }, headers=auth_headers)
    
    assert c_resp.status_code == 201
    assert c_resp.json["parent_id"] == parent_id

def test_get_binders_pagination(client, auth_headers):
    # Créer quelques binders
    for i in range(5):
        client.post("/api/v1/binders", json={"name": f"Folder {i}"}, headers=auth_headers)
        
    response = client.get("/api/v1/binders?page=1&per_page=3", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json["data"]) == 3
    assert response.json["pagination"]["total"] == 5
    assert response.json["pagination"]["pages"] == 2

def test_binder_isolation(client, auth_headers, test_user):
    # Créer un binder avec user 1
    resp1 = client.post("/api/v1/binders", json={"name": "User1 Folder"}, headers=auth_headers)
    binder_id = resp1.json["id"]
    
    # Créer user 2
    client.post("/api/v1/auth/register", json={
        "email": "user2@example.com",
        "username": "user2",
        "password": "password123"
    })
    
    # Se connecter comme user 2
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "user2@example.com",
        "password": "password123"
    })
    token2 = login_resp.json["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # User 2 essaie de lire le binder de User 1
    resp2 = client.get(f"/api/v1/binders/{binder_id}", headers=headers2)
    assert resp2.status_code == 403
    assert resp2.json["error"]["code"] == "FORBIDDEN"

def test_create_deck(client, auth_headers):
    response = client.post("/api/v1/decks", json={
        "name": "Vocabulaire Espagnol",
        "description": "Cartes de révision pour le vocabulaire"
    }, headers=auth_headers)
    assert response.status_code == 201
    assert response.json["name"] == "Vocabulaire Espagnol"
    assert response.json["binder_id"] is None


def test_deck_card_is_recto_verso_only(client, auth_headers):
    """D3c : un deck ne contient que des flashcards recto/verso. Les anciens
    champs typés (card_type/payload, PR #48) ne sont plus exposés par l'API deck."""
    deck = client.post("/api/v1/decks", json={"name": "Bases"}, headers=auth_headers)
    deck_id = deck.json["id"]
    card = client.post(f"/api/v1/decks/{deck_id}/cards", json={
        "front": "Capitale de l'Italie ?", "back": "Rome"
    }, headers=auth_headers)
    assert card.status_code == 201
    assert card.json["front"] == "Capitale de l'Italie ?"
    assert card.json["back"] == "Rome"
    # Le type/payload typés ont migré vers les ensembles de révision.
    assert "card_type" not in card.json
    assert "payload" not in card.json
