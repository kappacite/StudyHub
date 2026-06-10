import pytest
from unittest.mock import patch

def test_regression_note_creation_and_update(client, auth_headers):
    # 1. On doit toujours pouvoir créer des notes
    note_resp = client.post("/api/v1/notes", json={
        "title": "Nouvelle note de test",
        "content": "Contenu de la note"
    }, headers=auth_headers)
    assert note_resp.status_code == 201
    note_id = note_resp.json["id"]
    assert note_resp.json["title"] == "Nouvelle note de test"

    # 2. On doit toujours pouvoir sauvegarder les notes
    save_resp = client.put(f"/api/v1/notes/{note_id}", json={
        "title": "Note de test mise à jour",
        "content": "Contenu de la note mis à jour avec un {{trou::mot caché}}."
    }, headers=auth_headers)
    assert save_resp.status_code == 200
    assert save_resp.json["title"] == "Note de test mise à jour"
    assert save_resp.json["content"] == "Contenu de la note mis à jour avec un {{trou::mot caché}}."
    assert len(save_resp.json["flashcards"]) > 0  # Assurer que les placeholders sont créés dans le deck fantôme

def test_regression_flashcard_creation_and_review(client, auth_headers):
    # 1. Créer un deck
    deck_resp = client.post("/api/v1/decks", json={
        "name": "Deck Test",
        "description": "Description Test"
    }, headers=auth_headers)
    assert deck_resp.status_code == 201
    deck_id = deck_resp.json["id"]

    # 2. On doit toujours pouvoir créer des flashcard
    card_resp = client.post(f"/api/v1/decks/{deck_id}/cards", json={
        "front": "Question de test",
        "back": "Réponse de test"
    }, headers=auth_headers)
    assert card_resp.status_code == 201
    card_id = card_resp.json["id"]

    # 3. On doit toujours pouvoir réviser
    review_resp = client.patch(f"/api/v1/flashcards/{card_id}/review", json={
        "score": 4
    }, headers=auth_headers)
    assert review_resp.status_code == 200
    assert review_resp.json["repetitions"] == 1
    assert review_resp.json["ease_factor"] > 0

@patch("app.services.ai_service.AIService.analyze_blurting")
def test_regression_blurting_page_blanche(mock_analyze_blurting, client, auth_headers, test_user, app):
    # Setup de la base de données de test
    from app.extensions import db
    from app.models.binder import Binder
    from app.models.note import Note
    
    with app.app_context():
        binder = Binder(user_id=test_user["id"], name="Classeur Test")
        db.session.add(binder)
        db.session.commit()
        
        note = Note(user_id=test_user["id"], binder_id=binder.id, title="Note Test", content="Contenu de base")
        db.session.add(note)
        db.session.commit()
        note_id = note.id

    # Mock de la réponse du service IA
    mock_analyze_blurting.return_value = {
        "retention_score": 95,
        "concepts": [],
        "suggested_flashcards": [],
        "general_feedback": "Excellente restitution."
    }

    # 4. On doit toujours pouvoir faire la page blanche
    resp = client.post("/api/v1/blurting/analyze", json={
        "note_id": note_id,
        "user_blurting": "Ma restitution de test",
        "duration_seconds": 60
    }, headers=auth_headers)
    
    assert resp.status_code == 200
    assert resp.json["retention_score"] == 95
    assert resp.json["general_feedback"] == "Excellente restitution."
