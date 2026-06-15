"""Tests du socle de révision (D3c) : ensembles homogènes typés + items SM-2/tuning."""
from datetime import datetime, timedelta

from app.services.spaced_repetition import calculate_sm2


# --- SM-2 tuning (D4) --------------------------------------------------------

def test_sm2_tuning_shortens_and_lengthens_interval():
    # Référence sans tuning (3e révision réussie : interval * ease_factor).
    _, base_interval, _, _ = calculate_sm2(score=5, ease_factor=2.5, interval=10, repetitions=2)
    # tuning < 1 : on révise plus souvent (intervalle plus court).
    _, shorter, _, _ = calculate_sm2(score=5, ease_factor=2.5, interval=10, repetitions=2, tuning=0.5)
    # tuning > 1 : on espace (intervalle plus long).
    _, longer, _, _ = calculate_sm2(score=5, ease_factor=2.5, interval=10, repetitions=2, tuning=2.0)
    assert shorter < base_interval < longer
    # L'intervalle ne descend jamais sous 1 jour.
    _, floored, _, _ = calculate_sm2(score=5, ease_factor=2.5, interval=1, repetitions=0, tuning=0.01)
    assert floored >= 1


# --- Ensembles homogènes typés ----------------------------------------------

def test_create_typed_set_and_item(client, auth_headers):
    rset = client.post("/api/v1/revision/sets", json={
        "name": "QCM Histoire", "type": "qcm",
    }, headers=auth_headers)
    assert rset.status_code == 201
    assert rset.json["type"] == "qcm"
    set_id = rset.json["id"]

    item = client.post(f"/api/v1/revision/sets/{set_id}/items", json={
        "payload": {
            "question": "Quelle est la capitale de la France ?",
            "options": [
                {"id": "a", "text": "Lyon", "correct": False},
                {"id": "b", "text": "Paris", "correct": True},
            ],
            "points": 2,
        }
    }, headers=auth_headers)
    assert item.status_code == 201
    assert item.json["payload"]["points"] == 2

    listed = client.get(f"/api/v1/revision/sets/{set_id}/items", headers=auth_headers)
    assert len(listed.json["data"]) == 1

    detail = client.get(f"/api/v1/revision/sets/{set_id}", headers=auth_headers)
    assert detail.json["item_count"] == 1


def test_qcm_rejects_payload_without_correct_option(client, auth_headers):
    set_id = client.post("/api/v1/revision/sets", json={
        "name": "QCM", "type": "qcm",
    }, headers=auth_headers).json["id"]
    resp = client.post(f"/api/v1/revision/sets/{set_id}/items", json={
        "payload": {
            "question": "Sans bonne réponse ?",
            "options": [
                {"id": "a", "text": "A", "correct": False},
                {"id": "b", "text": "B", "correct": False},
            ],
        }
    }, headers=auth_headers)
    assert resp.status_code == 400


def test_invalid_set_type_rejected(client, auth_headers):
    resp = client.post("/api/v1/revision/sets", json={
        "name": "Bad", "type": "flashcard",  # flashcard n'est PAS un type d'ensemble (D2)
    }, headers=auth_headers)
    assert resp.status_code == 400


def test_definition_set(client, auth_headers):
    set_id = client.post("/api/v1/revision/sets", json={
        "name": "Définitions", "type": "definition",
    }, headers=auth_headers).json["id"]
    ok = client.post(f"/api/v1/revision/sets/{set_id}/items", json={
        "payload": {"term": "Photosynthèse", "definition": "Conversion de lumière en énergie chimique."}
    }, headers=auth_headers)
    assert ok.status_code == 201
    bad = client.post(f"/api/v1/revision/sets/{set_id}/items", json={
        "payload": {"term": "Sans définition"}
    }, headers=auth_headers)
    assert bad.status_code == 400


