"""Tests A8 — statistiques agrégées par classeur (ensembles de révision)."""


def _binder(client, headers, name, parent_id=None):
    payload = {"name": name}
    if parent_id:
        payload["parent_id"] = parent_id
    return client.post("/api/v1/binders", json=payload, headers=headers).json["id"]


def _qcm_set(client, headers, binder_id, name="QCM"):
    set_id = client.post("/api/v1/revision/sets", json={
        "name": name, "type": "qcm", "binder_id": binder_id,
    }, headers=headers).json["id"]
    item = client.post(f"/api/v1/revision/sets/{set_id}/items", json={"payload": {
        "question": "2+2 ?",
        "options": [{"id": "a", "text": "3", "correct": False},
                    {"id": "b", "text": "4", "correct": True}],
    }}, headers=headers).json
    return set_id, item


def test_binder_stats_aggregates_multiple_sets_and_types(client, auth_headers):
    binder_id = _binder(client, auth_headers, "Révisions")
    set_id, item = _qcm_set(client, auth_headers, binder_id, "QCM Maths")
    # Un passage réussi pour alimenter les stats.
    client.post(f"/api/v1/revision/sets/{set_id}/run",
                json={"answers": [{"item_id": item["id"], "selected_option_ids": ["b"]}]},
                headers=auth_headers)
    # Un second ensemble d'un autre type (sans révision).
    vf_id = client.post("/api/v1/revision/sets", json={
        "name": "VF Histoire", "type": "vf", "binder_id": binder_id,
    }, headers=auth_headers).json["id"]
    client.post(f"/api/v1/revision/sets/{vf_id}/items",
                json={"payload": {"assertion": "Vrai ?", "correct": True}}, headers=auth_headers)

    resp = client.get(f"/api/v1/stats/binders/{binder_id}", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json
    assert body["binder_id"] == binder_id
    assert body["sets_count"] == 2
    assert body["items_count"] == 2
    assert body["reviewed_items"] == 1
    types = {b["type"]: b for b in body["by_type"]}
    assert types["qcm"]["sets_count"] == 1 and types["vf"]["sets_count"] == 1
    assert isinstance(body["verdicts"], list) and len(body["verdicts"]) >= 1
    assert isinstance(body["weakest_sets"], list)


def test_binder_stats_includes_descendants_by_default(client, auth_headers):
    parent_id = _binder(client, auth_headers, "Parent")
    child_id = _binder(client, auth_headers, "Enfant", parent_id=parent_id)
    _qcm_set(client, auth_headers, child_id, "QCM enfant")

    # Par défaut : inclut le sous-arbre.
    inc = client.get(f"/api/v1/stats/binders/{parent_id}", headers=auth_headers).json
    assert inc["sets_count"] == 1 and inc["items_count"] == 1

    # descendants=false : seulement le classeur direct (vide ici).
    excl = client.get(f"/api/v1/stats/binders/{parent_id}?descendants=false", headers=auth_headers).json
    assert excl["sets_count"] == 0 and excl["items_count"] == 0


def test_binder_stats_isolation_between_users(client, auth_headers):
    binder_id = _binder(client, auth_headers, "Privé")
    _qcm_set(client, auth_headers, binder_id)
    client.post("/api/v1/auth/register",
                json={"email": "ob@example.com", "username": "obuser", "password": "password123"})
    other = client.post("/api/v1/auth/login",
                        json={"email": "ob@example.com", "password": "password123"}).json["access_token"]
    resp = client.get(f"/api/v1/stats/binders/{binder_id}",
                      headers={"Authorization": f"Bearer {other}"})
    assert resp.status_code in (403, 404)


def test_binder_stats_query_budget(client, auth_headers, app):
    """Pas de N+1 : budget borné quel que soit le nombre d'ensembles/items."""
    binder_id = _binder(client, auth_headers, "Gros classeur")
    for s in range(3):
        sid = client.post("/api/v1/revision/sets", json={
            "name": f"VF {s}", "type": "vf", "binder_id": binder_id,
        }, headers=auth_headers).json["id"]
        for i in range(4):
            client.post(f"/api/v1/revision/sets/{sid}/items",
                        json={"payload": {"assertion": f"A{s}-{i}", "correct": True}}, headers=auth_headers)

    from app.extensions import db
    from app.services.revision_stats_service import RevisionStatsService
    from app.dao.revision_dao import RevisionSetDAO, RevisionItemDAO
    from app.dao.study_session_dao import StudySessionDAO
    from app.dao.binder_dao import BinderDAO

    with app.app_context():
        from app.models.user import User
        uid = User.query.filter_by(email="test@example.com").first().id
        svc = RevisionStatsService(
            RevisionSetDAO(db.session), RevisionItemDAO(db.session),
            StudySessionDAO(db.session), BinderDAO(db.session),
        )
        from sqlalchemy import event
        engine = db.session.get_bind()
        count = {"n": 0}

        def _before(conn, cursor, statement, params, context, executemany):
            count["n"] += 1

        event.listen(engine, "before_cursor_execute", _before)
        try:
            result = svc.get_binder_stats(uid, binder_id)
        finally:
            event.remove(engine, "before_cursor_execute", _before)

    assert result.sets_count == 3 and result.items_count == 12
    # Indépendant du nombre d'items : accès binder + descendants + sets + items
    # + 1 requête de sessions par type présent (ici 1 type). Marge raisonnable.
    assert count["n"] <= 8
