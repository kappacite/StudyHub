def test_register_success(client):
    response = client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "securepassword123"
    })
    assert response.status_code == 201
    assert "id" in response.json
    assert response.json["email"] == "newuser@example.com"
    assert response.json["username"] == "newuser"

def test_register_duplicate_email(client, test_user):
    response = client.post("/api/v1/auth/register", json={
        "email": test_user["email"],  # Déjà existant
        "username": "uniqueusername",
        "password": "password123"
    })
    assert response.status_code == 409
    assert response.json["error"]["code"] == "CONFLICT"

def test_login_success(client, test_user):
    response = client.post("/api/v1/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    assert response.status_code == 200
    assert "access_token" in response.json
    assert "refresh_token" in response.json
    assert response.json["user"]["email"] == test_user["email"]

def test_login_invalid_password(client, test_user):
    response = client.post("/api/v1/auth/login", json={
        "email": test_user["email"],
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json["error"]["code"] == "UNAUTHORIZED"

def test_refresh_token(client, test_user):
    # D'abord se connecter pour avoir le refresh token
    login_resp = client.post("/api/v1/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    refresh_token = login_resp.json["refresh_token"]
    
    # Rafraîchir
    response = client.post("/api/v1/auth/refresh", headers={
        "Authorization": f"Bearer {refresh_token}"
    })
    assert response.status_code == 200
    assert "access_token" in response.json

def test_delete_account(client, auth_headers):
    # Supprimer le compte avec les headers d'auth
    response = client.delete("/api/v1/auth/account", headers=auth_headers)
    assert response.status_code == 204
    
    # Vérifier qu'on ne peut plus se connecter
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert login_resp.status_code == 401

def test_logout_revocation(client, test_user):
    # Connecter l'utilisateur pour obtenir le token
    login_resp = client.post("/api/v1/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    token = login_resp.json["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Valider que l'accès à un endpoint protégé fonctionne
    protected_resp = client.get("/api/v1/binders", headers=headers)
    assert protected_resp.status_code == 200
    
    # Effectuer la déconnexion
    logout_resp = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_resp.status_code == 204
    
    # Vérifier que le token est révoqué et l'accès refusé
    revoked_resp = client.get("/api/v1/binders", headers=headers)
    assert revoked_resp.status_code == 401
    assert revoked_resp.json["error"]["code"] == "UNAUTHORIZED"

