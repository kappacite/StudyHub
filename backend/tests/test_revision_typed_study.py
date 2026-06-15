"""Tests A3–A6 — correction & SM-2 à l'étude des types vf / association / ordre."""


def _set(client, auth_headers, type_):
    return client.post("/api/v1/revision/sets", json={"name": type_, "type": type_}, headers=auth_headers).json["id"]


def _item(client, auth_headers, set_id, payload):
    return client.post(f"/api/v1/revision/sets/{set_id}/items", json={"payload": payload}, headers=auth_headers).json


def _grade(client, auth_headers, set_id, item_id, answer):
    return client.post(f"/api/v1/revision/sets/{set_id}/study/grade/{item_id}", json={"answer": answer}, headers=auth_headers)


def test_vf_verdict_correction(client, auth_headers):
    set_id = _set(client, auth_headers, "vf")
    item = _item(client, auth_headers, set_id, {"assertion": "La Terre est plate.", "correct": False})

    ok = _grade(client, auth_headers, set_id, item["id"], {"value": False})
    assert ok.status_code == 200
    assert ok.json["correct"] is True
    assert ok.json["item"]["repetitions"] == 1  # SM-2 mis à jour (réussite)

    ko = _grade(client, auth_headers, set_id, item["id"], {"value": True})
    assert ko.json["correct"] is False


def test_association_order_independent_and_partial(client, auth_headers):
    set_id = _set(client, auth_headers, "association")
    item = _item(client, auth_headers, set_id, {
        "title": "Pays/capitales",
        "pairs": [{"left": "France", "right": "Paris"}, {"left": "Italie", "right": "Rome"}],
    })

    # Ordre indifférent : appariement complet correct → vrai.
    ok = _grade(client, auth_headers, set_id, item["id"], {"matches": {"Italie": "Rome", "France": "Paris"}})
    assert ok.json["correct"] is True

    # Appariement partiel → faux.
    partial = _grade(client, auth_headers, set_id, item["id"], {"matches": {"France": "Paris"}})
    assert partial.json["correct"] is False

    # Appariement erroné → faux.
    wrong = _grade(client, auth_headers, set_id, item["id"], {"matches": {"France": "Rome", "Italie": "Paris"}})
    assert wrong.json["correct"] is False


def test_ordre_strict_correction(client, auth_headers):
    set_id = _set(client, auth_headers, "ordre")
    item = _item(client, auth_headers, set_id, {"title": "Cycle", "steps": ["A", "B", "C"]})

    assert _grade(client, auth_headers, set_id, item["id"], {"order": ["A", "B", "C"]}).json["correct"] is True
    assert _grade(client, auth_headers, set_id, item["id"], {"order": ["A", "C", "B"]}).json["correct"] is False


def test_grade_rejects_definition_type(client, auth_headers):
    set_id = _set(client, auth_headers, "definition")
    item = _item(client, auth_headers, set_id, {"term": "X", "definition": "Y"})
    resp = _grade(client, auth_headers, set_id, item["id"], {"value": True})
    assert resp.status_code == 400


def test_definition_self_eval_via_answer(client, auth_headers):
    # La définition reste en auto-évaluation : on passe par l'endpoint answer générique.
    set_id = _set(client, auth_headers, "definition")
    item = _item(client, auth_headers, set_id, {"term": "Photosynthèse", "definition": "..."})
    ans = client.post(f"/api/v1/revision/sets/{set_id}/study/answer/{item['id']}", json={"score": 5}, headers=auth_headers)
    assert ans.status_code == 200
    assert ans.json["repetitions"] == 1
