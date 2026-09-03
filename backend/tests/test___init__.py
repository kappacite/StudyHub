"""notes-ia-planning-corrections, Task 1 : app/schemas/__init__.py re-exportait encore
DeckBreakdownSchema (renomme BreakdownItemSchema), cassant l'import de tout le module
schemas au demarrage de l'app. Test de non-regression minimal sur le barrel export."""

from app.schemas import BreakdownItemSchema, PlanningDaySchema, PlanningCalendarResponse, PlanningAdvanceRequest


def test_planning_schemas_exported_from_barrel():
    assert BreakdownItemSchema is not None
    assert PlanningDaySchema is not None
    assert PlanningCalendarResponse is not None
    assert PlanningAdvanceRequest is not None


# notes-ia-planning-corrections, Task 12 : NoteGrade ajoute a app/models/__init__.py.
def test_breakdown_item_schema_in_all():
    import app.schemas as schemas_module
    assert "BreakdownItemSchema" in schemas_module.__all__
