"""notes-ia-planning-corrections, Task 1 : advance_review_set, equivalent de
advance_review pour un RevisionSet (get_calendar deja couvert par test_planning.py)."""

from datetime import datetime, timedelta

import pytest
from app.extensions import db
from app.models.revision import RevisionSet, RevisionItem
from app.dao.flashcard_dao import FlashcardDAO
from app.dao.deck_dao import DeckDAO
from app.dao.revision_dao import RevisionItemDAO, RevisionSetDAO
from app.services.planning_service import PlanningService
from app.middlewares.error_handler import ForbiddenError, ResourceNotFoundError


@pytest.fixture
def planning_service():
    return PlanningService(
        FlashcardDAO(db.session), DeckDAO(db.session),
        RevisionItemDAO(db.session), RevisionSetDAO(db.session),
    )


def test_advance_review_set_forbidden_for_other_user(app, planning_service, test_user):
    with app.app_context():
        from app.models.user import User
        other = User(email="other-advance@example.com", username="other_advance")
        other.set_password("password123")
        db.session.add(other)
        db.session.commit()

        rset = RevisionSet(name="PasAMoi", user_id=other.id)
        db.session.add(rset)
        db.session.commit()
        item = RevisionItem(
            set_id=rset.id, type="vf", payload={"assertion": "A", "correct": True},
            next_review=datetime.utcnow(),
        )
        db.session.add(item)
        db.session.commit()

        with pytest.raises(ForbiddenError):
            planning_service.advance_review_set(test_user["id"], rset.id, [item.id])


def test_advance_review_set_returns_items_without_modifying_them(app, planning_service, test_user):
    with app.app_context():
        rset = RevisionSet(name="Anatomie", user_id=test_user["id"])
        db.session.add(rset)
        db.session.commit()

        orig_next_review = datetime.utcnow() + timedelta(days=4)
        item = RevisionItem(
            set_id=rset.id, type="vf", payload={"assertion": "A", "correct": True},
            next_review=orig_next_review,
        )
        db.session.add(item)
        db.session.commit()

        items = planning_service.advance_review_set(test_user["id"], rset.id, [item.id])

        assert len(items) == 1
        assert items[0].id == item.id
        db.session.refresh(item)
        assert item.next_review == orig_next_review


def test_advance_review_set_unknown_set_raises_not_found(app, planning_service, test_user):
    with app.app_context():
        with pytest.raises(ResourceNotFoundError):
            planning_service.advance_review_set(test_user["id"], 999999, [1])
