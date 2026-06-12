import pytest
from app.extensions import db
from app.models.binder import Binder
from app.models.note import Note
from app.models.deck import Deck
from app.models.flashcard import Flashcard
from app.models.user import User

@pytest.fixture
def other_user(app):
    with app.app_context():
        user = User(email="other@example.com", username="otheruser")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "password": "password123"
        }

@pytest.fixture
def other_auth_headers(client, other_user):
    response = client.post("/api/v1/auth/login", json={
        "email": other_user["email"],
        "password": other_user["password"]
    })
    token = response.json["access_token"]
    return {
        "Authorization": f"Bearer {token}"
    }

def test_community_marketplace_and_cloning(client, auth_headers, other_auth_headers, test_user, other_user):
    # 1. Créer un Binder public avec tags et description par test_user
    binder_data = {
        "name": "Chimie Organique L1",
        "is_public": True,
        "description": "Cours complet de chimie organique du premier semestre",
        "tags": ["Chimie", "L1", "Science"]
    }
    
    resp = client.post("/api/v1/binders", json=binder_data, headers=auth_headers)
    assert resp.status_code == 201
    binder_id = resp.json["id"]
    
    # Ajouter une note avec placeholder dans ce binder
    note_data = {
        "title": "Les Alcènes",
        "content": "Un alcène possède une [double liaison C=C]{def:insaturée}.",
        "binder_id": binder_id
    }
    client.post("/api/v1/notes", json=note_data, headers=auth_headers)
    
    # Simuler une révision de la carte pour changer son SM-2
    with client.application.app_context():
        binder_obj = db.session.query(Binder).filter_by(id=binder_id).first()
        deck = db.session.query(Deck).filter_by(binder_id=binder_obj._id).first()
        card = db.session.query(Flashcard).filter_by(deck_id=deck.id).first()
        card.interval = 15
        card.repetitions = 3
        card.ease_factor = 2.8
        db.session.commit()
        
    # 2. Explorer le marketplace avec other_user
    explore_resp = client.get("/api/v1/packages?search=Chimie", headers=other_auth_headers)
    assert explore_resp.status_code == 200
    assert len(explore_resp.json["data"]) == 1
    assert explore_resp.json["data"][0]["name"] == "Chimie Organique L1"
    
    # 3. Cloner le package avec other_user
    clone_resp = client.post(f"/api/v1/packages/{binder_id}/clone", headers=other_auth_headers)
    assert clone_resp.status_code == 201
    cloned_binder_id = clone_resp.json["id"]
    
    # 4. Vérifier les données clonées pour other_user
    with client.application.app_context():
        # Vérifier que le Binder appartient à other_user et est privé par défaut
        cloned_binder = db.session.query(Binder).filter_by(id=cloned_binder_id).first()
        assert cloned_binder is not None
        assert cloned_binder.user_id == other_user["id"]
        assert cloned_binder.is_public is False
        assert cloned_binder.original_author_id == test_user["id"]
        
        # Vérifier la note clonée
        cloned_note = db.session.query(Note).filter_by(binder_id=cloned_binder._id).first()
        assert cloned_note is not None
        assert cloned_note.user_id == other_user["id"]
        assert "double liaison C=C" in cloned_note.content
        
        # Vérifier le deck et la carte clonée
        cloned_deck = db.session.query(Deck).filter_by(binder_id=cloned_binder._id).first()
        assert cloned_deck is not None
        assert cloned_deck.user_id == other_user["id"]
        
        cloned_card = db.session.query(Flashcard).filter_by(deck_id=cloned_deck.id).first()
        assert cloned_card is not None
        # Le SM-2 doit être réinitialisé
        assert cloned_card.interval == 0
        assert cloned_card.repetitions == 0
        assert cloned_card.ease_factor == 2.5
        
        # Vérifier l'original
        original_binder = db.session.query(Binder).filter_by(id=binder_id).first()
        assert original_binder.fork_count == 1

def test_public_package_preview(client, auth_headers):
    # 1. Créer un Binder public avec note par test_user
    binder_data = {
        "name": "Physique Quantique L3",
        "is_public": True,
        "description": "Cours avancé",
        "tags": ["Physique", "L3"]
    }
    
    resp = client.post("/api/v1/binders", json=binder_data, headers=auth_headers)
    assert resp.status_code == 201
    binder_id = resp.json["id"]
    
    note_data = {
        "title": "Équation de Schrödinger",
        "content": "Description",
        "binder_id": binder_id
    }
    client.post("/api/v1/notes", json=note_data, headers=auth_headers)
    
    # 2. Appeler la route publique de preview sans en-tête d'authentification (Guest)
    preview_resp = client.get(f"/api/v1/packages/{binder_id}")
    assert preview_resp.status_code == 200
    json_data = preview_resp.json
    
    assert json_data["binder"]["name"] == "Physique Quantique L3"
    assert "Équation de Schrödinger" in json_data["notes"]
