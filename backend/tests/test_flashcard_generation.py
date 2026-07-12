from unittest.mock import patch
from app.models.binder import Binder
from app.models.deck import Deck
from app.models.flashcard import Flashcard
from app.models.note import Note
from app.extensions import db

AI_CARDS = [
    {"front": "Quelle est la capitale de la France ?", "back": "Paris"},
    {"front": "Combien font 2 + 2 ?", "back": "4"},
]


@patch("app.services.ai_service.AIService.generate_flashcards")
def test_generate_from_note(mock_gen, client, auth_headers, test_user, app):
    mock_gen.return_value = AI_CARDS
    with app.app_context():
        note = Note(user_id=test_user["id"], title="Géo", content="La capitale de la France est Paris.")
        db.session.add(note)
        db.session.commit()
        note_id = note.id

    resp = client.post("/api/v1/flashcards/generate", json={
        "source_type": "note",
        "note_id": note_id,
    }, headers=auth_headers)

    assert resp.status_code == 200
    body = resp.json
    assert body["count"] == 2
    assert body["flashcards"][0]["front"].startswith("Quelle")
    mock_gen.assert_called_once()


@patch("app.services.ai_service.AIService.generate_flashcards")
def test_generate_from_binder_aggregates_notes(mock_gen, client, auth_headers, test_user, app):
    mock_gen.return_value = AI_CARDS
    with app.app_context():
        binder = Binder(user_id=test_user["id"], name="Bio")
        db.session.add(binder)
        db.session.commit()
        db.session.add(Note(user_id=test_user["id"], binder=binder, title="N1", content="Cellule."))
        db.session.add(Note(user_id=test_user["id"], binder=binder, title="N2", content="Mitose."))
        db.session.commit()
        binder_id = binder.id

    resp = client.post("/api/v1/flashcards/generate", json={
        "source_type": "binder",
        "binder_id": binder_id,
    }, headers=auth_headers)

    assert resp.status_code == 200
    assert resp.json["count"] == 2
    # Le texte agrégé des deux notes a bien été transmis à l'IA
    sent_text = mock_gen.call_args[0][0]
    assert "Cellule." in sent_text and "Mitose." in sent_text


@patch("app.services.ai_service.AIService.generate_flashcards")
def test_generate_empty_note_returns_400(mock_gen, client, auth_headers, test_user, app):
    mock_gen.return_value = AI_CARDS
    with app.app_context():
        note = Note(user_id=test_user["id"], title="Vide", content="")
        db.session.add(note)
        db.session.commit()
        note_id = note.id

    resp = client.post("/api/v1/flashcards/generate", json={
        "source_type": "note",
        "note_id": note_id,
    }, headers=auth_headers)

    assert resp.status_code == 400
    mock_gen.assert_not_called()


@patch("app.services.ai_service.AIService.generate_flashcards")
def test_generate_note_not_found(mock_gen, client, auth_headers, test_user, app):
    mock_gen.return_value = AI_CARDS
    resp = client.post("/api/v1/flashcards/generate", json={
        "source_type": "note",
        "note_id": "does-not-exist",
    }, headers=auth_headers)
    assert resp.status_code == 404


@patch("app.services.ai_service.AIService.generate_flashcards")
def test_generate_other_users_note_forbidden(mock_gen, client, auth_headers, test_user, app):
    mock_gen.return_value = AI_CARDS
    with app.app_context():
        from app.models.user import User
        from werkzeug.security import generate_password_hash
        other = User(email="other@x.io", username="other", password_hash=generate_password_hash("x"))
        db.session.add(other)
        db.session.commit()
        note = Note(user_id=other.id, title="Privée", content="Secret de l'autre utilisateur.")
        db.session.add(note)
        db.session.commit()
        note_id = note.id

    resp = client.post("/api/v1/flashcards/generate", json={
        "source_type": "note",
        "note_id": note_id,
    }, headers=auth_headers)
    assert resp.status_code == 403


@patch("app.services.ai_service.AIService.generate_flashcards")
def test_generate_passes_existing_deck_cards_to_ai(mock_gen, client, auth_headers, test_user, app):
    """Un deck_id ciblé → ses cartes existantes sont transmises à l'IA (anti-doublon)."""
    mock_gen.return_value = AI_CARDS
    with app.app_context():
        note = Note(user_id=test_user["id"], title="Géo", content="La capitale de la France est Paris.")
        deck = Deck(user_id=test_user["id"], name="Géographie")
        db.session.add_all([note, deck])
        db.session.commit()
        db.session.add(Flashcard(deck_id=deck.id, front="Capitale de l'Italie ?", back="Rome"))
        db.session.commit()
        note_id, deck_id = note.id, deck.id

    resp = client.post("/api/v1/flashcards/generate", json={
        "source_type": "note",
        "note_id": note_id,
        "deck_id": deck_id,
    }, headers=auth_headers)

    assert resp.status_code == 200
    existing = mock_gen.call_args.kwargs["existing_cards"]
    assert {"front": "Capitale de l'Italie ?", "back": "Rome"} in existing


