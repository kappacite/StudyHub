import pytest
from app.utils.placeholder_parser import extract_placeholders_from_text
from app.models.deck import Deck
from app.models.flashcard import Flashcard
from app.models.study_session import StudySession
from app.extensions import db

def test_placeholder_parsing_logic():
    content = (
        "Le chat {{trou::mange}} la souris.\n"
        "{{qcm::Qui a écrit Les Misérables ?::Zola|*Victor Hugo*|Maupassant}}\n"
        "{{ordre::Cycle de l'eau::Évaporation > Condensation > Précipitation}}\n"
        "{{assoc::Capitales::France=Paris | Espagne=Madrid}}\n"
        "{{vf::La Terre est plate::Faux::La Terre est ronde.}}"
    )
    
    placeholders = extract_placeholders_from_text(content, note_id=1)
    
    assert len(placeholders) == 5
    
    # 1. Trou
    assert placeholders[0]["type"] == "trou"
    assert "Le chat [...] la souris." in placeholders[0]["front"]
    assert placeholders[0]["back"] == "mange"
    
    # 2. QCM
    assert placeholders[1]["type"] == "qcm"
    assert "Qui a écrit Les Misérables ?" in placeholders[1]["front"]
    assert placeholders[1]["back"] == "Victor Hugo"
    
    # 3. Ordre
    assert placeholders[2]["type"] == "ordre"
    assert "Cycle de l'eau" in placeholders[2]["front"]
    assert placeholders[2]["back"] == "Évaporation > Condensation > Précipitation"
    
    # 4. Assoc
    assert placeholders[3]["type"] == "assoc"
    assert "Capitales" in placeholders[3]["front"]
    assert placeholders[3]["back"] == "France=Paris | Espagne=Madrid"
    
    # 5. VF
    assert placeholders[4]["type"] == "vf"
    assert "La Terre est plate" in placeholders[4]["front"]
    assert "Faux" in placeholders[4]["back"]
    assert "La Terre est ronde" in placeholders[4]["back"]

