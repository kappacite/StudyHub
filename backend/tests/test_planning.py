import pytest
from datetime import datetime, timedelta, date
from app.extensions import db
from app.models.deck import Deck
from app.models.flashcard import Flashcard
from app.services.planning_service import PlanningService
from app.dao.flashcard_dao import FlashcardDAO
from app.dao.deck_dao import DeckDAO
from app.middlewares.error_handler import ForbiddenError, ResourceNotFoundError

@pytest.fixture
def planning_service():
    flashcard_dao = FlashcardDAO(db.session)
    deck_dao = DeckDAO(db.session)
    return PlanningService(flashcard_dao, deck_dao)

def test_calendar_returns_correct_counts(app, planning_service, test_user):
    with app.app_context():
        # Create deck
        deck = Deck(name="Astrobiologie", description="", user_id=test_user["id"])
        db.session.add(deck)
        db.session.commit()

        today = datetime.utcnow().date()

        # Card 1: Late (should go to today's count)
        card1 = Flashcard(
            deck_id=deck.id,
            front="Q1",
            back="A1",
            next_review=datetime.utcnow() - timedelta(days=3)
        )
        # Card 2: Due today
        card2 = Flashcard(
            deck_id=deck.id,
            front="Q2",
            back="A2",
            next_review=datetime.utcnow()
        )
        # Card 3: Due tomorrow
        card3 = Flashcard(
            deck_id=deck.id,
            front="Q3",
            back="A3",
            next_review=datetime.utcnow() + timedelta(days=1)
        )
        db.session.add_all([card1, card2, card3])
        db.session.commit()

        # Call get_calendar
        date_from = today
        date_to = today + timedelta(days=2)
        result = planning_service.get_calendar(test_user["id"], date_from, date_to)

        # Verify
        days = result["days"]
        assert len(days) == 3

        # Today: card1 (late) + card2 (due today) = 2
        assert days[0]["date"] == today.isoformat()
        assert days[0]["total_due"] == 2
        assert days[0]["breakdown"][0]["deck_id"] == deck.id
        assert days[0]["breakdown"][0]["count"] == 2

        # Tomorrow: card3 (due tomorrow) = 1
        assert days[1]["date"] == (today + timedelta(days=1)).isoformat()
        assert days[1]["total_due"] == 1

        # Day 3: 0
        assert days[2]["date"] == (today + timedelta(days=2)).isoformat()
        assert days[2]["total_due"] == 0

def test_calendar_empty_range_returns_empty_days(app, planning_service, test_user):
    with app.app_context():
        today = datetime.utcnow().date()
        date_from = today
        date_to = today + timedelta(days=5)

        result = planning_service.get_calendar(test_user["id"], date_from, date_to)

        assert len(result["days"]) == 6
        for day in result["days"]:
            assert day["total_due"] == 0
            assert len(day["breakdown"]) == 0

def test_advance_review_forbidden_for_other_user_card(app, planning_service, test_user):
    with app.app_context():
        # Create second user manually
        from app.models.user import User
        user2 = User(email="test2@example.com", username="testuser2")
        user2.set_password("password123")
        db.session.add(user2)
        db.session.commit()

        # Create deck belonging to user 2
        deck = Deck(name="Calculus", description="", user_id=user2.id)
        db.session.add(deck)
        db.session.commit()

        card = Flashcard(
            deck_id=deck.id,
            front="Limits",
            back="Limit value",
            next_review=datetime.utcnow()
        )
        db.session.add(card)
        db.session.commit()

        # User 1 attempts to review user 2's deck
        with pytest.raises(ForbiddenError):
            planning_service.advance_review(test_user["id"], deck.id, [card.id])

def test_advance_review_returns_cards_without_modifying_them(app, planning_service, test_user):
    with app.app_context():
        deck = Deck(name="Anatomie", description="", user_id=test_user["id"])
        db.session.add(deck)
        db.session.commit()

        orig_next_review = datetime.utcnow() + timedelta(days=4)
        card = Flashcard(
            deck_id=deck.id,
            front="Muscle",
            back="Squelettique",
            next_review=orig_next_review
        )
        db.session.add(card)
        db.session.commit()

        # Call advance_review
        cards = planning_service.advance_review(test_user["id"], deck.id, [card.id])

        assert len(cards) == 1
        assert cards[0].id == card.id
        
        # Verify db state has not changed
        db.session.refresh(card)
        assert card.next_review == orig_next_review

# Integration Endpoints tests
def test_get_planning_calendar_endpoint(client, auth_headers, app, test_user):
    with app.app_context():
        deck = Deck(name="Chimie", description="", user_id=test_user["id"])
        db.session.add(deck)
        db.session.commit()
        
        card = Flashcard(
            deck_id=deck.id,
            front="H2O",
            back="Eau",
            next_review=datetime.utcnow()
        )
        db.session.add(card)
        db.session.commit()

    today_str = datetime.utcnow().date().isoformat()
    to_str = (datetime.utcnow().date() + timedelta(days=1)).isoformat()

    response = client.get(
        f"/api/v1/planning/calendar?from={today_str}&to={to_str}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "days" in data
    assert len(data["days"]) == 2
    assert data["days"][0]["total_due"] == 1

def test_post_planning_advance_endpoint(client, auth_headers, app, test_user):
    with app.app_context():
        deck = Deck(name="Bio", description="", user_id=test_user["id"])
        db.session.add(deck)
        db.session.commit()
        
        card = Flashcard(
            deck_id=deck.id,
            front="Cellule",
            back="Noyau",
            next_review=datetime.utcnow() + timedelta(days=2)
        )
        db.session.add(card)
        db.session.commit()
        card_id = card.id
        deck_id = deck.id

    response = client.post(
        "/api/v1/planning/advance",
        json={
            "deck_id": deck_id,
            "card_ids": [card_id]
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["id"] == card_id
    assert data[0]["front"] == "Cellule"
