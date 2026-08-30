"""Tests A2 — QCM par question (D6, Task 2 revision-flexibilite) : correction
sans effet de bord (check) puis validation avec la note SM-2 choisie par
l'utilisateur (answer) -- meme principe que check_item_answer/grade_item
(Task 1) applique au QCM, question par question (plus de passage groupe)."""

from app.extensions import db
from app.models.revision import RevisionItem
from app.models.study_session import StudySession


def _qcm_set(client, auth_headers):
    return client.post(
        "/api/v1/revision/sets", json={"name": "QCM", "type": "qcm"}, headers=auth_headers
    ).json["id"]


def _add_item(client, auth_headers, set_id, payload):
    return client.post(
        f"/api/v1/revision/sets/{set_id}/items", json={"payload": payload}, headers=auth_headers
    ).json


def _check(client, auth_headers, set_id, item_id, selected_option_ids):
    return client.post(
        f"/api/v1/revision/sets/{set_id}/study/qcm-check/{item_id}",
        json={"selected_option_ids": selected_option_ids},
        headers=auth_headers,
    )


def _answer(client, auth_headers, set_id, item_id, selected_option_ids, score, duration_seconds=0):
    return client.post(
        f"/api/v1/revision/sets/{set_id}/study/qcm-answer/{item_id}",
        json={
            "selected_option_ids": selected_option_ids,
            "score": score,
            "duration_seconds": duration_seconds,
        },
        headers=auth_headers,
    )


def test_check_weighted_score_single_and_multi(client, auth_headers):
    set_id = _qcm_set(client, auth_headers)
    # Q1 : réponse unique, 1 point (par défaut).
    q1 = _add_item(
        client,
        auth_headers,
        set_id,
        {
            "question": "Capitale de la France ?",
            "options": [
                {"id": "a", "text": "Lyon", "correct": False},
                {"id": "b", "text": "Paris", "correct": True},
            ],
        },
    )
    # Q2 : réponses multiples, 3 points.
    q2 = _add_item(
        client,
        auth_headers,
        set_id,
        {
            "question": "Nombres pairs ?",
            "points": 3,
            "options": [
                {"id": "a", "text": "2", "correct": True},
                {"id": "b", "text": "3", "correct": False},
                {"id": "c", "text": "4", "correct": True},
            ],
        },
    )

    r1 = _check(client, auth_headers, set_id, q1["id"], ["b"])
    assert r1.status_code == 200
    assert r1.json["correct"] is True
    assert r1.json["earned"] == 1
    assert r1.json["points"] == 1

    r2 = _check(client, auth_headers, set_id, q2["id"], ["a", "c"])
    assert r2.status_code == 200
    assert r2.json["correct"] is True
    assert r2.json["earned"] == 3
    assert r2.json["points"] == 3
    assert r2.json["correct_option_ids"] == ["a", "c"]


def test_check_multi_all_or_nothing(client, auth_headers):
    set_id = _qcm_set(client, auth_headers)
    q = _add_item(
        client,
        auth_headers,
        set_id,
        {
            "question": "Nombres pairs ?",
            "points": 2,
            "options": [
                {"id": "a", "text": "2", "correct": True},
                {"id": "b", "text": "3", "correct": False},
                {"id": "c", "text": "4", "correct": True},
            ],
        },
    )
    # Sélection partielle (manque "c") → tout-ou-rien : 0 point.
    resp = _check(client, auth_headers, set_id, q["id"], ["a"])
    assert resp.status_code == 200
    assert resp.json["correct"] is False
    assert resp.json["earned"] == 0
    assert resp.json["points"] == 2
    assert resp.json["correct_option_ids"] == ["a", "c"]