def test_note_phantom_deck_sync(client, auth_headers):
    # 1. Créer une note avec des placeholders
    note_data = {
        "title": "Notes sur l'Histoire",
        "content": "La capitale de la France est {{trou::Paris}}."
    }
    
    response = client.post("/api/v1/notes", json=note_data, headers=auth_headers)
    assert response.status_code == 201
    note_id = response.json["id"]
    
    # 2. Vérifier que le deck fantôme est créé
    with client.application.app_context():
        deck = db.session.query(Deck).filter_by(note_id=note_id).first()
        assert deck is not None
        assert deck.name == f"[Phantom] Note: {note_data['title']}"
        
        # Vérifier que la carte est créée
        cards = db.session.query(Flashcard).filter_by(deck_id=deck.id).all()
        assert len(cards) == 1
        assert "La capitale de la France est [...]" in cards[0].front
        assert cards[0].back == "Paris"
        card_id = cards[0].id
        placeholder_hash = cards[0].placeholder_hash

    # 3. Mettre à jour la note : changer le placeholder
    update_data = {
        "title": "Notes sur l'Histoire",
        "content": "La capitale de la France est {{trou::Paris}}.\nQui a écrit Germinal ? {{trou::Zola}}"
    }
    
    response = client.put(f"/api/v1/notes/{note_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    
    with client.application.app_context():
        deck = db.session.query(Deck).filter_by(note_id=note_id).first()
        cards = db.session.query(Flashcard).filter_by(deck_id=deck.id).all()
        # Devrait avoir 2 cartes maintenant
        assert len(cards) == 2
        
    # 4. Retirer un placeholder
    update_data_2 = {
        "title": "Notes sur l'Histoire",
        "content": "La capitale de la France est {{trou::Paris}}."
    }
    
    response = client.put(f"/api/v1/notes/{note_id}", json=update_data_2, headers=auth_headers)
    assert response.status_code == 200
    
    with client.application.app_context():
        deck = db.session.query(Deck).filter_by(note_id=note_id).first()
        cards = db.session.query(Flashcard).filter_by(deck_id=deck.id).all()
        # Devrait redevenir 1 seule carte
        assert len(cards) == 1
        assert cards[0].back == "Paris"

def test_review_card_direct_api(client, auth_headers):
    # 1. Créer une note avec placeholder
    note_data = {
        "title": "Notes Physiques",
        "content": "La formule de la force est {{trou::F=ma}}."
    }
    response = client.post("/api/v1/notes", json=note_data, headers=auth_headers)
    assert response.status_code == 201
    note_id = response.json["id"]
    
    with client.application.app_context():
        deck = db.session.query(Deck).filter_by(note_id=note_id).first()
        card = db.session.query(Flashcard).filter_by(deck_id=deck.id).first()
        card_id = card.id
        
    # 2. Réviser la carte via l'API globale PATCH
    review_data = {"score": 4}
    response = client.patch(f"/api/v1/flashcards/{card_id}/review", json=review_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json["interval"] > 0
    
    # 3. Vérifier qu'une session d'étude a été enregistrée
    with client.application.app_context():
        session = db.session.query(StudySession).filter_by(flashcard_id=card_id).first()
        assert session is not None
        assert session.grade == 4
        assert session.module == "flashcard"

def test_diagram_occlusion_sync(client, auth_headers):
    # 1. Créer un diagramme avec des masques d'occlusion
    import json
    diag_data = {
        "title": "Diagramme de biologie",
        "code": json.dumps({
            "type": "visual",
            "backgroundImage": "data:image/png;base64,abc",
            "nodes": [],
            "connections": [],
            "masks": [
                {"id": "mask-1", "x": 10, "y": 20, "width": 50, "height": 30, "label": "Noyau"}
            ]
        })
    }
    response = client.post("/api/v1/diagrams", json=diag_data, headers=auth_headers)
    assert response.status_code == 201
    diag_id = response.json["id"]
    
    # 2. Créer une note qui inclut ce diagramme
    note_data = {
        "title": "Cours de biologie cellulaire",
        "content": f"Voici le schéma de la cellule : [diagram:{diag_id}]."
    }
    response = client.post("/api/v1/notes", json=note_data, headers=auth_headers)
    assert response.status_code == 201
    note_id = response.json["id"]
    
    # 3. Vérifier que la flashcard d'occlusion est créée dans le deck fantôme
    with client.application.app_context():
        deck = db.session.query(Deck).filter_by(note_id=note_id).first()
        assert deck is not None
        cards = db.session.query(Flashcard).filter_by(deck_id=deck.id).all()
        assert len(cards) == 1
        assert cards[0].back == "Noyau"
        assert cards[0].original_text == f"[diagram:{diag_id}] mask:mask-1"
        
    # 4. Mettre à jour le diagramme : ajouter un masque
    diag_update_data = {
        "code": json.dumps({
            "type": "visual",
            "backgroundImage": "data:image/png;base64,abc",
            "nodes": [],
            "connections": [],
            "masks": [
                {"id": "mask-1", "x": 10, "y": 20, "width": 50, "height": 30, "label": "Noyau"},
                {"id": "mask-2", "x": 100, "y": 120, "width": 60, "height": 40, "label": "Mitochondrie"}
            ]
        })
    }
    response = client.put(f"/api/v1/diagrams/{diag_id}", json=diag_update_data, headers=auth_headers)
    assert response.status_code == 200
    
    # 5. Vérifier que la note s'est synchronisée automatiquement
    with client.application.app_context():
        deck = db.session.query(Deck).filter_by(note_id=note_id).first()
        cards = db.session.query(Flashcard).filter_by(deck_id=deck.id).all()
        # Devrait maintenant avoir 2 cartes
        assert len(cards) == 2
        backs = [c.back for c in cards]
        assert "Noyau" in backs
        assert "Mitochondrie" in backs
