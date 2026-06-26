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
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.5-flash")
    
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

def test_generate_evaluation_missing_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    service = AIService()
    with pytest.raises(RuntimeError) as excinfo:
        service.generate_evaluation("Contenu du cours")
    assert "La clé d'API Gemini n'est pas configurée" in str(excinfo.value)


@patch("urllib.request.urlopen")
def test_generate_evaluation_success_mixed_items(mock_urlopen, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.5-flash")

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps({
                                "items": [
                                    {
                                        "type": "qcm",
                                        "question": "Quelle est la capitale de la France ?",
                                        "options": [
                                            {"id": "a", "text": "Lyon", "correct": False},
                                            {"id": "b", "text": "Paris", "correct": True},
                                            {"id": "c", "text": "Nice", "correct": False},
                                            {"id": "d", "text": "Lille", "correct": False},
                                        ],
                                    },
                                    {"type": "vf", "assertion": "L'eau bout à 100°C.", "correct": True, "justification": "Au niveau de la mer."},
                                    {"type": "trou", "text_with_blank": "La mitochondrie est le siège de la [...].", "answer": "respiration cellulaire"},
                                    {"type": "open", "question": "Expliquez la photosynthèse.", "model_answer": "Conversion de lumière en énergie chimique.", "key_points": ["lumière", "chlorophylle", "glucose"]},
                                ]
                            })
                        }
                    ]
                }
            }
        ]
    }).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_response

    service = AIService()
    result = service.generate_evaluation("Contenu de la note", item_count=4)

    assert isinstance(result, dict)
    items = result["items"]
    assert len(items) == 4
    types = [it["type"] for it in items]
    assert types == ["qcm", "vf", "trou", "open"]
    # La clé de correction est bien embarquée (un seul appel)
    assert any(opt["correct"] for opt in items[0]["options"])
    assert items[1]["correct"] is True
    assert items[2]["answer"] == "respiration cellulaire"
    assert items[3]["key_points"]


@patch("urllib.request.urlopen")
def test_generate_evaluation_invalid_shape_raises(mock_urlopen, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")

    mock_response = MagicMock()
    # Gemini renvoie un tableau au lieu d'un objet {items: [...]}
    mock_response.read.return_value = json.dumps({
        "candidates": [{"content": {"parts": [{"text": json.dumps([{"type": "qcm"}])}]}}]
    }).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_response

    service = AIService()
    with pytest.raises(RuntimeError):
        service.generate_evaluation("Contenu")


def test_analyze_feynman_missing_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    service = AIService()
    with pytest.raises(RuntimeError) as excinfo:
        service.analyze_feynman("Titre", "Contenu", "Explication simple")
    assert "La clé d'API Gemini n'est pas configurée" in str(excinfo.value)


@patch("urllib.request.urlopen")
def test_analyze_feynman_success(mock_urlopen, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.5-flash")

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "candidates": [{"content": {"parts": [{"text": json.dumps({
            "clarity_score": 78,
            "jargon": ["mitochondrie"],
            "gaps": [{"concept": "ATP", "issue": "rôle énergétique non expliqué"}],
            "feedback": "Bonne analogie, mais un terme reste opaque.",
            "suggestion": "Compare la mitochondrie à une centrale électrique."
        })}]}}]
    }).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_response

    service = AIService()
    result = service.analyze_feynman("La cellule", "Contenu du cours", "Mon explication")

    assert result["clarity_score"] == 78
    assert result["jargon"] == ["mitochondrie"]
    assert result["gaps"][0]["concept"] == "ATP"
    assert "analogie" in result["feedback"]
    assert result["suggestion"]


@patch("app.services.ai_service.AIService.analyze_feynman")
def test_feynman_analyze_endpoint(mock_analyze_feynman, client, auth_headers, test_user, app):
    mock_analyze_feynman.return_value = {
        "clarity_score": 88,
        "jargon": [],
        "gaps": [],
        "feedback": "Très clair.",
        "suggestion": "Continuez ainsi.",
    }

    with app.app_context():
        from app.extensions import db
        binder = Binder(user_id=test_user["id"], name="Classeur Feynman")
        db.session.add(binder)
        db.session.commit()
        note = Note(user_id=test_user["id"], binder_id=binder.id, title="Note F", content="Contenu")
        db.session.add(note)
        db.session.commit()
        note_id = note.id

    resp = client.post("/api/v1/feynman/analyze", json={
        "note_id": note_id,
        "user_explanation": "Mon explication simple",
        "duration_seconds": 90,
    }, headers=auth_headers)

    assert resp.status_code == 202
    assert "task_id" in resp.json
    task_id = resp.json["task_id"]

    poll = client.get(f"/api/v1/feynman/tasks/{task_id}", headers=auth_headers)
    assert poll.status_code == 200
    assert poll.json["status"] == "SUCCESS"
    assert poll.json["result"]["clarity_score"] == 88
    assert poll.json["result"]["feedback"] == "Très clair."


def test_feynman_analyze_requires_fields(client, auth_headers):
    resp = client.post("/api/v1/feynman/analyze", json={"note_id": None}, headers=auth_headers)
    assert resp.status_code == 400


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
    
    assert resp.status_code == 202
    assert "task_id" in resp.json
    task_id = resp.json["task_id"]
    
    # Polling de l'état de la tâche
    poll_resp = client.get(f"/api/v1/blurting/tasks/{task_id}", headers=auth_headers)
    assert poll_resp.status_code == 200
    assert poll_resp.json["status"] == "SUCCESS"
    assert poll_resp.json["result"]["retention_score"] == 90
    assert poll_resp.json["result"]["general_feedback"] == "Excellent."

