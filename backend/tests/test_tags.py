import pytest
from app.extensions import db
from app.models.note import Note
from app.models.tag import Tag
from app.models.user import User
from app.dao.tag_dao import TagDAO
from app.schemas.tag_schema import TagCreateSchema, TagSetSchema
from app.services.tag_service import TagService
from app.middlewares.error_handler import ConflictError, ForbiddenError, ValidationError


@pytest.fixture
def tag_service(app):
    with app.app_context():
        yield TagService(TagDAO(db.session))


@pytest.fixture
def other_user(app):
    with app.app_context():
        user = User(email="tag-other@example.com", username="tagother")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return {"id": user.id, "email": user.email, "username": user.username}


def test_create_tag_success(tag_service, test_user):
    tag = tag_service.create_tag(test_user["id"], TagCreateSchema(name="Chimie", color="#4F46E5"))

    assert tag.name == "Chimie"
    assert tag.color == "#4F46E5"


def test_create_tag_duplicate_name_raises_conflict(tag_service, test_user):
    tag_service.create_tag(test_user["id"], TagCreateSchema(name="Chimie", color=None))

    with pytest.raises(ConflictError):
        tag_service.create_tag(test_user["id"], TagCreateSchema(name="Chimie", color=None))


def test_create_tag_invalid_color_raises_validation(tag_service, test_user):
    with pytest.raises(ValidationError):
        tag_service.create_tag(test_user["id"], TagCreateSchema(name="Bio", color="blue"))


def test_max_tags_per_user_raises_limit_error(tag_service, test_user):
    for index in range(50):
        tag_service.create_tag(test_user["id"], TagCreateSchema(name=f"Tag {index}", color=None))

    with pytest.raises(ValidationError):
        tag_service.create_tag(test_user["id"], TagCreateSchema(name="Tag 51", color=None))


def test_set_tags_for_note_replaces_existing(tag_service, test_user):
    note = Note(title="Note", content="Content", user_id=test_user["id"])
    db.session.add(note)
    db.session.commit()
    first = tag_service.create_tag(test_user["id"], TagCreateSchema(name="A", color=None))
    second = tag_service.create_tag(test_user["id"], TagCreateSchema(name="B", color=None))

    tag_service.set_tags_for_entity(test_user["id"], "notes", note.id, [first.id])
    tags = tag_service.set_tags_for_entity(test_user["id"], "notes", note.id, [second.id])

    assert [tag.id for tag in tags] == [second.id]


def test_delete_tag_removes_all_associations(tag_service, test_user):
    note = Note(title="Note", content="Content", user_id=test_user["id"])
    db.session.add(note)
    db.session.commit()
    tag = tag_service.create_tag(test_user["id"], TagCreateSchema(name="A", color=None))
    tag_service.set_tags_for_entity(test_user["id"], "notes", note.id, [tag.id])

    tag_service.delete_tag(test_user["id"], tag.id)
    db.session.refresh(note)

    assert note.tags == []


def test_get_tags_requires_auth(client):
    response = client.get("/api/v1/tags")

    assert response.status_code == 401


def test_post_tag_creates_and_returns_201(client, auth_headers):
    response = client.post("/api/v1/tags", json={"name": "Math", "color": "#22C55E"}, headers=auth_headers)

    assert response.status_code == 201
    assert response.json["name"] == "Math"


def test_filter_notes_by_tag_id(client, auth_headers):
    tag_response = client.post("/api/v1/tags", json={"name": "Bio"}, headers=auth_headers)
    tagged_note = client.post("/api/v1/notes", json={"title": "Cellule", "content": ""}, headers=auth_headers)
    client.post("/api/v1/notes", json={"title": "Analyse", "content": ""}, headers=auth_headers)
    client.post(
        f"/api/v1/notes/{tagged_note.json['id']}/tags",
        json={"tag_ids": [tag_response.json["id"]]},
        headers=auth_headers,
    )

    response = client.get(f"/api/v1/notes?tag_id={tag_response.json['id']}", headers=auth_headers)

    assert response.status_code == 200
    assert [note["title"] for note in response.json["data"]] == ["Cellule"]
    assert response.json["data"][0]["tags"][0]["name"] == "Bio"


def test_filter_decks_by_tag_id(client, auth_headers):
    tag_response = client.post("/api/v1/tags", json={"name": "DeckTag"}, headers=auth_headers)
    tagged_deck = client.post("/api/v1/decks", json={"name": "Deck A", "description": ""}, headers=auth_headers)
    client.post("/api/v1/decks", json={"name": "Deck B", "description": ""}, headers=auth_headers)
    client.post(
        f"/api/v1/decks/{tagged_deck.json['id']}/tags",
        json={"tag_ids": [tag_response.json["id"]]},
        headers=auth_headers,
    )

    response = client.get(f"/api/v1/decks?tag_id={tag_response.json['id']}", headers=auth_headers)

    assert response.status_code == 200
    assert [deck["name"] for deck in response.json["data"]] == ["Deck A"]


def test_tag_belongs_to_user_isolation(tag_service, test_user, other_user):
    tag = tag_service.create_tag(other_user["id"], TagCreateSchema(name="Private", color=None))
    note = Note(title="Note", content="", user_id=test_user["id"])
    db.session.add(note)
    db.session.commit()

    with pytest.raises(ForbiddenError):
        tag_service.set_tags_for_entity(test_user["id"], "notes", note.id, [tag.id])
