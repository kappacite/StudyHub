"""
Tests PR4 — Engagement classe : annonces, fil, notifications, classement.
"""
from app.models.user import User
from app.extensions import db


def _create_user(app, email, username):
    with app.app_context():
        u = User(email=email, username=username)
        u.set_password("password123")
        db.session.add(u)
        db.session.commit()
        db.session.refresh(u)
        return u.id


def _login(client, email):
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    return {"Authorization": f"Bearer {r.json['access_token']}"}


def _class_with_student(client, teacher_headers, app, email):
    resp = client.post("/api/v1/classes", json={"name": "Classe Engagement"}, headers=teacher_headers)
    class_id, invite = resp.json["id"], resp.json["invite_code"]
    sid = _create_user(app, email, email.split("@")[0])
    sh = _login(client, email)
    client.post("/api/v1/groups/join", json={"invite_code": invite}, headers=sh)
    return class_id, sid, sh


def test_announcement_posts_to_feed_and_notifies(client, auth_headers, app):
    class_id, sid, sh = _class_with_student(client, auth_headers, app, "eng1@test.com")

    # L'élève ne peut pas publier d'annonce.
    bad = client.post(f"/api/v1/classes/{class_id}/announcements",
                      json={"title": "Coucou"}, headers=sh)
    assert bad.status_code == 403

    # Le prof publie une annonce.
    ok = client.post(f"/api/v1/classes/{class_id}/announcements",
                     json={"title": "Contrôle vendredi", "body": "Réviser le ch.3"}, headers=auth_headers)
    assert ok.status_code == 201
    assert ok.json["type"] == "announcement"
    assert ok.json["payload"]["title"] == "Contrôle vendredi"

    # L'annonce apparaît dans le fil.
    feed = client.get(f"/api/v1/classes/{class_id}/feed", headers=sh)
    assert feed.status_code == 200
    assert any(f["type"] == "announcement" and f["payload"]["title"] == "Contrôle vendredi" for f in feed.json)

    # L'élève a reçu une notification.
    notifs = client.get("/api/v1/notifications", headers=sh)
    assert notifs.status_code == 200
    titles = [n["title"] for n in notifs.json]
    assert "Contrôle vendredi" in titles


def test_new_assignment_creates_notification(client, auth_headers, app):
    class_id, sid, sh = _class_with_student(client, auth_headers, app, "eng2@test.com")
    binder_id = client.post("/api/v1/binders", json={"name": "B"}, headers=auth_headers).json["id"]
    client.post(f"/api/v1/classes/{class_id}/assignments", json={
        "title": "Devoir noté", "tasks": [{"task_type": "flashcards", "ref": binder_id}],
    }, headers=auth_headers)

    count = client.get("/api/v1/notifications/unread-count", headers=sh)
    assert count.status_code == 200
    assert count.json["count"] >= 1

    notifs = client.get("/api/v1/notifications?unread=1", headers=sh).json
    assert any(n["type"] == "new_assignment" for n in notifs)


def test_mark_notifications_read(client, auth_headers, app):
    class_id, sid, sh = _class_with_student(client, auth_headers, app, "eng3@test.com")
    client.post(f"/api/v1/classes/{class_id}/announcements",
                json={"title": "A1"}, headers=auth_headers)
    client.post(f"/api/v1/classes/{class_id}/announcements",
                json={"title": "A2"}, headers=auth_headers)

    notifs = client.get("/api/v1/notifications", headers=sh).json
    assert len(notifs) >= 2
    first_id = notifs[0]["id"]

    # Marquer une notification comme lue.
    r = client.patch(f"/api/v1/notifications/{first_id}/read", headers=sh)
    assert r.status_code == 204

    # Tout marquer comme lu → 0 non lues.
    client.post("/api/v1/notifications/read-all", headers=sh)
    assert client.get("/api/v1/notifications/unread-count", headers=sh).json["count"] == 0


def test_leaderboard_lists_students(client, auth_headers, app):
    class_id, sid, sh = _class_with_student(client, auth_headers, app, "eng4@test.com")

    lb = client.get(f"/api/v1/classes/{class_id}/leaderboard", headers=auth_headers)
    assert lb.status_code == 200
    assert lb.json["enabled"] is True
    assert any(e["user_id"] == sid for e in lb.json["entries"])

    # L'élève accède aussi au classement.
    lb_student = client.get(f"/api/v1/classes/{class_id}/leaderboard", headers=sh)
    assert lb_student.status_code == 200


def test_leaderboard_disabled_returns_empty(client, auth_headers, app):
    from app.models.group import Group
    class_id, sid, sh = _class_with_student(client, auth_headers, app, "eng5@test.com")
    with app.app_context():
        g = db.session.get(Group, class_id)
        g.leaderboard_enabled = False
        db.session.commit()

    lb = client.get(f"/api/v1/classes/{class_id}/leaderboard", headers=auth_headers)
    assert lb.status_code == 200
    assert lb.json["enabled"] is False
    assert lb.json["entries"] == []


def test_notification_isolation_between_users(client, auth_headers, app):
    """Un élève ne voit pas/ne peut pas marquer la notification d'un autre."""
    class_id, sid_a, sh_a = _class_with_student(client, auth_headers, app, "engA@test.com")
    # Deuxième élève
    invite = client.get("/api/v1/classes", headers=auth_headers).json[0]["invite_code"]
    sid_b = _create_user(app, "engB@test.com", "engB")
    sh_b = _login(client, "engB@test.com")
    client.post("/api/v1/groups/join", json={"invite_code": invite}, headers=sh_b)

    client.post(f"/api/v1/classes/{class_id}/announcements",
                json={"title": "Pour tous"}, headers=auth_headers)

    notifs_a = client.get("/api/v1/notifications", headers=sh_a).json
    notif_a_id = notifs_a[0]["id"]
    # B ne peut pas marquer la notification de A.
    r = client.patch(f"/api/v1/notifications/{notif_a_id}/read", headers=sh_b)
    assert r.status_code == 404
