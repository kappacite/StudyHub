"""Task 1 (revision-flexibilite) — scission check_item_answer / grade_item : le
client voit la correction (check, sans effet de bord) puis choisit sa note SM-2
(grade, `score` desormais fourni explicitement, plus jamais deduit)."""

import pytest

from app.extensions import db
from app.models.revision import RevisionItem
from app.models.study_session import StudySession


def _set(client, auth_headers, type_):
    return client.post(
        "/api/v1/revision/sets", json={"name": type_, "type": type_}, headers=auth_headers
    ).json["id"]


def _item(client, auth_headers, set_id, payload):
    return client.post(
        f"/api/v1/revision/sets/{set_id}/items", json={"payload": payload}, headers=auth_headers
    ).json


def _check(client, auth_headers, set_id, item_id, answer):
    return client.post(
        f"/api/v1/revision/sets/{set_id}/study/check/{item_id}",
        json={"answer": answer},
        headers=auth_headers,
    )


def _grade(client, auth_headers, set_id, item_id, answer, score, duration_seconds=0):
    return client.post(
        f"/api/v1/revision/sets/{set_id}/study/grade/{item_id}",
        json={"answer": answer, "score": score, "duration_seconds": duration_seconds},
        headers=auth_headers,
    )


GRADABLE_CASES = [
    (
        "vf",
        {"assertion": "La Terre est plate.", "correct": False},
        {"value": False},
        {"value": True},
    ),
    (
        "association",
        {"pairs": [{"left": "France", "right": "Paris"}, {"left": "Italie", "right": "Rome"}]},
        {"matches": {"France": "Paris", "Italie": "Rome"}},
        {"matches": {"France": "Rome", "Italie": "Paris"}},
    ),
    (
        "ordre",
        {"steps": ["A", "B", "C"]},
        {"order": ["A", "B", "C"]},
        {"order": ["A", "C", "B"]},
    ),
]


@pytest.mark.parametrize("type_, payload, correct_answer, wrong_answer", GRADABLE_CASES)
def test_check_item_answer_reports_correctness_without_side_effects(
    client, auth_headers, app, type_, payload, correct_answer, wrong_answer
):
    set_id = _set(client, auth_headers, type_)
    item = _item(client, auth_headers, set_id, payload)

    with app.app_context():
        before = db.session.get(RevisionItem, item["id"])
        before_state = (
            before.ease_factor,
            before.interval,
            before.repetitions,
            before.next_review,
        )

    ok = _check(client, auth_headers, set_id, item["id"], correct_answer)
    assert ok.status_code == 200
    assert ok.json == {"correct": True}

    ko = _check(client, auth_headers, set_id, item["id"], wrong_answer)
    assert ko.status_code == 200
    assert ko.json == {"correct": False}

    with app.app_context():
        after = db.session.get(RevisionItem, item["id"])
        after_state = (
            after.ease_factor,
            after.interval,
            after.repetitions,
            after.next_review,
        )
        assert after_state == before_state, "check_item_answer ne doit pas toucher SM-2"
        assert StudySession.query.filter_by(item_id=item["id"]).count() == 0


def test_check_item_answer_rejects_non_gradable_type(client, auth_headers):
    """Même garde que l'existant (GRADABLE_TYPES) : definition/qcm/flashcard
    ne sont pas corrigés côté serveur."""
    set_id = _set(client, auth_headers, "definition")
    item = _item(client, auth_headers, set_id, {"term": "X", "definition": "Y"})

    resp = _check(client, auth_headers, set_id, item["id"], {"value": True})
    assert resp.status_code == 400


def test_grade_item_without_score_is_rejected(client, auth_headers):
    """Le point de la scission : le client DOIT fournir la note choisie."""
    set_id = _set(client, auth_headers, "vf")
    item = _item(client, auth_headers, set_id, {"assertion": "Le ciel est bleu.", "correct": True})

    resp = client.post(
        f"/api/v1/revision/sets/{set_id}/study/grade/{item['id']}",
        json={"answer": {"value": True}},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_grade_item_uses_provided_score_even_when_answer_is_wrong(client, auth_headers, app):
    """faux + score=3 -> SM-2 calculé avec score=3 (réussite), jamais avec le
    score=2 que l'ancien code aurait déduit d'une réponse fausse."""
    set_id = _set(client, auth_headers, "vf")
    item = _item(client, auth_headers, set_id, {"assertion": "Le ciel est bleu.", "correct": True})

    resp = _grade(client, auth_headers, set_id, item["id"], {"value": False}, score=3)
    assert resp.status_code == 200
    assert resp.json["correct"] is False  # correction réelle : la réponse est fausse
    assert resp.json["item"]["repetitions"] == 1  # score=3 >= 3 -> SM-2 "réussite"

    with app.app_context():
        sess = StudySession.query.filter_by(item_id=item["id"]).first()
        assert sess.grade == 3
        assert sess.cards_correct == 0  # basé sur la correction réelle, pas le score


def test_grade_item_cards_correct_independent_of_low_score_on_right_answer(
    client, auth_headers, app
):
    """Réponse juste mais note basse (score=1) : `correct`/`cards_correct`
    restent vrais (correction réelle), SM-2 traite quand même l'item en échec."""
    set_id = _set(client, auth_headers, "vf")
    item = _item(client, auth_headers, set_id, {"assertion": "Le ciel est bleu.", "correct": True})

    resp = _grade(client, auth_headers, set_id, item["id"], {"value": True}, score=1)
    assert resp.status_code == 200
    assert resp.json["correct"] is True
    assert resp.json["item"]["repetitions"] == 0  # score=1 < 3 -> SM-2 "échec"

    with app.app_context():
        sess = StudySession.query.filter_by(item_id=item["id"]).first()
        assert sess.grade == 1
        assert sess.cards_correct == 1  # basé sur la correction réelle, pas le score


def test_grade_item_rejects_score_out_of_range(client, auth_headers):
    set_id = _set(client, auth_headers, "vf")
    item = _item(client, auth_headers, set_id, {"assertion": "Le ciel est bleu.", "correct": True})

    resp = _grade(client, auth_headers, set_id, item["id"], {"value": True}, score=6)
    assert resp.status_code == 400
