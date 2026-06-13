from datetime import datetime, timedelta

from app.extensions import db
from app.models.deck import Deck
from app.models.flashcard import Flashcard


def _make_card(app, user_id, *, ease_factor, interval, repetitions, days_until_due):
    with app.app_context():
        deck = Deck(user_id=user_id, name="Deck Planning")
        db.session.add(deck)
        db.session.commit()
        card = Flashcard(
            deck_id=deck.id,
            front="Q",
            back="A",
            ease_factor=ease_factor,
            interval=interval,
            repetitions=repetitions,
            next_review=datetime.utcnow() + timedelta(days=days_until_due),
        )
        db.session.add(card)
        db.session.commit()
        return card.id


def test_advance_review_applies_sm2_from_today(client, auth_headers, test_user, app):
    # Carte due dans 10 jours, révisée en avance. 1ère réussite -> interval 1.
    card_id = _make_card(app, test_user["id"], ease_factor=2.5, interval=0,
                         repetitions=0, days_until_due=10)
    before = datetime.utcnow()

    resp = client.patch(f"/api/v1/flashcards/{card_id}/review",
                        json={"score": 5}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json["interval"] == 1
    assert resp.json["repetitions"] == 1

    # next_review repart d'aujourd'hui (~ +1j), pas de l'ancienne échéance (+10j).
    with app.app_context():
        card = db.session.get(Flashcard, card_id)
        assert card.next_review < before + timedelta(days=3)


def test_sm2_interval_not_inflated_by_advance(client, auth_headers, test_user, app):
    # Carte mûre (reps=2, interval=10, ef=2.0) due dans 30j, révisée en avance.
    card_id = _make_card(app, test_user["id"], ease_factor=2.0, interval=10,
                         repetitions=2, days_until_due=30)

    resp = client.patch(f"/api/v1/flashcards/{card_id}/review",
                        json={"score": 5}, headers=auth_headers)
    assert resp.status_code == 200
    # SM-2 : ef -> 2.1, interval = round(10 * 2.1) = 21 — PAS gonflé par les 30j d'avance.
    assert resp.json["interval"] == 21

    with app.app_context():
        card = db.session.get(Flashcard, card_id)
        assert card.next_review < datetime.utcnow() + timedelta(days=23)
