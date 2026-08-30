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


def _share_set_with_new_user(client, owner_headers, binder_name="Cours partagé"):
    """Cree un classeur + ensemble QCM appartenant a l'utilisateur courant
    (owner_headers), le partage via un groupe (permission read), et fait
    rejoindre un second utilisateur -- reproduit le cas legitime « cours
    partage » (SM-2 partage, cf. revision_service.py) sur lequel plusieurs
    utilisateurs enregistrent des StudySession sur les MEMES items."""
    binder_id = client.post(
        "/api/v1/binders", json={"name": binder_name}, headers=owner_headers
    ).json["id"]
    set_id, item = _qcm_with_item_in_binder(client, owner_headers, binder_id)

    group_resp = client.post("/api/v1/groups", json={"name": "Groupe stats"}, headers=owner_headers)
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
            "email": "student_stats@example.com",
            "username": "student_stats",
            "password": "password123",
        },
    )
    student_token = client.post(
        "/api/v1/auth/login",
        json={"email": "student_stats@example.com", "password": "password123"},
    ).json["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}
    client.post("/api/v1/groups/join", json={"invite_code": invite_code}, headers=student_headers)

    return set_id, item, student_headers


def _qcm_with_item_in_binder(client, headers, binder_id):
    set_id = client.post(
        "/api/v1/revision/sets",
        json={"name": "S", "type": "qcm", "binder_id": binder_id},
        headers=headers,
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
        headers=headers,
    ).json
    return set_id, item


def test_item_stats_scoped_to_requesting_user_on_shared_set(client, auth_headers):
    """Finding #2 (revue de branche reviser-hub) : un ensemble partage (« cours »)
    laisse legitimement plusieurs utilisateurs enregistrer des StudySession sur
    les memes items (SM-2 partage) -- mais les stats PERSONNELLES de chacun ne
    doivent refleter QUE ses propres sessions, pas celles blendees de tout le
    monde ayant acces."""
    set_id, item, student_headers = _share_set_with_new_user(client, auth_headers)

    # Le proprietaire reussit (grade eleve).
    client.post(
        f"/api/v1/revision/sets/{set_id}/run",
        json={"answers": [{"item_id": item["id"], "selected_option_ids": ["b"]}]},
        headers=auth_headers,
    )
    # L'eleve rate (grade bas) -- meme item, meme ensemble partage.
    client.post(
        f"/api/v1/revision/sets/{set_id}/run",
        json={"answers": [{"item_id": item["id"], "selected_option_ids": ["a"]}]},
        headers=student_headers,
    )

    owner_stats = client.get(f"/api/v1/stats/items/{item['id']}", headers=auth_headers).json
    student_stats = client.get(f"/api/v1/stats/items/{item['id']}", headers=student_headers).json

    # Sans le correctif : chacun verrait reviews == 2 et success_rate == 50 (les
    # deux sessions blendees), pas sa propre performance.
    assert owner_stats["reviews"] == 1
    assert owner_stats["success_rate"] == 100.0
    assert student_stats["reviews"] == 1
    assert student_stats["success_rate"] == 0.0


def test_set_stats_scoped_to_requesting_user_on_shared_set(client, auth_headers):
    """Meme correctif que ci-dessus, au niveau agrege de l'ensemble
    (avg_success_rate, true_retention...) -- get_set_stats passe par le meme
    DAO.get_for_items."""
    set_id, item, student_headers = _share_set_with_new_user(client, auth_headers)

    client.post(
        f"/api/v1/revision/sets/{set_id}/run",
        json={"answers": [{"item_id": item["id"], "selected_option_ids": ["b"]}]},
        headers=auth_headers,
    )
    client.post(
        f"/api/v1/revision/sets/{set_id}/run",
        json={"answers": [{"item_id": item["id"], "selected_option_ids": ["a"]}]},
        headers=student_headers,
    )

    owner_stats = client.get(f"/api/v1/stats/sets/{set_id}", headers=auth_headers).json
    student_stats = client.get(f"/api/v1/stats/sets/{set_id}", headers=student_headers).json

    assert owner_stats["avg_success_rate"] == 100.0
    assert student_stats["avg_success_rate"] == 0.0


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


def _definition_with_item(client, auth_headers):
    set_id = client.post(
        "/api/v1/revision/sets", json={"name": "D", "type": "definition"}, headers=auth_headers
    ).json["id"]
    item = client.post(
        f"/api/v1/revision/sets/{set_id}/items",
        json={"payload": {"term": "T", "definition": "D"}},
        headers=auth_headers,
    ).json
    return set_id, item


def _add_session(item_id, grade, created_at, duration_seconds=0):
    """Insere directement une StudySession avec un created_at controle -- le
    endpoint /study/answer ne permet pas de piloter created_at (server_default
    func.now(), insensible a freezegun sur SQLite) : necessaire pour tester le
    bucketing hebdomadaire/quotidien."""
    from app.extensions import db
    from app.models.study_session import StudySession

    db.session.add(
        StudySession(
            user_id=_add_session.uid,
            module="definition",
            duration_seconds=duration_seconds,
            cards_reviewed=1,
            cards_correct=1 if grade >= 3 else 0,
            item_id=item_id,
            item_type="definition",
            grade=grade,
            created_at=created_at,
        )
    )
    db.session.commit()


def test_set_stats_grade_distribution_buckets_sm2_scale(client, auth_headers, app):
    """Repartition des notes SM-2 (0-5, cf. invariants-sm2) en 4 paliers pedagogiques :
    0-1 -> Encore (echec net), 2 -> Difficile (echec limite), 3-4 -> Bien (reussite
    avec effort), 5 -> Facile (reussite parfaite). Le seuil reussite/echec SM-2 lui
    meme (score >= 3) tombe pile entre 'hard' et 'good' -- ce bucketing ajoute une
    graduation de chaque cote de cette frontiere, il ne la deplace pas."""
    set_id, item = _definition_with_item(client, auth_headers)

    from app.models.user import User

    with app.app_context():
        uid = User.query.filter_by(email="test@example.com").first().id
        _add_session.uid = uid
        now = datetime.utcnow()
        for grade in [0, 1, 2, 2, 3, 4, 5]:
            _add_session(item["id"], grade, now)

    stats = client.get(f"/api/v1/stats/sets/{set_id}", headers=auth_headers)
    assert stats.status_code == 200
    assert stats.json["grade_distribution"] == {"again": 2, "hard": 2, "good": 2, "easy": 1}


def test_set_stats_weekly_progression_six_week_window(client, auth_headers, app):
    """Progression hebdomadaire (6 dernieres semaines, semaines ISO lundi-dimanche) :
    une session vieille d'exactement 5 semaines tombe dans le bucket le plus ancien
    (index 0), la session du jour dans le plus recent (index 5) ; une session hors
    fenetre (10 semaines) est exclue du total."""
    set_id, item = _definition_with_item(client, auth_headers)

    from app.models.user import User

    with app.app_context():
        uid = User.query.filter_by(email="test@example.com").first().id
        _add_session.uid = uid
        now = datetime.utcnow()
        _add_session(item["id"], 5, now)  # semaine courante : reussite
        _add_session(item["id"], 1, now - timedelta(weeks=5))  # semaine la + ancienne : echec
        _add_session(item["id"], 5, now - timedelta(weeks=10))  # hors fenetre

    stats = client.get(f"/api/v1/stats/sets/{set_id}", headers=auth_headers)
    assert stats.status_code == 200
    weeks = stats.json["weekly_progression"]
    assert len(weeks) == 6
    assert weeks[0]["reviews"] == 1 and weeks[0]["success_rate"] == 0.0
    assert weeks[-1]["reviews"] == 1 and weeks[-1]["success_rate"] == 100.0
    assert sum(w["reviews"] for w in weeks) == 2  # la session a -10 semaines n'apparait pas


def test_set_stats_session_history_grouped_by_day(client, auth_headers, app):
    """Historique de sessions : une ligne par jour calendaire (created_at.date()),
    le plus recent en premier, avec le taux de reussite agrege du jour."""
    set_id, item = _definition_with_item(client, auth_headers)

    from app.models.user import User

    with app.app_context():
        uid = User.query.filter_by(email="test@example.com").first().id
        _add_session.uid = uid
        today_9am = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0)
        _add_session(item["id"], 5, today_9am)
        _add_session(item["id"], 1, today_9am + timedelta(hours=2))
        _add_session(item["id"], 4, today_9am - timedelta(days=1))

    stats = client.get(f"/api/v1/stats/sets/{set_id}", headers=auth_headers)
    assert stats.status_code == 200
    history = stats.json["session_history"]
    assert len(history) == 2
    assert history[0]["reviews"] == 2 and history[0]["success_rate"] == 50.0
    assert history[1]["reviews"] == 1 and history[1]["success_rate"] == 100.0


