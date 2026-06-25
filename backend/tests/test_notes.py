def test_create_note_strips_xss_vectors(client, auth_headers):
    # Le contenu d'une note est du Markdown : on neutralise les vecteurs
    # exécutables sans échapper la ponctuation Markdown.
    xss_content = "<p>Hello World</p><script>alert('XSS')</script><iframe src='javascript:alert(1)'></iframe><img src='x' onerror='alert(2)'>"

    response = client.post("/api/v1/notes", headers=auth_headers, json={
        "title": "Test XSS Note",
        "content": xss_content
    })

    assert response.status_code == 201
    content = response.json["content"]
    # script et iframe (et leur contenu) sont supprimés.
    assert "<script>" not in content
    assert "alert('XSS')" not in content
    assert "iframe" not in content
    # Le gestionnaire on* inline est retiré, l'image reste.
    assert "onerror" not in content
    assert "<img src='x'>" in content
    # Le contenu Markdown/HTML bénin est préservé tel quel.
    assert "<p>Hello World</p>" in content


def test_update_note_strips_xss_vectors(client, auth_headers):
    create_resp = client.post("/api/v1/notes", headers=auth_headers, json={
        "title": "Clean Note",
        "content": "<p>Clean</p>"
    })
    note_id = create_resp.json["id"]

    xss_content = "<div onclick='malicious()'>Click me</div><a href='javascript:alert(1)'>Link</a>"
    update_resp = client.put(f"/api/v1/notes/{note_id}", headers=auth_headers, json={
        "content": xss_content
    })

    assert update_resp.status_code == 200
    content = update_resp.json["content"]
    # Le gestionnaire on* et l'URI javascript: sont neutralisés.
    assert "onclick" not in content
    assert "javascript:" not in content
    # Le texte légitime est conservé.
    assert "Click me" in content
    assert "Link" in content


def test_note_preserves_markdown_punctuation(client, auth_headers):
    """Régression : le Markdown (citations `>`, comparaisons `<`/`>`, `&`)
    ne doit pas être échappé en entités HTML par le sanitizer serveur."""
    markdown = (
        "> Une citation importante\n\n"
        "Comparaison : si a > b et c < d alors ok.\n\n"
        "Flèche -> suite & fin.\n\n"
        "| Col A | Col B |\n|---|---|\n| a > b | c < d |\n"
    )

    response = client.post("/api/v1/notes", headers=auth_headers, json={
        "title": "Markdown intact",
        "content": markdown
    })

    assert response.status_code == 201
    content = response.json["content"]
    assert content == markdown
    assert "&gt;" not in content
    assert "&lt;" not in content
    assert "&amp;" not in content


def test_copy_note_does_not_double_escape(client, auth_headers):
    """Régression bug #2 : copier une note ne doit pas transformer ses
    caractères en entités HTML."""
    markdown = "> Citation\n\nSi x > 0 alors x < 10.\n"
    create_resp = client.post("/api/v1/notes", headers=auth_headers, json={
        "title": "Source",
        "content": markdown
    })
    note_id = create_resp.json["id"]

    copy_resp = client.post(f"/api/v1/notes/{note_id}/copy", headers=auth_headers)
    assert copy_resp.status_code in (200, 201)
    copied = copy_resp.json["content"]
    assert "&gt;" not in copied
    assert "&lt;" not in copied
    assert copied == markdown
