import json
from unittest.mock import patch, MagicMock
import pytest
from app.services.ai_service import AIService
from app.models.binder import Binder
from app.models.note import Note

def test_ai_service_missing_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    service = AIService()
    with pytest.raises(RuntimeError) as excinfo:
        service.analyze_blurting("Titre", "Contenu", "Restitution")
    assert "La clé d'API Gemini n'est pas configurée" in str(excinfo.value)

@patch("urllib.request.urlopen")
def test_ai_service_success(mock_urlopen, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
    monkeypatch.setenv("GEMINI_MODEL", "gemma-4-31b")
    
    # Simuler la réponse de l'API Gemini
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps({
                                "retention_score": 85,
                                "concepts": [
                                    {"name": "Concept 1", "status": "mastered", "explanation": "Bravo"}
                                ],
                                "suggested_flashcards": [
                                    {"front": "Question 1", "back": "Reponse 1"}
                                ],
                                "general_feedback": "Bon travail global."
                            })
                        }
                    ]
                }
            }
        ]
    }).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_response

    service = AIService()
    result = service.analyze_blurting("Titre de la note", "Contenu de la note", "Restitution de l'etudiant")
    
    assert result["retention_score"] == 85
    assert len(result["concepts"]) == 1
    assert result["concepts"][0]["name"] == "Concept 1"
    assert len(result["suggested_flashcards"]) == 1
    assert result["suggested_flashcards"][0]["front"] == "Question 1"
    assert result["general_feedback"] == "Bon travail global."

@patch("app.services.ai_service.AIService.analyze_blurting")
def test_blurting_analyze_endpoint(mock_analyze_blurting, client, auth_headers, test_user, app):
    # Mocking du service IA
    mock_analyze_blurting.return_value = {
        "retention_score": 90,
        "concepts": [],
        "suggested_flashcards": [],
        "general_feedback": "Excellent."
    }
    
    with app.app_context():
        # Création d'un classeur et d'une note associés à l'utilisateur de test
        from app.extensions import db
        
        binder = Binder(user_id=test_user["id"], name="Classeur Test")
        db.session.add(binder)
        db.session.commit()
        
        note = Note(user_id=test_user["id"], binder_id=binder.id, title="Note Test", content="Contenu de la note")
        db.session.add(note)
        db.session.commit()
        
        note_id = note.id

    # Appel de l'API d'analyse
    resp = client.post("/api/v1/blurting/analyze", json={
        "note_id": note_id,
        "user_blurting": "Restitution de test",
        "duration_seconds": 120
    }, headers=auth_headers)
    
    assert resp.status_code == 200
    assert resp.json["retention_score"] == 90
    assert resp.json["general_feedback"] == "Excellent."
