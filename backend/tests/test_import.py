import io
import zipfile
import sqlite3
import json
import pytest
from datetime import datetime
from app.extensions import db
from app.models.deck import Deck
from app.models.flashcard import Flashcard
from app.utils.anki_parser import parse_apkg

def create_dummy_apkg(deck_name="Test Deck", notes_data=None):
    if notes_data is None:
        notes_data = [
            ("Front 1", "Back 1", "tag1 tag2"),
            ("Front 2", "Back 2", "tag2 tag3")
        ]
        
    import tempfile
    import os
    fd, path = tempfile.mkstemp()
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        # Table col
        cursor.execute("CREATE TABLE col (decks TEXT)")
        decks_info = {
            "123": {
                "id": 123,
                "name": deck_name
            }
        }
        cursor.execute("INSERT INTO col VALUES (?)", (json.dumps(decks_info),))
        
        # Table notes et cards
        cursor.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, flds TEXT, tags TEXT)")
        cursor.execute("CREATE TABLE cards (id INTEGER PRIMARY KEY, nid INTEGER, did INTEGER)")
        
        for idx, (front, back, tags) in enumerate(notes_data):
            note_id = 1000 + idx
            card_id = 2000 + idx
            flds = f"{front}\x1f{back}"
            cursor.execute("INSERT INTO notes (id, flds, tags) VALUES (?, ?, ?)", (note_id, flds, tags))
            cursor.execute("INSERT INTO cards (id, nid, did) VALUES (?, ?, 123)", (card_id, note_id))
            
        conn.commit()
        conn.close()
        
        with open(path, "rb") as f:
            db_bytes = f.read()
    finally:
        os.remove(path)
        
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as z:
        z.writestr("collection.anki2", db_bytes)
        
    return zip_buffer.getvalue()

# --- Tests Unitaires Parser ---

def test_parse_valid_apkg_returns_cards():
    apkg_bytes = create_dummy_apkg("Biologie", [
        ("Mitose", "Division cellulaire", "bio cellule"),
        ("ADN", "Acide Désoxyribonucléique", "bio adn")
    ])
    
    decks, warnings = parse_apkg(apkg_bytes)
    
    assert len(decks) == 1
    assert decks[0]["name"] == "Biologie"
    assert len(decks[0]["cards"]) == 2
    assert decks[0]["cards"][0]["front"] == "Mitose"
    assert decks[0]["cards"][0]["back"] == "Division cellulaire"
    assert decks[0]["cards"][0]["tags"] == ["bio", "cellule"]
    assert len(warnings) == 0

def test_parse_corrupted_file_raises_error():
    with pytest.raises(ValueError, match="archive ZIP"):
        parse_apkg(b"not a zip file content")

def test_parse_multi_field_card_uses_first_two_fields():
    # Note avec 3 champs (recto, verso, notes additionnelles)
    apkg_bytes = create_dummy_apkg("Deck Multi", [
        ("Recto\x1fVerso\x1fChampAdditionnel", "", "")
    ])
    
    decks, warnings = parse_apkg(apkg_bytes)
    assert len(decks) == 1
    assert decks[0]["cards"][0]["front"] == "Recto"
    assert decks[0]["cards"][0]["back"] == "Verso"
    assert len(warnings) > 0
    assert "plus de 2 champs" in warnings[0]

# --- Tests d'Intégration API / Service ---

def test_import_creates_deck_and_cards_in_db(app, client, auth_headers, test_user):
    apkg_bytes = create_dummy_apkg("Deck Anatomie", [
        ("Fémur", "Os de la cuisse", "squelette os"),
        ("Coeur", "Muscle cardiaque", "cardio")
    ])
    
    data = {
        "file": (io.BytesIO(apkg_bytes), "anatomie.apkg")
    }
    
    response = client.post(
        "/api/v1/import/anki",
        data=data,
        headers=auth_headers,
        content_type="multipart/form-data"
    )
    
    assert response.status_code == 201
    res_data = response.json
    assert res_data["deck_name"] == "Deck Anatomie"
    assert res_data["cards_imported"] == 2
    assert res_data["cards_skipped"] == 0
    
    # Vérification en base de données
    with app.app_context():
        deck = db.session.get(Deck, res_data["deck_id"])
        assert deck is not None
        assert deck.name == "Deck Anatomie"
        assert deck.user_id == test_user["id"]
        assert len(deck.cards) == 2
        assert len(deck.tags) == 3  # "squelette", "os", "cardio"

def test_import_sets_default_sm2_parameters(app, client, auth_headers):
    apkg_bytes = create_dummy_apkg("Deck SM2", [
        ("Question", "Réponse", "")
    ])
    
    response = client.post(
        "/api/v1/import/anki",
        data={"file": (io.BytesIO(apkg_bytes), "sm2.apkg")},
        headers=auth_headers,
        content_type="multipart/form-data"
    )
    
    assert response.status_code == 201
    deck_id = response.json["deck_id"]
    
    with app.app_context():
        deck = db.session.get(Deck, deck_id)
        card = deck.cards[0]
        assert card.ease_factor == 2.5
        assert card.interval == 0
        assert card.repetitions == 0
        assert card.next_review is not None

def test_import_wrong_mimetype_returns_400(client, auth_headers):
    response = client.post(
        "/api/v1/import/anki",
        data={"file": (io.BytesIO(b"content"), "document.txt")},
        headers=auth_headers,
        content_type="multipart/form-data"
    )
    assert response.status_code == 400
    assert "Seuls les fichiers .apkg" in response.json["error"]["message"]

def test_import_file_too_large_returns_413(client, auth_headers):
    # Fichier simulé de 51 Mo (limite à 50 Mo)
    large_data = b"0" * (51 * 1024 * 1024)
    response = client.post(
        "/api/v1/import/anki",
        data={"file": (io.BytesIO(large_data), "large.apkg")},
        headers=auth_headers,
        content_type="multipart/form-data"
    )
    assert response.status_code == 413

def test_import_user_isolation(app, client, auth_headers, test_user):
    # Importer un deck avec l'utilisateur 1
    apkg_bytes = create_dummy_apkg("Deck Secret", [("S", "R", "")])
    response = client.post(
        "/api/v1/import/anki",
        data={"file": (io.BytesIO(apkg_bytes), "secret.apkg")},
        headers=auth_headers,
        content_type="multipart/form-data"
    )
    assert response.status_code == 201
    deck_id = response.json["deck_id"]
    
    # Créer un second utilisateur manuellement
    with app.app_context():
        from app.models.user import User
        user2 = User(email="test2@example.com", username="testuser2")
        user2.set_password("password123")
        db.session.add(user2)
        db.session.commit()
        db.session.refresh(user2)
        user2_id = user2.id
        
    # Vérifier que le deck secret appartient bien à l'utilisateur 1 et non à l'utilisateur 2
    with app.app_context():
        deck = db.session.get(Deck, deck_id)
        assert deck.user_id == test_user["id"]
        assert deck.user_id != user2_id
