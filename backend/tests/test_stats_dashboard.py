from datetime import datetime, timedelta
from app.extensions import db
from app.models.study_session import StudySession

def test_dashboard_stats(client, auth_headers, app):
    # 1. Enregistrer une session d'étude de flashcards
    resp = client.post("/api/v1/stats/sessions", json={
        "module": "flashcard",
        "duration_seconds": 600,
        "cards_reviewed": 10,
        "cards_correct": 8
    }, headers=auth_headers)
    assert resp.status_code == 201
    
    # Enregistrer une autre session pour un autre module
    resp2 = client.post("/api/v1/stats/sessions", json={
        "module": "note",
        "duration_seconds": 900
    }, headers=auth_headers)
    assert resp2.status_code == 201
    
    # 2. Récupérer l'overview
    overview_resp = client.get("/api/v1/stats/overview", headers=auth_headers)
    assert overview_resp.status_code == 200
    assert overview_resp.json["total_time_seconds"] == 1500
    assert overview_resp.json["total_reviewed"] == 10
    assert overview_resp.json["total_correct"] == 8
    assert overview_resp.json["streak"] == 1  # Étudié aujourd'hui
    
    # 3. Récupérer la heatmap
    heatmap_resp = client.get("/api/v1/stats/heatmap", headers=auth_headers)
    assert heatmap_resp.status_code == 200
    assert len(heatmap_resp.json) >= 1
    # Trouver l'entrée d'aujourd'hui
    today_str = datetime.utcnow().date().isoformat()
    today_entry = next((item for item in heatmap_resp.json if item["date"] == today_str), None)
    assert today_entry is not None
    assert today_entry["duration"] == 1500
    assert today_entry["count"] == 2
