"""Tests A7 — statistiques par élément/ensemble de révision (indicateurs D5)."""

from datetime import datetime, timedelta

from app.services.revision_stats_service import (
    difficulty_from_ef,
    project_mastery_date,
    retrievability,
)

# --- Calculs unitaires (indicateurs D5) --------------------------------------


def test_difficulty_from_ef_bounds():
    assert difficulty_from_ef(2.5) == 1.0  # facile → difficulté minimale
    assert difficulty_from_ef(1.3) == 10.0  # dur → difficulté maximale
    assert 1.0 < difficulty_from_ef(1.9) < 10.0


def test_retrievability_decays_over_time():
    now = datetime.utcnow()
    fresh = retrievability(10, now, now)  # vient d'être révisé → ~1
    old = retrievability(10, now - timedelta(days=20), now)  # 2× la stabilité → bas
    assert fresh > old
    assert retrievability(0, None, now) == 0.0


def test_mastery_projection_reaches_threshold():
    now = datetime.utcnow()
    d = project_mastery_date(1, 2.5, now, now)
    assert d is not None and d >= now


# --- Endpoints ---------------------------------------------------------------


def _qcm_with_item(client, auth_headers):
    set_id = client.post(
        "/api/v1/revision/sets", json={"name": "S", "type": "qcm"}, headers=auth_headers
    ).json["id"]
    item = client.post(
        f"/api/v1/revision/sets/{set_id}/items",
        json={
            "payload": {
                "question": "2+2 ?",
                "options": [
                    {"id": "a", "text": "3", "correct": False},
                    {"id": "b", "text": "4", "correct": True},
                ],
            }
        },
        headers=auth_headers,
    ).json
    return set_id, item


def test_item_stats_after_reviews(client, auth_headers):
    set_id, item = _qcm_with_item(client, auth_headers)
    # 2 passages : 1 réussi, 1 raté.
    client.post(
        f"/api/v1/revision/sets/{set_id}/run",
        json={"answers": [{"item_id": item["id"], "selected_option_ids": ["b"]}]},
        headers=auth_headers,
    )
    client.post(
        f"/api/v1/revision/sets/{set_id}/run",
        json={"answers": [{"item_id": item["id"], "selected_option_ids": ["a"]}]},
        headers=auth_headers,
    )

    stats = client.get(f"/api/v1/stats/items/{item['id']}", headers=auth_headers)
    assert stats.status_code == 200
    body = stats.json
    assert body["reviews"] == 2
    assert body["lapses"] == 1
    assert body["success_rate"] == 50.0
    assert 1.0 <= body["difficulty"] <= 10.0
    assert 0.0 <= body["retrievability"] <= 1.0
    assert len(body["history"]) == 2


def test_set_stats_aggregates_and_verdicts(client, auth_headers):
    set_id, item = _qcm_with_item(client, auth_headers)
    client.post(
        f"/api/v1/revision/sets/{set_id}/run",
        json={"answers": [{"item_id": item["id"], "selected_option_ids": ["b"]}]},
        headers=auth_headers,
    )

    stats = client.get(f"/api/v1/stats/sets/{set_id}", headers=auth_headers)
    assert stats.status_code == 200
    body = stats.json
    assert body["items_count"] == 1
    assert body["reviewed_items"] == 1
    assert isinstance(body["verdicts"], list) and len(body["verdicts"]) >= 1


def test_set_stats_query_budget(client, auth_headers, app):
    """Agrégat d'ensemble : pas de N+1 (budget de requêtes borné quel que soit le nb d'items)."""
    set_id = client.post(
        "/api/v1/revision/sets", json={"name": "Big", "type": "vf"}, headers=auth_headers
    ).json["id"]
    for i in range(6):
        client.post(
            f"/api/v1/revision/sets/{set_id}/items",
            json={"payload": {"assertion": f"A{i}", "correct": True}},
            headers=auth_headers,
        )

    from app.dao.revision_dao import RevisionItemDAO, RevisionSetDAO
    from app.dao.study_session_dao import StudySessionDAO
    from app.extensions import db
    from app.services.revision_stats_service import RevisionStatsService

    with app.app_context():
        # JWT identity = id de l'utilisateur de test (1er créé).
        from app.models.user import User

        uid = User.query.filter_by(email="test@example.com").first().id
        svc = RevisionStatsService(
            RevisionSetDAO(db.session), RevisionItemDAO(db.session), StudySessionDAO(db.session)
        )

        from sqlalchemy import event

        engine = db.session.get_bind()
        count = {"n": 0}

        def _before(conn, cursor, statement, params, context, executemany):
            count["n"] += 1

        event.listen(engine, "before_cursor_execute", _before)
        try:
            svc.get_set_stats(uid, set_id)
        finally:
            event.remove(engine, "before_cursor_execute", _before)

    # Indépendant du nombre d'items : set + items + sessions (+ marge).
    assert count["n"] <= 6


