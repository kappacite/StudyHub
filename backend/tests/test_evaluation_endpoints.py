from unittest.mock import patch, MagicMock

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
def test_complete_proposes_cards_and_optin_adds_to_deck(mock_gen, client, auth_headers):
    mock_gen.return_value = AI_RESULT
    note_id = _create_note(client, auth_headers)

    gen = client.post(
        "/api/v1/evaluations/generate",
        json={"note_id": note_id, "item_count": 4},
        headers=auth_headers,
    )
    result = client.get(
        f"/api/v1/evaluations/tasks/{gen.json['task_id']}", headers=auth_headers
    ).json["result"]
    eval_id = result["id"]
    qcm = next(i for i in result["items"] if i["type"] == "qcm" and i["source"] == "ai")

    # Rater le QCM volontairement (mauvaise option)
    client.post(
        f"/api/v1/evaluations/{eval_id}/items/{qcm['id']}/answer",
        json={"value": "a"},
        headers=auth_headers,
    )

    # Complétion : des cartes sont PROPOSÉES (pas créées).
    done = client.post(f"/api/v1/evaluations/{eval_id}/complete", headers=auth_headers)
    assert done.status_code == 200
    proposals = done.json["proposed_cards"]
    assert any(c["front"] == "Capitale de la France ?" for c in proposals)
    proposed_item_id = next(c["item_id"] for c in proposals if c["front"] == "Capitale de la France ?")

    # L'élève choisit un deck réel et y ajoute la carte (opt-in).
    deck = client.post("/api/v1/decks", json={"name": "Mes lacunes"}, headers=auth_headers)
    deck_id = deck.json["id"]
    add = client.post(
        f"/api/v1/evaluations/{eval_id}/flashcards",
        json={"deck_id": deck_id, "item_ids": [proposed_item_id]},
        headers=auth_headers,
    )
    assert add.status_code == 201
    assert add.json["created"] == 1

    cards = client.get(f"/api/v1/decks/{deck_id}/cards", headers=auth_headers)
    fronts = [c["front"] for c in cards.json["data"]]
    assert "Capitale de la France ?" in fronts


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


def test_task_status_uses_celery_app_bound_asyncresult(client, auth_headers):
    """Régression : get_task_status doit utiliser celery_app.AsyncResult (lié au
    result-backend Redis), et non l'AsyncResult nu de celery.result. Ce dernier se
    rattache au current_app *thread-local* — dans un thread worker gunicorn c'est le
    Celery par défaut (DisabledBackend), d'où un 500 sur le polling."""
    fake = MagicMock()
    fake.status = "PENDING"
    fake.ready.return_value = False

    with patch("app.extensions.celery_app.AsyncResult", return_value=fake) as mock_ar:
        resp = client.get("/api/v1/evaluations/tasks/some-task-id", headers=auth_headers)

    assert resp.status_code == 200
    assert resp.json["status"] == "PENDING"
    # Si on régresse vers l'AsyncResult nu, ce mock ne serait jamais appelé.
    mock_ar.assert_called_once_with("some-task-id")


@patch("app.tasks.run_evaluation_generation.delay", side_effect=RuntimeError("broker down"))
@patch("app.services.ai_service.AIService.generate_evaluation")
def test_generate_falls_back_to_sync_when_broker_down(mock_gen, mock_delay, client, auth_headers):
    """Broker Redis injoignable -> exécution inline -> 200 + résultat direct,
    sans task_id (le frontend court-circuite alors le polling)."""
    mock_gen.return_value = AI_RESULT
    note_id = _create_note(client, auth_headers)

    resp = client.post(
        "/api/v1/evaluations/generate",
        json={"note_id": note_id, "item_count": 4},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json["status"] == "SUCCESS"
    assert "task_id" not in resp.json
    result = resp.json["result"]
    assert len(result["items"]) == 4
    # La vue question reste sanitisée même en repli synchrone.
    qcm = next(i for i in result["items"] if i["type"] == "qcm" and i["source"] == "ai")
    for opt in qcm["payload"]["options"]:
        assert "correct" not in opt
