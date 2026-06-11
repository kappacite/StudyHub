import json
from app.models.user import User
from app.models.group import Group, GroupMember, GroupBinder, GroupActivity
from app.models.binder import Binder
from app.models.study_session import StudySession
from app.extensions import db

def _create_other_user(app, email, username):
    with app.app_context():
        user = User(email=email, username=username)
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user.id

def _get_auth_headers(client, email, password="password123"):
    response = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password
    })
    token = response.json["access_token"]
    return {
        "Authorization": f"Bearer {token}"
    }

def test_create_group_generates_unique_invite_code(client, auth_headers, test_user):
    resp = client.post("/api/v1/groups", json={
        "name": "Groupe de Médecine",
        "description": "Groupe pour les étudiants en PACES"
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json
    assert data["name"] == "Groupe de Médecine"
    assert len(data["invite_code"]) == 8
    assert data["created_by"] == test_user["id"]
    assert data["members_count"] == 1
    assert data["binders_count"] == 0

def test_join_group_by_invite_code(client, auth_headers, test_user, app):
    # 1. Créer le groupe
    resp = client.post("/api/v1/groups", json={
        "name": "Groupe d'Histoire",
        "description": "Histoire contemporaine"
    }, headers=auth_headers)
    invite_code = resp.json["invite_code"]
    group_id = resp.json["id"]

    # 2. Créer un autre utilisateur et se connecter
    user2_id = _create_other_user(app, "user2@example.com", "user2")
    user2_headers = _get_auth_headers(client, "user2@example.com")

    # 3. Rejoindre le groupe
    join_resp = client.post("/api/v1/groups/join", json={
        "invite_code": invite_code
    }, headers=user2_headers)
    assert join_resp.status_code == 200
    assert join_resp.json["members_count"] == 2

    # 4. Vérifier les détails du groupe
    detail_resp = client.get(f"/api/v1/groups/{group_id}", headers=auth_headers)
    assert detail_resp.status_code == 200
    members = detail_resp.json["members"]
    assert len(members) == 2
    assert any(m["user_id"] == user2_id and m["role"] == "member" for m in members)
    assert any(m["user_id"] == test_user["id"] and m["role"] == "owner" for m in members)

def test_join_invalid_code_returns_404(client, auth_headers):
    resp = client.post("/api/v1/groups/join", json={
        "invite_code": "INVALID1"
    }, headers=auth_headers)
    assert resp.status_code == 404
    assert "code" in resp.json["error"]
    assert resp.json["error"]["code"] == "RESOURCE_NOT_FOUND"

def test_max_groups_per_user_enforced(client, auth_headers, test_user, app):
    # Créer 5 groupes (limite maximale autorisée)
    for i in range(5):
        resp = client.post("/api/v1/groups", json={
            "name": f"Group {i}"
        }, headers=auth_headers)
        assert resp.status_code == 201

    # Le 6ème doit échouer
    resp_fail = client.post("/api/v1/groups", json={
        "name": "Group 6"
    }, headers=auth_headers)
    assert resp_fail.status_code == 403
    assert resp_fail.json["error"]["code"] == "FORBIDDEN"

    # Tester la limite de 20 groupes rejoints
    # Créer 20 groupes avec un autre utilisateur directement dans la base de données
    user2_id = _create_other_user(app, "user2@example.com", "user2")

    codes = []
    with app.app_context():
        for i in range(20):
            group = Group(
                name=f"Target Group {i}",
                invite_code=f"CD{i:06d}",
                created_by=user2_id
            )
            db.session.add(group)
            db.session.commit()
            db.session.refresh(group)
            
            # Ajouter user2 comme owner
            member = GroupMember(group_id=group.id, user_id=user2_id, role="owner")
            db.session.add(member)
            db.session.commit()
            
            codes.append(group.invite_code)

    # L'utilisateur principal en rejoint 15 de plus (déjà membre de ses 5 créés, donc total = 20)
    for i in range(15):
        join_resp = client.post("/api/v1/groups/join", json={
            "invite_code": codes[i]
        }, headers=auth_headers)
        assert join_resp.status_code == 200

    # Le 16ème doit échouer (car cela ferait 5 + 16 = 21 groupes rejoints)
    join_fail = client.post("/api/v1/groups/join", json={
        "invite_code": codes[15]
    }, headers=auth_headers)
    assert join_fail.status_code == 403
    assert join_fail.json["error"]["code"] == "FORBIDDEN"

def test_share_binder_requires_owner_role(client, auth_headers, test_user, app):
    # 1. Créer un classeur appartenant à l'utilisateur principal
    with app.app_context():
        binder1 = Binder(user_id=test_user["id"], name="Classeur Gynéco")
        db.session.add(binder1)
        db.session.commit()
        binder1_id = binder1.id

    # 2. Créer un groupe
    resp = client.post("/api/v1/groups", json={
        "name": "Groupe Santé"
    }, headers=auth_headers)
    group_id = resp.json["id"]
    invite_code = resp.json["invite_code"]

    # 3. Partager le classeur (Succès car propriétaire du classeur)
    share_resp = client.post(f"/api/v1/groups/{group_id}/binders", json={
        "binder_id": binder1_id,
        "permission": "read"
    }, headers=auth_headers)
    assert share_resp.status_code == 200
    assert share_resp.json["binder_name"] == "Classeur Gynéco"

    # 4. Créer un autre utilisateur
    user2_id = _create_other_user(app, "user2@example.com", "user2")
    user2_headers = _get_auth_headers(client, "user2@example.com")

    # Rejoindre le groupe
    client.post("/api/v1/groups/join", json={"invite_code": invite_code}, headers=user2_headers)

    # Créer un classeur pour l'utilisateur 2
    with app.app_context():
        binder2 = Binder(user_id=user2_id, name="Classeur Cardio")
        db.session.add(binder2)
        db.session.commit()
        binder2_id = binder2.id

    # 5. L'utilisateur 1 essaie de partager le classeur de l'utilisateur 2 -> 403
    share_fail = client.post(f"/api/v1/groups/{group_id}/binders", json={
        "binder_id": binder2_id,
        "permission": "read"
    }, headers=auth_headers)
    assert share_fail.status_code == 403

def test_progress_endpoint_returns_only_aggregated_data(client, auth_headers, test_user, app):
    # 1. Créer le groupe
    resp = client.post("/api/v1/groups", json={
        "name": "Groupe Progrès"
    }, headers=auth_headers)
    group_id = resp.json["id"]
    invite_code = resp.json["invite_code"]

    # 2. Enregistrer une session d'étude pour l'utilisateur principal
    session_data = {
        "module": "flashcard",
        "duration_seconds": 1200,
        "cards_reviewed": 15,
        "cards_correct": 12
    }
    client.post("/api/v1/stats/sessions", json=session_data, headers=auth_headers)

    # 3. Récupérer la progression
    prog_resp = client.get(f"/api/v1/groups/{group_id}/members/progress", headers=auth_headers)
    assert prog_resp.status_code == 200
    
    data = prog_resp.json
    assert len(data) == 1
    assert data[0]["user_id"] == test_user["id"]
    assert data[0]["total_time_seconds"] == 1200
    assert data[0]["cards_reviewed"] == 15
    assert data[0]["cards_correct"] == 12
    
    # S'assurer que le contenu privé n'est pas présent
    assert "cards" not in data[0]
    assert "answers" not in data[0]

def test_activity_recorded_on_events(client, auth_headers, test_user, app):
    # 1. Créer le groupe (génère une activité 'joined' du créateur)
    resp = client.post("/api/v1/groups", json={
        "name": "Groupe Activités"
    }, headers=auth_headers)
    group_id = resp.json["id"]
    invite_code = resp.json["invite_code"]

    # 2. Créer un classeur et le partager
    with app.app_context():
        binder = Binder(user_id=test_user["id"], name="Classeur Actif")
        db.session.add(binder)
        db.session.commit()
        binder_id = binder.id

    client.post(f"/api/v1/groups/{group_id}/binders", json={
        "binder_id": binder_id,
        "permission": "write"
    }, headers=auth_headers)

    # 3. Terminer une session d'étude (doit déclencher une activité 'completed_session')
    session_data = {
        "module": "note",
        "duration_seconds": 600,
        "cards_reviewed": 0,
        "cards_correct": 0
    }
    client.post("/api/v1/stats/sessions", json=session_data, headers=auth_headers)

    # 4. Récupérer le fil d'activité
    act_resp = client.get(f"/api/v1/groups/{group_id}/activity", headers=auth_headers)
    assert act_resp.status_code == 200
    activities = act_resp.json
    
    # Nous devons avoir 3 activités : joined, shared_binder, completed_session
    assert len(activities) == 3
    
    types = [a["type"] for a in activities]
    assert "joined" in types
    assert "shared_binder" in types
    assert "completed_session" in types