def test_item_stats_isolation_between_users(client, auth_headers):
    set_id, item = _qcm_with_item(client, auth_headers)
    client.post(
        "/api/v1/auth/register",
        json={"email": "other2@example.com", "username": "otheruser2", "password": "password123"},
    )
    other = client.post(
        "/api/v1/auth/login", json={"email": "other2@example.com", "password": "password123"}
    ).json["access_token"]
    resp = client.get(
        f"/api/v1/stats/items/{item['id']}", headers={"Authorization": f"Bearer {other}"}
    )
    assert resp.status_code in (403, 404)


def test_stats_schemas_accept_nullable_set_type_and_item_type():
    """RevisionSetStats/RevisionSetSummary.type doit accepter None (ensemble
    heterogene, D8) -- ces schemas de stats n'avaient jamais ete alignes avec
    RevisionSetResponse.type. RevisionItemSummary doit porter son propre type
    (necessaire pour l'afficher/le regrouper cote frontend, reviser-hub)."""
    from app.schemas.revision_schema import (
        RevisionItemSummary,
        RevisionSetStats,
        RevisionSetSummary,
    )

    stats = RevisionSetStats(
        set_id=1,
        type=None,
        name="Mixte",
        items_count=0,
        reviewed_items=0,
        mastered_count=0,
        mastery_rate=0.0,
        avg_success_rate=0.0,
        true_retention=0.0,
        leeches_count=0,
        due_count=0,
        avg_difficulty=0.0,
        verdicts=[],
        items=[],
    )
    assert stats.type is None

    summary = RevisionSetSummary(
        set_id=1,
        type=None,
        name="Mixte",
        items_count=0,
        reviewed_items=0,
        mastered_count=0,
        mastery_rate=0.0,
        avg_success_rate=0.0,
        true_retention=0.0,
        leeches_count=0,
        due_count=0,
        avg_difficulty=0.0,
    )
    assert summary.type is None

    item_summary = RevisionItemSummary(
        item_id=1,
        type="flashcard",
        label="Chat",
        reviews=0,
        success_rate=0.0,
        difficulty=1.0,
        retrievability=0.0,
        is_leech=False,
        is_mature=False,
        due=False,
    )
    assert item_summary.type == "flashcard"


def test_item_stats_on_heterogeneous_set_item(client, auth_headers):
    """Un ensemble reellement heterogene (type: None, cree sans 'type' dans le
    body, cf. test_create_set_without_type_is_heterogeneous) : les stats d'un
    item doivent refleter ses sessions reelles. Avant le correctif,
    get_item_stats passait rset.type (None) au DAO polymorphe
    (item_id/item_type discrimine la source, pas de FK) au lieu de item.type
    -- item_type == None ne matche jamais aucune session reelle, l'historique
    restait silencieusement vide."""
    set_id = client.post(
        "/api/v1/revision/sets", json={"name": "Mixte"}, headers=auth_headers
    ).json["id"]
    item = client.post(
        f"/api/v1/revision/sets/{set_id}/items",
        json={
            "type": "flashcard",
            "payload": {"front": "Chat", "back": "Cat"},
        },
        headers=auth_headers,
    ).json

    client.post(
        f"/api/v1/revision/sets/{set_id}/study/answer/{item['id']}",
        json={"score": 4},
        headers=auth_headers,
    )

    stats = client.get(f"/api/v1/stats/items/{item['id']}", headers=auth_headers)
    assert stats.status_code == 200
    body = stats.json
    assert body["reviews"] == 1
    assert len(body["history"]) == 1


def test_set_stats_on_heterogeneous_set_counts_all_item_types(client, auth_headers):
    """Ensemble heterogene avec 2 types d'items notes : get_set_stats doit
    compter les deux. Avant le correctif, un seul appel de sessions groupe
    par rset.type (None) ne matchait aucune session reelle -> reviewed_items
    restait a 0 quel que soit le nombre de passages reels."""
    set_id = client.post(
        "/api/v1/revision/sets", json={"name": "Mixte"}, headers=auth_headers
    ).json["id"]
    flash = client.post(
        f"/api/v1/revision/sets/{set_id}/items",
        json={"type": "flashcard", "payload": {"front": "Chat", "back": "Cat"}},
        headers=auth_headers,
    ).json
    vf = client.post(
        f"/api/v1/revision/sets/{set_id}/items",
        json={"type": "vf", "payload": {"assertion": "Le ciel est bleu.", "correct": True}},
        headers=auth_headers,
    ).json

    client.post(
        f"/api/v1/revision/sets/{set_id}/study/answer/{flash['id']}",
        json={"score": 5},
        headers=auth_headers,
    )
    client.post(
        f"/api/v1/revision/sets/{set_id}/study/grade/{vf['id']}",
        json={"answer": {"value": True}},
        headers=auth_headers,
    )

    stats = client.get(f"/api/v1/stats/sets/{set_id}", headers=auth_headers)
    assert stats.status_code == 200
    body = stats.json
    assert body["type"] is None
    assert body["items_count"] == 2
    assert body["reviewed_items"] == 2
    types = {it["type"] for it in body["items"]}
    assert types == {"flashcard", "vf"}
