def test_create_note_sanitizes_html(client, auth_headers):
    # Create a note with malicious HTML content (XSS vectors)
    xss_content = "<p>Hello World</p><script>alert('XSS')</script><iframe src='javascript:alert(1)'></iframe><img src='x' onerror='alert(2)'>"
    
    response = client.post("/api/v1/notes", headers=auth_headers, json={
        "title": "Test XSS Note",
        "content": xss_content
    })
    
    assert response.status_code == 201
    note_data = response.json
    # Script and iframe should be completely stripped
    assert "<script>" not in note_data["content"]
    assert "alert" not in note_data["content"]
    assert "iframe" not in note_data["content"]
    assert "<p>Hello World</p>" in note_data["content"]
    # Bleach cleans onerror attribute but retains valid elements like img
    assert "<img src=\"x\">" in note_data["content"] or "<img>" in note_data["content"]

def test_update_note_sanitizes_html(client, auth_headers):
    # 1. Create a clean note
    create_resp = client.post("/api/v1/notes", headers=auth_headers, json={
        "title": "Clean Note",
        "content": "<p>Clean</p>"
    })
    note_id = create_resp.json["id"]
    
    # 2. Update with malicious HTML
    xss_content = "<div onclick='malicious()'>Click me</div><a href='javascript:alert(1)'>Link</a>"
    update_resp = client.put(f"/api/v1/notes/{note_id}", headers=auth_headers, json={
        "content": xss_content
    })
    
    assert update_resp.status_code == 200
    updated_data = update_resp.json
    # onclick and div should be stripped, javascript scheme should be neutralized
    assert "onclick" not in updated_data["content"]
    assert "javascript" not in updated_data["content"]
    assert "div" not in updated_data["content"]
    assert "Link" in updated_data["content"]
