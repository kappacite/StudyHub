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
    
    # 4. Récupérer le dashboard global
    dashboard_resp = client.get("/api/v1/stats/dashboard", headers=auth_headers)
    assert dashboard_resp.status_code == 200
    json_data = dashboard_resp.json
    
    # Vérifier la structure
    assert "kpi" in json_data
    assert "heatmap" in json_data
    assert "maturity_distribution" in json_data
    assert "forecast_7_days" in json_data
    
    # Vérifier les KPI
    assert json_data["kpi"]["total_cards_studied"] == 10
    assert json_data["kpi"]["mature_cards"] == 0
    assert json_data["kpi"]["retention_rate"] == 0.0
    
    # Vérifier la distribution
    assert json_data["maturity_distribution"]["learning"] == 0
    assert json_data["maturity_distribution"]["young"] == 0
    assert json_data["maturity_distribution"]["mature"] == 0
    
    # Vérifier la prévision
    assert len(json_data["forecast_7_days"]) == 7