@patch("app.services.ai_service.AIService.generate_flashcards")
def test_generate_without_deck_sends_no_existing_cards(mock_gen, client, auth_headers, test_user, app):
    """Nouveau deck (pas de deck_id) → aucune carte existante transmise."""
    mock_gen.return_value = AI_CARDS
    with app.app_context():
        note = Note(user_id=test_user["id"], title="Géo", content="La capitale de la France est Paris.")
        db.session.add(note)
        db.session.commit()
        note_id = note.id

    resp = client.post("/api/v1/flashcards/generate", json={
        "source_type": "note",
        "note_id": note_id,
    }, headers=auth_headers)

    assert resp.status_code == 200
    assert mock_gen.call_args.kwargs["existing_cards"] == []


@patch("app.services.ai_service.AIService.generate_flashcards")
def test_generate_other_users_deck_forbidden(mock_gen, client, auth_headers, test_user, app):
    """Cibler le deck d'un autre utilisateur ne doit pas fuiter ses cartes (403)."""
    mock_gen.return_value = AI_CARDS
    with app.app_context():
        from app.models.user import User
        from werkzeug.security import generate_password_hash
        other = User(email="deckowner@x.io", username="deckowner", password_hash=generate_password_hash("x"))
        db.session.add(other)
        db.session.commit()
        deck = Deck(user_id=other.id, name="Privé")
        note = Note(user_id=test_user["id"], title="Géo", content="La capitale de la France est Paris.")
        db.session.add_all([deck, note])
        db.session.commit()
        note_id, deck_id = note.id, deck.id

    resp = client.post("/api/v1/flashcards/generate", json={
        "source_type": "note",
        "note_id": note_id,
        "deck_id": deck_id,
    }, headers=auth_headers)

    assert resp.status_code == 403
    mock_gen.assert_not_called()


@patch("app.services.ai_service.AIService.generate_flashcards")
def test_generate_passes_coverage_to_ai(mock_gen, client, auth_headers, test_user, app):
    """Le taux de couverture fourni est transmis tel quel à l'IA."""
    mock_gen.return_value = AI_CARDS
    with app.app_context():
        note = Note(user_id=test_user["id"], title="Géo", content="La capitale de la France est Paris.")
        db.session.add(note)
        db.session.commit()
        note_id = note.id

    resp = client.post("/api/v1/flashcards/generate", json={
        "source_type": "note",
        "note_id": note_id,
        "coverage": 40,
    }, headers=auth_headers)

    assert resp.status_code == 200
    assert mock_gen.call_args.kwargs["coverage"] == 40


@patch("app.services.ai_service.AIService.generate_flashcards")
def test_generate_coverage_defaults_to_75(mock_gen, client, auth_headers, test_user, app):
    """Sans coverage explicite, le défaut équilibré (75) est appliqué."""
    mock_gen.return_value = AI_CARDS
    with app.app_context():
        note = Note(user_id=test_user["id"], title="Géo", content="La capitale de la France est Paris.")
        db.session.add(note)
        db.session.commit()
        note_id = note.id

    resp = client.post("/api/v1/flashcards/generate", json={
        "source_type": "note",
        "note_id": note_id,
    }, headers=auth_headers)

    assert resp.status_code == 200
    assert mock_gen.call_args.kwargs["coverage"] == 75


@patch("app.services.ai_service.AIService.generate_flashcards")
def test_generate_invalid_coverage_returns_400(mock_gen, client, auth_headers, test_user, app):
    """Un coverage hors [0,100] ou non entier est rejeté avant tout appel IA."""
    mock_gen.return_value = AI_CARDS
    with app.app_context():
        note = Note(user_id=test_user["id"], title="Géo", content="La capitale de la France est Paris.")
        db.session.add(note)
        db.session.commit()
        note_id = note.id

    for bad in (150, -1, "beaucoup", 50.5):
        resp = client.post("/api/v1/flashcards/generate", json={
            "source_type": "note",
            "note_id": note_id,
            "coverage": bad,
        }, headers=auth_headers)
        assert resp.status_code == 400, f"coverage={bad!r} aurait dû être rejeté"
    mock_gen.assert_not_called()


def test_generate_requires_auth(client):
    resp = client.post("/api/v1/flashcards/generate", json={"source_type": "note", "note_id": "1"})
    assert resp.status_code == 401