def test_check_qcm_answer_has_no_side_effect(client, auth_headers, app):
    """check_qcm_answer est une lecture seule : ni StudySession, ni changement
    SM-2 (ease_factor/interval/repetitions/next_review), peu importe la
    correction du résultat."""
    set_id = _qcm_set(client, auth_headers)
    q = _add_item(
        client,
        auth_headers,
        set_id,
        {
            "question": "2+2 ?",
            "options": [
                {"id": "a", "text": "3", "correct": False},
                {"id": "b", "text": "4", "correct": True},
            ],
        },
    )

    with app.app_context():
        before = db.session.get(RevisionItem, q["id"])
        before_state = (
            before.ease_factor,
            before.interval,
            before.repetitions,
            before.next_review,
        )

    _check(client, auth_headers, set_id, q["id"], ["b"])
    _check(client, auth_headers, set_id, q["id"], ["a"])

    with app.app_context():
        after = db.session.get(RevisionItem, q["id"])
        after_state = (
            after.ease_factor,
            after.interval,
            after.repetitions,
            after.next_review,
        )
        assert after_state == before_state, "check_qcm_answer ne doit pas toucher SM-2"
        assert StudySession.query.filter_by(item_id=q["id"]).count() == 0


def test_answer_qcm_item_applies_provided_score_to_sm2(client, auth_headers, app):
    """answer_qcm_item applique le score fourni par le client (pas un binaire
    5/1 déduit de la correction, cf. ancien run_qcm)."""
    set_id = _qcm_set(client, auth_headers)
    q = _add_item(
        client,
        auth_headers,
        set_id,
        {
            "question": "2+2 ?",
            "options": [
                {"id": "a", "text": "3", "correct": False},
                {"id": "b", "text": "4", "correct": True},
            ],
        },
    )

    # Réponse juste mais note basse (score=2) : SM-2 traite quand même l'item
    # en échec (score < 3), alors que l'ancien code aurait forcé grade=5.
    resp = _answer(client, auth_headers, set_id, q["id"], ["b"], score=2)
    assert resp.status_code == 200
    assert resp.json["correct"] is True
    assert resp.json["item"]["repetitions"] == 0  # score=2 < 3 -> SM-2 "échec"

    with app.app_context():
        sess = StudySession.query.filter_by(item_id=q["id"], item_type="qcm").first()
        assert sess is not None
        assert sess.grade == 2
        assert sess.cards_correct == 1  # basé sur la correction réelle, pas le score


def test_check_qcm_answer_rejects_item_type_mismatch(client, auth_headers, app):
    """Revue finale de branche (defaut Important #2) : un item dont le type
    n'est PAS "qcm", insere dans un ensemble QCM, doit faire lever une
    ValidationError (400) a qcm-check -- pas un correct=True fabrique par
    _score_qcm_answer retombant silencieusement sur des options vides."""
    set_id = _qcm_set(client, auth_headers)
    q = _add_item(
        client,
        auth_headers,
        set_id,
        {
            "question": "2+2 ?",
            "options": [
                {"id": "a", "text": "3", "correct": False},
                {"id": "b", "text": "4", "correct": True},
            ],
        },
    )
    with app.app_context():
        item = db.session.get(RevisionItem, q["id"])
        item.type = "flashcard"
        db.session.commit()

    resp = _check(client, auth_headers, set_id, q["id"], [])
    assert resp.status_code == 400


def test_answer_qcm_item_rejects_item_type_mismatch(client, auth_headers, app):
    """Meme defaut que ci-dessus, cote qcm-answer (Important #2, revue finale
    de branche) : sans la garde sur item.type, une selection vide serait
    comptee correct=True a tort (correct_ids == [] == selected_ids) et
    appliquerait une note SM-2 sur une donnee fabriquee."""
    set_id = _qcm_set(client, auth_headers)
    q = _add_item(
        client,
        auth_headers,
        set_id,
        {
            "question": "2+2 ?",
            "options": [
                {"id": "a", "text": "3", "correct": False},
                {"id": "b", "text": "4", "correct": True},
            ],
        },
    )
    with app.app_context():
        item = db.session.get(RevisionItem, q["id"])
        item.type = "flashcard"
        db.session.commit()

    resp = _answer(client, auth_headers, set_id, q["id"], [], score=5)
    assert resp.status_code == 400

    with app.app_context():
        assert StudySession.query.filter_by(item_id=q["id"]).count() == 0


def test_answer_qcm_item_uses_its_own_duration(client, auth_headers, app):
    """Chaque question a sa propre durée réelle mesurée côté frontend (plus de
    répartition divmod d'une durée de lot, cf. ancien run_qcm/Task 9)."""
    set_id = _qcm_set(client, auth_headers)
    q = _add_item(
        client,
        auth_headers,
        set_id,
        {
            "question": "Q",
            "options": [
                {"id": "a", "text": "A", "correct": True},
                {"id": "b", "text": "B", "correct": False},
            ],
        },
    )

    resp = _answer(client, auth_headers, set_id, q["id"], ["a"], score=5, duration_seconds=42)
    assert resp.status_code == 200

    with app.app_context():
        sess = StudySession.query.filter_by(item_id=q["id"]).first()
        assert sess.duration_seconds == 42