def test_study_and_answer_updates_sm2_and_session(client, auth_headers, app):
    set_id = client.post("/api/v1/revision/sets", json={
        "name": "VF", "type": "vf",
    }, headers=auth_headers).json["id"]
    item = client.post(f"/api/v1/revision/sets/{set_id}/items", json={
        "payload": {"assertion": "La Terre est plate.", "correct": False}
    }, headers=auth_headers).json

    # L'item neuf est dû immédiatement.
    study = client.get(f"/api/v1/revision/sets/{set_id}/study", headers=auth_headers)
    assert study.status_code == 200
    assert any(i["id"] == item["id"] for i in study.json)

    answered = client.post(
        f"/api/v1/revision/sets/{set_id}/study/answer/{item['id']}",
        json={"score": 5}, headers=auth_headers,
    )
    assert answered.status_code == 200
    assert answered.json["repetitions"] == 1
    assert answered.json["interval"] >= 1

    # Une StudySession unifiée a été enregistrée (item_id + item_type).
    with app.app_context():
        from app.models.study_session import StudySession
        sess = StudySession.query.filter_by(item_id=item["id"], item_type="vf").first()
        assert sess is not None
        assert sess.grade == 5


def test_set_isolation_between_users(client, auth_headers, app):
    set_id = client.post("/api/v1/revision/sets", json={
        "name": "Privé", "type": "qcm",
    }, headers=auth_headers).json["id"]

    # Second utilisateur.
    client.post("/api/v1/auth/register", json={
        "email": "other@example.com", "username": "other", "password": "password123",
    })
    other = client.post("/api/v1/auth/login", json={
        "email": "other@example.com", "password": "password123",
    }).json["access_token"]
    other_headers = {"Authorization": f"Bearer {other}"}

    resp = client.get(f"/api/v1/revision/sets/{set_id}", headers=other_headers)
    assert resp.status_code in (403, 404)


# --- Migration de réconciliation PR #48 (D3c) --------------------------------

def test_reconcile_pr48_moves_typed_cards_to_revision_sets(app):
    """La migration de réconciliation déplace les cartes typées d'un deck vers un
    RevisionSet homogène et restaure le deck en flashcards `basic`. Idempotente."""
    from app.extensions import db
    from app.models.user import User
    from app.models.deck import Deck
    from app.models.flashcard import Flashcard
    from app.models.revision import RevisionSet, RevisionItem
    from migrations.versions.b2c3d4e5f6a7_reconcile_pr48_typed_cards import reconcile

    with app.app_context():
        user = User(email="recon@example.com", username="recon")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        deck = Deck(name="Mixte", user_id=user.id)
        db.session.add(deck)
        db.session.commit()

        basic = Flashcard(deck_id=deck.id, front="Capitale ?", back="Paris", card_type="basic")
        qcm = Flashcard(
            deck_id=deck.id, front="Q ?", back="B",
            card_type="qcm",
            payload={"question": "Q ?", "options": [
                {"id": "a", "text": "A", "correct": False},
                {"id": "b", "text": "B", "correct": True},
            ]},
        )
        db.session.add_all([basic, qcm])
        db.session.commit()

        # Exécute la réconciliation sur la connexion courante.
        reconcile(db.session.connection())
        db.session.expire_all()

        # Le deck ne garde que la carte basic.
        remaining = Flashcard.query.filter_by(deck_id=deck.id).all()
        assert len(remaining) == 1
        assert remaining[0].card_type == "basic"

        # Un ensemble QCM homogène a été créé avec l'item migré.
        rset = RevisionSet.query.filter_by(user_id=user.id, type="qcm").first()
        assert rset is not None
        items = RevisionItem.query.filter_by(set_id=rset.id).all()
        assert len(items) == 1
        assert items[0].payload["options"][1]["correct"] is True

        # Idempotence : une seconde exécution ne crée pas de doublon.
        reconcile(db.session.connection())
        db.session.expire_all()
        assert RevisionSet.query.filter_by(user_id=user.id, type="qcm").count() == 1
        assert RevisionItem.query.filter_by(set_id=rset.id).count() == 1
