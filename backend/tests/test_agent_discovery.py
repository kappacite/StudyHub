import json

def test_api_catalog_endpoint(client):
    response = client.get("/.well-known/api-catalog")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/linkset+json; charset=utf-8"
    data = json.loads(response.data)
    assert "linkset" in data
    assert len(data["linkset"]) > 0
    assert data["linkset"][0]["anchor"] == "https://study.leshen.cloud/api/v1"

def test_oauth_discovery_endpoints(client):
    for path in ["/.well-known/openid-configuration", "/.well-known/oauth-authorization-server"]:
        response = client.get(path)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["issuer"] == "https://study.leshen.cloud"
        assert "agent_auth" in data
        assert data["agent_auth"]["register_uri"] == "https://study.leshen.cloud/register"

def test_oauth_protected_resource_endpoint(client):
    response = client.get("/.well-known/oauth-protected-resource")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["resource"] == "https://study.leshen.cloud/api/v1"

def test_agent_card_endpoint(client):
    response = client.get("/.well-known/agent-card.json")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["name"] == "StudyHub Assistant"
    assert "capabilities" in data

def test_mcp_server_card_endpoint(client):
    response = client.get("/.well-known/mcp/server-card.json")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["serverInfo"]["name"] == "StudyHub MCP Server"

def test_agent_skills_index_and_md(client):
    response = client.get("/.well-known/agent-skills/index.json")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "$schema" in data
    skill = data["skills"][0]
    assert skill["name"] == "study-sm2"
    
    response_md = client.get("/.well-known/agent-skills/study-sm2/SKILL.md")
    assert response_md.status_code == 200
    assert response_md.headers["Content-Type"] == "text/markdown; charset=utf-8"
    assert "# study-sm2" in response_md.text

def test_markdown_content_negotiation_root(client):
    response = client.get("/api/v1/markdown-root")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/markdown; charset=utf-8"
    assert "x-markdown-tokens" in response.headers
    assert "# StudyHub" in response.text

def test_markdown_content_negotiation_public_note(client, clean_db):
    from app.extensions import db
    from app.models.user import User
    from app.models.note import Note
    
    user = User(email="author@example.com", username="author")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()
    
    note = Note(title="My Markdown Note", content="Contenu en *Markdown*", user_id=user.id, is_public=True, share_token="test_token")
    db.session.add(note)
    db.session.commit()
    
    # Test avec en-tête Accept: text/markdown
    response = client.get("/api/v1/notes/public/test_token", headers={"Accept": "text/markdown"})
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/markdown; charset=utf-8"
    assert "# My Markdown Note" in response.text
    assert "Contenu en *Markdown*" in response.text
    
    # Test par défaut sans Accept (renvoie le JSON)
    response_json = client.get("/api/v1/notes/public/test_token")
    assert response_json.status_code == 200
    assert response_json.headers["Content-Type"] == "application/json"
    data = json.loads(response_json.data)
    assert data["title"] == "My Markdown Note"
