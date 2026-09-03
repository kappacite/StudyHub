"""notes-ia-planning-corrections, Task 1 : BreakdownItemSchema generalise
DeckBreakdownSchema pour couvrir aussi les RevisionSet (kind discriminant)."""

import pytest
from pydantic import ValidationError

from app.schemas.planning_schema import BreakdownItemSchema, PlanningAdvanceRequest


def test_breakdown_item_accepts_deck_kind():
    item = BreakdownItemSchema(kind="deck", id=1, name="Bio", count=3)
    assert item.kind == "deck"


def test_breakdown_item_accepts_revision_set_kind():
    item = BreakdownItemSchema(kind="revision_set", id=2, name="Chimie", count=5)
    assert item.kind == "revision_set"


def test_breakdown_item_rejects_unknown_kind():
    with pytest.raises(ValidationError):
        BreakdownItemSchema(kind="deck_wrong", id=1, name="X", count=1)


def test_advance_request_accepts_either_deck_or_set_id():
    assert PlanningAdvanceRequest(deck_id=1).deck_id == 1
    assert PlanningAdvanceRequest(set_id=2).set_id == 2
