from unittest.mock import patch

NOTE_CONTENT = (
    "Cours d'introduction.\n"
    "{{vf::La Terre est plate::Faux::La Terre est sphérique.}}\n"
    "[ADN]{def:Acide désoxyribonucléique}"
)

AI_RESULT = {
    "items": [
        {
            "type": "qcm",
            "question": "Capitale de la France ?",
            "options": [
                {"id": "a", "text": "Lyon", "correct": False},
                {"id": "b", "text": "Paris", "correct": True},
                {"id": "c", "text": "Nice", "correct": False},
                {"id": "d", "text": "Lille", "correct": False},
            ],
        },
        {"type": "open", "question": "Expliquez X.", "model_answer": "...", "key_points": ["a"]},
    ]
}


def _create_note(client, auth_headers):
    resp = client.post(
        "/api/v1/notes",
        json={"title": "Cours", "content": NOTE_CONTENT},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json["id"]


@patch("app.services.ai_service.AIService.generate_evaluation")
def test_generate_poll_answer_complete_flow(mock_gen, client, auth_headers):
    mock_gen.return_value = AI_RESULT
    note_id = _create_note(client, auth_headers)

    # 1. Génération asynchrone -> 202 + task_id
    resp = client.post("/api/v1/evaluations/generate", json={"note_id": note_id, "item_count": 4}, headers=auth_headers)
    assert resp.status_code == 202
    task_id = resp.json["task_id"]

    # 2. Polling -> SUCCESS + résultat (vue question sanitisée)
    poll = client.get(f"/api/v1/evaluations/tasks/{task_id}", headers=auth_headers)
    assert poll.status_code == 200
    assert poll.json["status"] == "SUCCESS"
    result = poll.json["result"]
    eval_id = result["id"]
    # 2 items IA + 2 items balises (vf + def->open)
    assert len(result["items"]) == 4
    qcm = next(i for i in result["items"] if i["type"] == "qcm" and i["source"] == "ai")
    for opt in qcm["payload"]["options"]:
        assert "correct" not in opt  # pas de fuite de correction

    # 3. Répondre au QCM (bonne réponse 'b')
    ans = client.post(
        f"/api/v1/evaluations/{eval_id}/items/{qcm['id']}/answer",
        json={"value": "b"},
        headers=auth_headers,
    )
    assert ans.status_code == 200
    assert ans.json["is_correct"] is True
    assert ans.json["correction"]["correct_option_id"] == "b"

    # 4. Compléter -> score + corrections révélées
    done = client.post(f"/api/v1/evaluations/{eval_id}/complete", headers=auth_headers)
    assert done.status_code == 200
    assert done.json["completed_at"] is not None
    assert done.json["score_pct"] is not None


@patch("app.services.ai_service.AIService.generate_evaluation")
def test_generate_forbidden_for_other_user_note(mock_gen, client, auth_headers, app):
    mock_gen.return_value = AI_RESULT
    note_id = _create_note(client, auth_headers)

    # Second utilisateur
    client.post("/api/v1/auth/register", json={
        "email": "intrus@example.com", "username": "intrus", "password": "password123"
    })
    login = client.post("/api/v1/auth/login", json={"email": "intrus@example.com", "password": "password123"})
    other_headers = {"Authorization": f"Bearer {login.json['access_token']}"}

    resp = client.post("/api/v1/evaluations/generate", json={"note_id": note_id}, headers=other_headers)
    assert resp.status_code == 403


def test_generate_requires_auth(client):
    resp = client.post("/api/v1/evaluations/generate", json={"note_id": "x"})
    assert resp.status_code == 401
