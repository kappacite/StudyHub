import xml.etree.ElementTree as ET

def test_sitemap_xml_format_and_content(client, clean_db):
    # 1. Requête sur l'endpoint sitemap.xml
    response = client.get("/sitemap.xml")
    
    # 2. Assertions sur le code HTTP et le type de contenu
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/xml"
    
    # 3. Validation de la syntaxe XML
    root = ET.fromstring(response.data)
    assert root.tag == "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset"
    
    # 4. Vérifier la présence des pages statiques
    locs = [loc.text for loc in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    assert "https://study.leshen.cloud/" in locs
    assert "https://study.leshen.cloud/explore" in locs
    assert "https://study.leshen.cloud/login" in locs
    assert "https://study.leshen.cloud/register" in locs

def test_sitemap_includes_public_resources(client, clean_db):
    from app.extensions import db
    from app.models.user import User
    from app.models.binder import Binder
    from app.models.note import Note
    
    # 1. Créer un utilisateur, un binder public et une note publique
    user = User(email="author@example.com", username="author")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()
    
    binder = Binder(name="Public Binder", user_id=user.id, is_public=True)
    note = Note(title="Public Note", user_id=user.id, is_public=True, share_token="test_token")
    
    db.session.add(binder)
    db.session.add(note)
    db.session.commit()
    
    # 2. Requête sur le sitemap
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    
    root = ET.fromstring(response.data)
    locs = [loc.text for loc in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    
    # 3. Vérifier que les ressources créées sont listées
    assert f"https://study.leshen.cloud/package/{binder.id}" in locs
    assert "https://study.leshen.cloud/notes/public/test_token" in locs
