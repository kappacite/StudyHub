import pytest
from app.extensions import db
from app.models.note import Note
from app.models.deck import Deck
from app.models.flashcard import Flashcard
from app.models.diagram import Diagram
from app.dao.search_dao import SearchDAO
from app.services.search_service import SearchService

@pytest.fixture
def search_service():
    search_dao = SearchDAO(db.session)
    return SearchService(search_dao)

def test_search_returns_notes_matching_query(app, search_service, test_user):
    with app.app_context():
        # Create note
        note = Note(
            title="Biologie Moléculaire",
            content="L'ADN est composé de nucléotides qui forment une double hélice.",
            user_id=test_user["id"]
        )
        db.session.add(note)
        db.session.commit()

        # Search
        result = search_service.search(test_user["id"], "ADN")
        
        assert result["total"] == 1
        assert len(result["results"]["notes"]) == 1
        assert result["results"]["notes"][0]["title"] == "Biologie Moléculaire"
        assert "ADN" in result["results"]["notes"][0]["excerpt"]

def test_search_filters_by_type(app, search_service, test_user):
    with app.app_context():
        note = Note(
            title="Mathématiques discrètes",
            content="Graphes et algèbre de Boole",
            user_id=test_user["id"]
        )
        deck = Deck(
            name="Mathématiques avancées",
            description="Algèbre linéaire et calcul",
            user_id=test_user["id"]
        )
        db.session.add_all([note, deck])
        db.session.commit()

        # Search only for notes
        result = search_service.search(test_user["id"], "Mathématiques", types=["note"])
        
        assert len(result["results"]["notes"]) == 1
        assert len(result["results"]["decks"]) == 0

def test_search_user_isolation(app, search_service, test_user):
    with app.app_context():
        # User 2 manually created
        from app.models.user import User
        user2 = User(email="user2@example.com", username="user2")
        user2.set_password("password123")
        db.session.add(user2)
        db.session.commit()

        note_user2 = Note(
            title="Secret Note",
            content="This is private content belonging to user 2.",
            user_id=user2.id
        )
        db.session.add(note_user2)
        db.session.commit()

        # Search with user 1's ID
        result = search_service.search(test_user["id"], "Secret")
        assert result["total"] == 0

def test_search_query_too_short_returns_400(client, auth_headers):
    # Query length < 2 must return 400
    response = client.get("/api/v1/search?q=a", headers=auth_headers)
    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "BAD_REQUEST"

def test_search_excerpt_contains_mark_tag(app, search_service, test_user):
    with app.app_context():
        note = Note(
            title="Optique géométrique",
            content="La réfraction de la lumière est décrite par les lois de Snell-Descartes.",
            user_id=test_user["id"]
        )
        db.session.add(note)
        db.session.commit()

        result = search_service.search(test_user["id"], "lumière")
        
        excerpt = result["results"]["notes"][0]["excerpt"]
        assert "<mark>lumière</mark>" in excerpt

def test_search_sqlite_fallback_works(app, search_service, test_user):
    with app.app_context():
        # Creating multiple entity types to confirm SQLite LIKE search fallback
        note = Note(title="Physique Quantique", content="Dualité onde-corpuscule", user_id=test_user["id"])
        deck = Deck(name="Physique Statistique", description="Introduction aux états", user_id=test_user["id"])
        db.session.add_all([note, deck])
        db.session.commit()

        result = search_service.search(test_user["id"], "Physique")
        assert result["total"] == 2
        assert len(result["results"]["notes"]) == 1
        assert len(result["results"]["decks"]) == 1
