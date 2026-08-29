"""Tests A2 — QCM scoré (D6) : points par question, multi tout-ou-rien, passage SM-2."""


def _qcm_set(client, auth_headers):
    return client.post(
        "/api/v1/revision/sets", json={"name": "QCM", "type": "qcm"}, headers=auth_headers
    ).json["id"]


def _add_item(client, auth_headers, set_id, payload):
    return client.post(
        f"/api/v1/revision/sets/{set_id}/items", json={"payload": payload}, headers=auth_headers
    ).json


def test_run_weighted_score_single_and_multi(client, auth_headers):
    set_id = _qcm_set(client, auth_headers)
    # Q1 : réponse unique, 1 point.
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

    run = client.post(
        f"/api/v1/revision/sets/{set_id}/run",
        json={
            "answers": [
                {"item_id": q1["id"], "selected_option_ids": ["b"]},  # correct → 1
                {"item_id": q2["id"], "selected_option_ids": ["a", "c"]},  # correct (multi) → 3
            ]
        },
        headers=auth_headers,
    )
    assert run.status_code == 200
    assert run.json["score"] == 4
    assert run.json["max_score"] == 4
    assert run.json["percentage"] == 100.0


def test_run_multi_all_or_nothing(client, auth_headers):
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
    run = client.post(
        f"/api/v1/revision/sets/{set_id}/run",
        json={
            "answers": [
                {"item_id": q["id"], "selected_option_ids": ["a"]},
            ]
        },
        headers=auth_headers,
    )
    assert run.json["score"] == 0
    assert run.json["max_score"] == 2
    assert run.json["results"][0]["correct"] is False
    assert run.json["results"][0]["correct_option_ids"] == ["a", "c"]


def test_run_updates_sm2_and_sessions(client, auth_headers, app):
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
    client.post(
        f"/api/v1/revision/sets/{set_id}/run",
        json={
            "answers": [
                {"item_id": q["id"], "selected_option_ids": ["b"]},
            ]
        },
        headers=auth_headers,
    )

    # SM-2 mis à jour (1re réussite → interval 1, repetitions 1).
    items = client.get(f"/api/v1/revision/sets/{set_id}/items", headers=auth_headers).json["data"]
    assert items[0]["repetitions"] == 1
    with app.app_context():
        from app.models.study_session import StudySession

        sess = StudySession.query.filter_by(item_id=q["id"], item_type="qcm").first()
        assert sess is not None and sess.grade == 5


def test_run_records_item_type_from_item_not_from_set(client, auth_headers, app):
    """Revue de branche reviser-hub, finding #7 : run_qcm ecrivait item_type=rset.type
    sur la StudySession au lieu de item_type=item.type (pattern deja correct dans
    answer_item/grade_item). Sans effet observable aujourd'hui puisque run_qcm exige
    un ensemble homogene QCM (item.type == rset.type == "qcm" a la creation), mais
    silencieusement faux si un item finit par porter un type different -- l'agregation
    des stats groupe par item.type et manquerait alors cette session. On force ce cas
    limite en mutant item.type directement en base apres creation."""
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
        from app.extensions import db
        from app.models.revision import RevisionItem

        item = db.session.get(RevisionItem, q["id"])
        item.type = "flashcard"
        db.session.commit()

    client.post(
        f"/api/v1/revision/sets/{set_id}/run",
        json={"answers": [{"item_id": q["id"], "selected_option_ids": ["b"]}]},
        headers=auth_headers,
    )

    with app.app_context():
        from app.models.study_session import StudySession

        sess = StudySession.query.filter_by(item_id=q["id"]).first()
        assert sess is not None
        assert sess.item_type == "flashcard"


def test_run_rejects_non_qcm_set(client, auth_headers):
    set_id = client.post(
        "/api/v1/revision/sets", json={"name": "VF", "type": "vf"}, headers=auth_headers
    ).json["id"]
    resp = client.post(
        f"/api/v1/revision/sets/{set_id}/run", json={"answers": []}, headers=auth_headers
    )
    assert resp.status_code == 400


