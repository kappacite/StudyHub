def test_create_and_study_cards(client, auth_headers):
    # 1. Créer un deck
    deck_resp = client.post("/api/v1/decks", json={
        "name": "Maths",
        "description": "Formules"
    }, headers=auth_headers)
    deck_id = deck_resp.json["id"]
    
    # 2. Créer une flashcard
    card_resp = client.post(f"/api/v1/decks/{deck_id}/cards", json={
        "front": "Dérivée de x²",
        "back": "2x"
    }, headers=auth_headers)
    assert card_resp.status_code == 201
    card_id = card_resp.json["id"]
    
    # 3. Récupérer les cartes à réviser
    study_resp = client.get(f"/api/v1/decks/{deck_id}/study", headers=auth_headers)
    assert study_resp.status_code == 200
    assert len(study_resp.json) == 1
    assert study_resp.json[0]["id"] == card_id
    
    # 4. Répondre avec succès (score 5)
    ans1_resp = client.post(
        f"/api/v1/decks/{deck_id}/study/answer/{card_id}",
        json={"score": 5},
        headers=auth_headers
    )
    assert ans1_resp.status_code == 200
    assert ans1_resp.json["repetitions"] == 1
    assert ans1_resp.json["interval"] == 1
    assert ans1_resp.json["ease_factor"] > 2.5
    
    # Simuler le fait qu'elle ait été révisée (pour la deuxième fois en succès, reps=2, interval=6)
    ans2_resp = client.post(
        f"/api/v1/decks/{deck_id}/study/answer/{card_id}",
        json={"score": 4},
        headers=auth_headers
    )
    assert ans2_resp.status_code == 200
    assert ans2_resp.json["repetitions"] == 2
    assert ans2_resp.json["interval"] == 6
    
    # 5. Répondre avec échec (score 1)
    ans3_resp = client.post(
        f"/api/v1/decks/{deck_id}/study/answer/{card_id}",
        json={"score": 1},
        headers=auth_headers
    )
    assert ans3_resp.status_code == 200
    assert ans3_resp.json["repetitions"] == 0
    assert ans3_resp.json["interval"] == 1
