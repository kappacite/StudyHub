"""Tests A2 — QCM scoré (D6) : points par question, multi tout-ou-rien, passage SM-2."""


def _qcm_set(client, auth_headers):
    return client.post("/api/v1/revision/sets", json={"name": "QCM", "type": "qcm"}, headers=auth_headers).json["id"]


def _add_item(client, auth_headers, set_id, payload):
    return client.post(f"/api/v1/revision/sets/{set_id}/items", json={"payload": payload}, headers=auth_headers).json


def test_run_weighted_score_single_and_multi(client, auth_headers):
    set_id = _qcm_set(client, auth_headers)
    # Q1 : réponse unique, 1 point.
    q1 = _add_item(client, auth_headers, set_id, {
        "question": "Capitale de la France ?",
        "options": [
            {"id": "a", "text": "Lyon", "correct": False},
            {"id": "b", "text": "Paris", "correct": True},
        ],
    })
    # Q2 : réponses multiples, 3 points.
    q2 = _add_item(client, auth_headers, set_id, {
        "question": "Nombres pairs ?",
        "points": 3,
        "options": [
            {"id": "a", "text": "2", "correct": True},
            {"id": "b", "text": "3", "correct": False},
            {"id": "c", "text": "4", "correct": True},
        ],
    })

    run = client.post(f"/api/v1/revision/sets/{set_id}/run", json={"answers": [
        {"item_id": q1["id"], "selected_option_ids": ["b"]},          # correct → 1
        {"item_id": q2["id"], "selected_option_ids": ["a", "c"]},      # correct (multi) → 3
    ]}, headers=auth_headers)
    assert run.status_code == 200
    assert run.json["score"] == 4
    assert run.json["max_score"] == 4
    assert run.json["percentage"] == 100.0


def test_run_multi_all_or_nothing(client, auth_headers):
    set_id = _qcm_set(client, auth_headers)
    q = _add_item(client, auth_headers, set_id, {
        "question": "Nombres pairs ?",
        "points": 2,
        "options": [
            {"id": "a", "text": "2", "correct": True},
            {"id": "b", "text": "3", "correct": False},
            {"id": "c", "text": "4", "correct": True},
        ],
    })
    # Sélection partielle (manque "c") → tout-ou-rien : 0 point.
    run = client.post(f"/api/v1/revision/sets/{set_id}/run", json={"answers": [
        {"item_id": q["id"], "selected_option_ids": ["a"]},
    ]}, headers=auth_headers)
    assert run.json["score"] == 0
    assert run.json["max_score"] == 2
    assert run.json["results"][0]["correct"] is False
    assert run.json["results"][0]["correct_option_ids"] == ["a", "c"]


def test_run_updates_sm2_and_sessions(client, auth_headers, app):
    set_id = _qcm_set(client, auth_headers)
    q = _add_item(client, auth_headers, set_id, {
        "question": "2+2 ?",
        "options": [
            {"id": "a", "text": "3", "correct": False},
            {"id": "b", "text": "4", "correct": True},
        ],
    })
    client.post(f"/api/v1/revision/sets/{set_id}/run", json={"answers": [
        {"item_id": q["id"], "selected_option_ids": ["b"]},
    ]}, headers=auth_headers)

    # SM-2 mis à jour (1re réussite → interval 1, repetitions 1).
    items = client.get(f"/api/v1/revision/sets/{set_id}/items", headers=auth_headers).json["data"]
    assert items[0]["repetitions"] == 1
    with app.app_context():
        from app.models.study_session import StudySession
        sess = StudySession.query.filter_by(item_id=q["id"], item_type="qcm").first()
        assert sess is not None and sess.grade == 5


def test_run_rejects_non_qcm_set(client, auth_headers):
    set_id = client.post("/api/v1/revision/sets", json={"name": "VF", "type": "vf"}, headers=auth_headers).json["id"]
    resp = client.post(f"/api/v1/revision/sets/{set_id}/run", json={"answers": []}, headers=auth_headers)
    assert resp.status_code == 400
