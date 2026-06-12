def test_get_me_returns_profile(client, auth_headers, test_user):
    resp = client.get("/api/v1/users/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json["email"] == test_user["email"]
    assert resp.json["username"] == test_user["username"]
    # Le hash du mot de passe ne doit jamais fuiter dans la réponse.
    assert "password_hash" not in resp.json
    assert "password" not in resp.json


def test_get_me_requires_auth(client):
    resp = client.get("/api/v1/users/me")
    assert resp.status_code == 401


def test_update_me_changes_username(client, auth_headers):
    resp = client.put(
        "/api/v1/users/me",
        json={"username": "nouveaupseudo"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json["username"] == "nouveaupseudo"


def test_update_me_invalid_username_returns_400(client, auth_headers):
    # username trop court (< 3 caractères) -> validation Pydantic
    resp = client.put("/api/v1/users/me", json={"username": "ab"}, headers=auth_headers)
    assert resp.status_code == 400


def test_update_me_duplicate_email_conflicts(client, auth_headers):
    # Un second utilisateur occupe l'email convoité.
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": "autre@example.com", "username": "autreuser", "password": "password123"},
    )
    assert reg.status_code == 201

    resp = client.put(
        "/api/v1/users/me",
        json={"email": "autre@example.com"},
        headers=auth_headers,
    )
    assert resp.status_code == 409


def test_update_me_changes_email_to_unique_value(client, auth_headers):
    resp = client.put(
        "/api/v1/users/me",
        json={"email": "nouveau@example.com"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json["email"] == "nouveau@example.com"


def test_update_me_duplicate_username_conflicts(client, auth_headers):
    client.post(
        "/api/v1/auth/register",
        json={"email": "two@example.com", "username": "occupied", "password": "password123"},
    )
    resp = client.put(
        "/api/v1/users/me",
        json={"username": "occupied"},
        headers=auth_headers,
    )
    assert resp.status_code == 409


def test_update_me_password_change_allows_login(client, auth_headers, test_user):
    resp = client.put(
        "/api/v1/users/me",
        json={"password": "newpassword123"},
        headers=auth_headers,
    )
    assert resp.status_code == 200

    # L'ancien mot de passe ne fonctionne plus, le nouveau oui.
    old = client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]},
    )
    assert old.status_code == 401

    new = client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": "newpassword123"},
    )
    assert new.status_code == 200
    assert "access_token" in new.json


def test_delete_me_removes_account(client, auth_headers):
    resp = client.delete("/api/v1/users/me", headers=auth_headers)
    assert resp.status_code == 204

    # Le compte n'existe plus : le profil n'est plus accessible.
    follow_up = client.get("/api/v1/users/me", headers=auth_headers)
    assert follow_up.status_code == 404
