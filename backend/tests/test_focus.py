import pytest
from datetime import datetime, timedelta
from app.extensions import db
from app.models.deck import Deck
from app.models.flashcard import Flashcard
from app.models.note import Note
from app.models.binder import Binder
from app.models.study_session import StudySession
from app.services.focus_service import FocusService

@pytest.fixture
def focus_service():
    return FocusService()

def test_today_items_returns_only_due_cards(app, focus_service, test_user):
    with app.app_context():
        # Create deck and flashcards
        deck = Deck(name="Optique", description="", user_id=test_user["id"])
        db.session.add(deck)
        db.session.commit()

        # Card 1: Due
        card1 = Flashcard(
            deck_id=deck.id,
            front="Loi de la réflexion",
            back="i1 = i'1",
            next_review=datetime.utcnow() - timedelta(minutes=10)
        )
        # Card 2: Not due
        card2 = Flashcard(
            deck_id=deck.id,
            front="Loi de la réfraction",
            back="n1 sin i1 = n2 sin i2",
            next_review=datetime.utcnow() + timedelta(days=1)
        )
        db.session.add_all([card1, card2])
        db.session.commit()

        # Call get_today_items
        result = focus_service.get_today_items(test_user["id"])
        
        # Verify
        assert result.flashcard_count == 1
        assert len(result.items) == 1
        assert result.items[0].id == deck.id
        assert result.items[0].type == "deck"
        assert result.items[0].count == 1

def test_today_items_marks_late_correctly(app, focus_service, test_user):
    with app.app_context():
        deck = Deck(name="Biochimie", description="", user_id=test_user["id"])
        db.session.add(deck)
        db.session.commit()

        # Card 1: Late (next_review < today - 1 day)
        card1 = Flashcard(
            deck_id=deck.id,
            front="Front 1",
            back="Back 1",
            next_review=datetime.utcnow() - timedelta(days=2)
        )
        # Card 2: Due but not late
        card2 = Flashcard(
            deck_id=deck.id,
            front="Front 2",
            back="Back 2",
            next_review=datetime.utcnow() - timedelta(minutes=10)
        )
        db.session.add_all([card1, card2])
        db.session.commit()

        result = focus_service.get_today_items(test_user["id"])
        
        assert result.flashcard_count == 2
        assert result.late_count == 1  # 1 deck item has a late card, and count of late card is 1
        assert result.items[0].is_late is True

def test_forecast_counts_correct_for_known_deck(app, focus_service, test_user):
    with app.app_context():
        deck = Deck(name="Chimie", description="", user_id=test_user["id"])
        db.session.add(deck)
        db.session.commit()

        # 3 cards due tomorrow
        tomorrow = datetime.utcnow() + timedelta(days=1)
        for i in range(3):
            c = Flashcard(deck_id=deck.id, front=f"Q{i}", back=f"A{i}", next_review=tomorrow)
            db.session.add(c)
        
        # 1 card due in 3 days
        three_days = datetime.utcnow() + timedelta(days=3)
        c2 = Flashcard(deck_id=deck.id, front="Q4", back="A4", next_review=three_days)
        db.session.add(c2)
        db.session.commit()

        result = focus_service.get_forecast(test_user["id"], days=7)
        
        forecast_map = {item.date: item.count for item in result.forecast}
        tomorrow_str = tomorrow.date().isoformat()
        three_days_str = three_days.date().isoformat()
        
        assert forecast_map[tomorrow_str] == 3
        assert forecast_map[three_days_str] == 1
        assert result.forecast[1].load_level == "low"  # count < 10

def test_retention_calculation_30_days(app, focus_service, test_user):
    with app.app_context():
        binder = Binder(name="Physique", user_id=test_user["id"])
        db.session.add(binder)
        db.session.commit()

        deck = Deck(name="Optique", binder_id=binder.id, user_id=test_user["id"])
        db.session.add(deck)
        db.session.commit()

        card = Flashcard(deck_id=deck.id, front="Q", back="A", next_review=datetime.utcnow())
        db.session.add(card)
        db.session.commit()

        # Create study sessions in the last 30 days
        # Session 1: correct
        s1 = StudySession(
            user_id=test_user["id"],
            module="flashcard",
            duration_seconds=30,
            cards_reviewed=1,
            cards_correct=1,
            flashcard_id=card.id,
            grade=4,
            created_at=datetime.utcnow() - timedelta(days=5)
        )
        # Session 2: incorrect
        s2 = StudySession(
            user_id=test_user["id"],
            module="flashcard",
            duration_seconds=30,
            cards_reviewed=1,
            cards_correct=0,
            flashcard_id=card.id,
            grade=1,
            created_at=datetime.utcnow() - timedelta(days=10)
        )
        db.session.add_all([s1, s2])
        db.session.commit()

        result = focus_service.get_retention_by_subject(test_user["id"])
        
        assert len(result.by_subject) == 1
        subject = result.by_subject[0]
        assert subject.binder_id == binder.id
        assert subject.retention_pct == 50.0  # 1/2 * 100

def test_retention_trend_positive_negative(app, focus_service, test_user):
    with app.app_context():
        binder = Binder(name="Math", user_id=test_user["id"])
        db.session.add(binder)
        db.session.commit()

        deck = Deck(name="Algèbre", binder_id=binder.id, user_id=test_user["id"])
        db.session.add(deck)
        db.session.commit()

        card = Flashcard(deck_id=deck.id, front="Q", back="A")
        db.session.add(card)
        db.session.commit()

        # Session in Period A (last 7 days): 100% correct
        s_a = StudySession(
            user_id=test_user["id"],
            module="flashcard",
            cards_reviewed=1,
            cards_correct=1,
            flashcard_id=card.id,
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        # Session in Period B (7-14 days ago): 0% correct
        s_b = StudySession(
            user_id=test_user["id"],
            module="flashcard",
            cards_reviewed=1,
            cards_correct=0,
            flashcard_id=card.id,
            created_at=datetime.utcnow() - timedelta(days=10)
        )
        db.session.add_all([s_a, s_b])
        db.session.commit()

        result = focus_service.get_retention_by_subject(test_user["id"])
        
        assert len(result.by_subject) == 1
        subject = result.by_subject[0]
        # trend_7d = rate_a (100.0) - rate_b (0.0) = 100.0
        assert subject.trend_7d == 100.0

def test_focus_endpoints_require_auth(client):
    response = client.get("/api/v1/focus/today")
    assert response.status_code == 401

def test_user_isolation_focus_data(app, client, auth_headers, test_user):
    # Other user data
    with app.app_context():
        from app.models.user import User
        other_user = User(email="other-focus@example.com", username="otherfocus")
        other_user.set_password("password123")
        db.session.add(other_user)
        db.session.commit()

        deck = Deck(name="Other Deck", description="", user_id=other_user.id)
        db.session.add(deck)
        db.session.commit()

        card = Flashcard(
            deck_id=deck.id,
            front="Other Q",
            back="Other A",
            next_review=datetime.utcnow() - timedelta(minutes=10)
        )
        db.session.add(card)
        db.session.commit()

    # Get focus today as test_user (auth_headers)
    response = client.get("/api/v1/focus/today", headers=auth_headers)
    
    assert response.status_code == 200
    # Should be empty since test_user has no decks/cards
    assert response.json["total_due"] == 0
    assert len(response.json["items"]) == 0