def test_check_and_answer_reject_non_qcm_set(client, auth_headers):
    set_id = client.post(
        "/api/v1/revision/sets", json={"name": "VF", "type": "vf"}, headers=auth_headers
    ).json["id"]
    item = client.post(
        f"/api/v1/revision/sets/{set_id}/items",
        json={"payload": {"assertion": "Vrai ?", "correct": True}},
        headers=auth_headers,
    ).json

    check_resp = _check(client, auth_headers, set_id, item["id"], [])
    assert check_resp.status_code == 400

    answer_resp = _answer(client, auth_headers, set_id, item["id"], [], score=5)
    assert answer_resp.status_code == 400


def test_answer_qcm_item_requires_score(client, auth_headers):
    set_id = _qcm_set(client, auth_headers)
    q = _add_item(
        client,
        auth_headers,
        set_id,
        {
            "question": "Q",
            "options": [
                {"id": "a", "text": "A", "correct": True},
                {"id": "b", "text": "B", "correct": False},
            ],
        },
    )
    resp = client.post(
        f"/api/v1/revision/sets/{set_id}/study/qcm-answer/{q['id']}",
        json={"selected_option_ids": ["a"]},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def _share_qcm_set_with_new_user(client, owner_headers):
    """Reproduit le cas légitime « cours partagé » (SM-2 partagé) : un élève
    répond sur le même item QCM que le propriétaire sans toucher son
    échéancier -- même pattern que test_shared_revision_sets.py."""
    binder_id = client.post(
        "/api/v1/binders", json={"name": "Cours QCM partagé"}, headers=owner_headers
    ).json["id"]
    set_id = client.post(
        "/api/v1/revision/sets",
        json={"name": "QCM", "type": "qcm", "binder_id": binder_id},
        headers=owner_headers,
    ).json["id"]
    item = _add_item(
        client,
        owner_headers,
        set_id,
        {
            "question": "2+2 ?",
            "options": [
                {"id": "a", "text": "3", "correct": False},
                {"id": "b", "text": "4", "correct": True},
            ],
        },
    )

    group_resp = client.post("/api/v1/groups", json={"name": "Groupe QCM"}, headers=owner_headers)
    group_id = group_resp.json["id"]
    invite_code = group_resp.json["invite_code"]
    client.post(
        f"/api/v1/groups/{group_id}/binders",
        json={"binder_id": binder_id, "permission": "read"},
        headers=owner_headers,
    )

    client.post(
        "/api/v1/auth/register",
        json={
            "email": "student_qcm@example.com",
            "username": "student_qcm",
            "password": "password123",
        },
    )
    student_token = client.post(
        "/api/v1/auth/login",
        json={"email": "student_qcm@example.com", "password": "password123"},
    ).json["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}
    client.post("/api/v1/groups/join", json={"invite_code": invite_code}, headers=student_headers)

    return set_id, item, student_headers


def test_answer_qcm_item_student_on_shared_set_does_not_update_sm2(client, auth_headers, app):
    """Un élève sur un ensemble QCM partagé (« cours ») : sa StudySession est
    enregistrée, mais l'échéancier SM-2 du propriétaire reste inchangé."""
    set_id, item, student_headers = _share_qcm_set_with_new_user(client, auth_headers)

    with app.app_context():
        before = db.session.get(RevisionItem, item["id"])
        before_state = (before.ease_factor, before.interval, before.repetitions, before.next_review)

    resp = _answer(client, student_headers, set_id, item["id"], ["b"], score=5)
    assert resp.status_code == 200

    with app.app_context():
        after = db.session.get(RevisionItem, item["id"])
        after_state = (after.ease_factor, after.interval, after.repetitions, after.next_review)
        assert after_state == before_state, "l'élève ne doit pas modifier l'échéancier du prof"
        sess = StudySession.query.filter_by(item_id=item["id"]).first()
        assert sess is not None and sess.grade == 5
