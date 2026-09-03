"""notes-ia-planning-corrections, Task 12."""

from app.schemas.note_grade_schema import NoteGradeResponse


def test_note_grade_response_serializes_from_model_attributes():
    class FakeGrade:
        score = 82
        verdict = "Note solide."
        points_forts = ["A"]
        ameliorations = ["B"]
        suggestions = "Suggestion"
        updated_at = None

    resp = NoteGradeResponse.model_validate(FakeGrade())
    assert resp.score == 82
    assert resp.points_forts == ["A"]