# --- Duree de revision reelle, split par divmod (Task 9, reviser-hub-redesign) --


def test_run_splits_duration_across_batch_via_divmod(client, auth_headers, app):
    """100s sur 3 questions -> divmod(100, 3) = (33, 1) : la premiere question
    (reste 1) recoit 34, les 2 suivantes 33 -- la somme retombe exactement sur
    100, aucune precision fabriquee."""
    set_id = _qcm_set(client, auth_headers)
    q1 = _add_item(
        client,
        auth_headers,
        set_id,
        {
            "question": "Q1",
            "options": [
                {"id": "a", "text": "A", "correct": True},
                {"id": "b", "text": "B", "correct": False},
            ],
        },
    )
    q2 = _add_item(
        client,
        auth_headers,
        set_id,
        {
            "question": "Q2",
            "options": [
                {"id": "a", "text": "A", "correct": True},
                {"id": "b", "text": "B", "correct": False},
            ],
        },
    )
    q3 = _add_item(
        client,
        auth_headers,
        set_id,
        {
            "question": "Q3",
            "options": [
                {"id": "a", "text": "A", "correct": True},
                {"id": "b", "text": "B", "correct": False},
            ],
        },
    )

    client.post(
        f"/api/v1/revision/sets/{set_id}/run",
        json={
            "duration_seconds": 100,
            "answers": [
                {"item_id": q1["id"], "selected_option_ids": ["a"]},
                {"item_id": q2["id"], "selected_option_ids": ["a"]},
                {"item_id": q3["id"], "selected_option_ids": ["a"]},
            ],
        },
        headers=auth_headers,
    )

    with app.app_context():
        from app.models.study_session import StudySession

        sessions = (
            StudySession.query.filter(StudySession.item_id.in_([q1["id"], q2["id"], q3["id"]]))
            .order_by(StudySession.item_id)
            .all()
        )
        durations = [s.duration_seconds for s in sessions]
        assert sum(durations) == 100
        assert durations == [34, 33, 33]


def test_run_omitted_duration_defaults_all_rows_to_zero(client, auth_headers, app):
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
    client.post(
        f"/api/v1/revision/sets/{set_id}/run",
        json={
            "answers": [{"item_id": q["id"], "selected_option_ids": ["a"]}],
        },
        headers=auth_headers,
    )

    with app.app_context():
        from app.models.study_session import StudySession

        sess = StudySession.query.filter_by(item_id=q["id"]).first()
        assert sess.duration_seconds == 0


def test_run_explicit_zero_duration_with_multiple_answers_no_division_error(
    client, auth_headers, app
):
    """duration_seconds=0 explicite avec plusieurs reponses : lignes toutes a
    zero, pas d'erreur de division (cf. brief Task 9 -- cas limite a ne pas
    laisser planter)."""
    set_id = _qcm_set(client, auth_headers)
    q1 = _add_item(
        client,
        auth_headers,
        set_id,
        {
            "question": "Q1",
            "options": [
                {"id": "a", "text": "A", "correct": True},
                {"id": "b", "text": "B", "correct": False},
            ],
        },
    )
    q2 = _add_item(
        client,
        auth_headers,
        set_id,
        {
            "question": "Q2",
            "options": [
                {"id": "a", "text": "A", "correct": True},
                {"id": "b", "text": "B", "correct": False},
            ],
        },
    )

    resp = client.post(
        f"/api/v1/revision/sets/{set_id}/run",
        json={
            "duration_seconds": 0,
            "answers": [
                {"item_id": q1["id"], "selected_option_ids": ["a"]},
                {"item_id": q2["id"], "selected_option_ids": ["a"]},
            ],
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200

    with app.app_context():
        from app.models.study_session import StudySession

        sessions = StudySession.query.filter(StudySession.item_id.in_([q1["id"], q2["id"]])).all()
        assert all(s.duration_seconds == 0 for s in sessions)