def test_set_stats_new_fields_default_when_never_reviewed(client, auth_headers):
    """Ensemble jamais revise : les nouveaux champs ont une forme saine (pas
    d'erreur de validation Pydantic, pas de division par zero)."""
    set_id = client.post(
        "/api/v1/revision/sets", json={"name": "Vide", "type": "qcm"}, headers=auth_headers
    ).json["id"]

    stats = client.get(f"/api/v1/stats/sets/{set_id}", headers=auth_headers)
    assert stats.status_code == 200
    body = stats.json
    assert body["grade_distribution"] == {"again": 0, "hard": 0, "good": 0, "easy": 0}
    assert len(body["weekly_progression"]) == 6
    assert all(w["reviews"] == 0 and w["success_rate"] == 0.0 for w in body["weekly_progression"])
    assert body["session_history"] == []
    assert body["total_duration_seconds"] == 0


# --- Duree cumulee reelle (Task 9, reviser-hub-redesign) ---------------------


def test_set_stats_total_duration_seconds_sums_real_sessions(client, auth_headers, app):
    """Temps cumule = somme des duration_seconds des sessions deja chargees
    par get_set_stats -- aucune requete supplementaire, pas de fabrication."""
    set_id, item = _definition_with_item(client, auth_headers)

    from app.models.user import User

    with app.app_context():
        uid = User.query.filter_by(email="test@example.com").first().id
        _add_session.uid = uid
        now = datetime.utcnow()
        _add_session(item["id"], 5, now, duration_seconds=30)
        _add_session(item["id"], 4, now - timedelta(days=1), duration_seconds=45)

    stats = client.get(f"/api/v1/stats/sets/{set_id}", headers=auth_headers)
    assert stats.status_code == 200
    assert stats.json["total_duration_seconds"] == 75


def test_set_stats_session_history_sums_duration_per_day(client, auth_headers, app):
    """La colonne Duree de l'historique doit sommer les sessions du meme jour
    calendaire, comme reviews/success_rate le font deja."""
    set_id, item = _definition_with_item(client, auth_headers)

    from app.models.user import User

    with app.app_context():
        uid = User.query.filter_by(email="test@example.com").first().id
        _add_session.uid = uid
        today_9am = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0)
        _add_session(item["id"], 5, today_9am, duration_seconds=20)
        _add_session(item["id"], 1, today_9am + timedelta(hours=2), duration_seconds=10)
        _add_session(item["id"], 4, today_9am - timedelta(days=1), duration_seconds=40)

    stats = client.get(f"/api/v1/stats/sets/{set_id}", headers=auth_headers)
    assert stats.status_code == 200
    history = stats.json["session_history"]
    assert len(history) == 2
    assert history[0]["duration_seconds"] == 30  # aujourd'hui : 20 + 10
    assert history[1]["duration_seconds"] == 40  # hier


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
        json={"answer": {"value": True}, "score": 5},
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
