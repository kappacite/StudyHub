import json
from datetime import datetime, timedelta
from app.models.user import User
from app.models.group import Group, GroupMember, GroupBinder
from app.models.binder import Binder
from app.models.deck import Deck
from app.models.flashcard import Flashcard
from app.models.note import Note
from app.extensions import db

def _create_user(app, email, username):
    with app.app_context():
        u = User(email=email, username=username)
        u.set_password("password123")
        db.session.add(u)
        db.session.commit()
        db.session.refresh(u)
        return u.id

def _login(client, email, password="password123"):
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {resp.json['access_token']}"}

def test_public_class_flow(client, auth_headers, test_user, app):
    # 1. Create a public class
    resp = client.post("/api/v1/classes", json={
        "name": "Biologie Cellulaire Publique",
        "description": "Cours public de biologie",
        "is_public": True
    }, headers=auth_headers)
    assert resp.status_code == 201
    class_id = resp.json["id"]
    assert resp.json["is_public"] is True

    # 2. Create another user (student)
    student_id = _create_user(app, "student_follow@test.com", "student_follow")
    student_headers = _login(client, "student_follow@test.com")

    # 3. Retrieve public classes list
    pub_list_resp = client.get("/api/v1/classes/public", headers=student_headers)
    assert pub_list_resp.status_code == 200
    public_classes = pub_list_resp.json
    assert any(c["id"] == class_id for c in public_classes)

    # 4. Student follows the public class
    follow_resp = client.post(f"/api/v1/classes/{class_id}/follow", json={}, headers=student_headers)
    assert follow_resp.status_code == 200
    assert follow_resp.json["members_count"] == 2

    # 5. Teacher shares a binder with the class
    # First create a binder, a note, a deck, and a card for the teacher
    with app.app_context():
        binder = Binder(user_id=test_user["id"], name="Classeur Biologie")
        db.session.add(binder)
        db.session.commit()
        
        note = Note(user_id=test_user["id"], binder=binder, title="Cours 1: La Cellule", content="Contenu important")
        db.session.add(note)
        
        deck = Deck(user_id=test_user["id"], binder=binder, name="Questions Biologie")
        db.session.add(deck)
        db.session.commit()

        card = Flashcard(deck_id=deck.id, front="Q1", back="R1")
        db.session.add(card)
        db.session.commit()
        
        binder_id = binder.id
        deck_id = deck.id
        card_id = card.id
        note_id = note.id

    # Share the binder with the class
    share_resp = client.post(f"/api/v1/groups/{class_id}/binders", json={
        "binder_id": binder_id,
        "permission": "read"
    }, headers=auth_headers)
    assert share_resp.status_code == 200

    # 6. Verify student can read the binder, deck, and note
    binder_read = client.get(f"/api/v1/binders/{binder_id}", headers=student_headers)
    assert binder_read.status_code == 200
    assert binder_read.json["name"] == "Classeur Biologie"

    note_read = client.get(f"/api/v1/notes/{note_id}", headers=student_headers)
    assert note_read.status_code == 200

    deck_read = client.get(f"/api/v1/decks/{deck_id}", headers=student_headers)
    assert deck_read.status_code == 200

    # 7. Verify student CANNOT edit note/deck/binder (ForbiddenError)
    note_write = client.put(f"/api/v1/notes/{note_id}", json={"content": "Tentative modification"}, headers=student_headers)
    assert note_write.status_code == 403

    deck_write = client.put(f"/api/v1/decks/{deck_id}", json={"name": "Essai"}, headers=student_headers)
    assert deck_write.status_code == 403

    card_add = client.post(f"/api/v1/decks/{deck_id}/cards", json={"front": "Q2", "back": "R2"}, headers=student_headers)
    assert card_add.status_code == 403

    # 8. Teacher adds content (live sync verification)
    with app.app_context():
        new_card = Flashcard(deck_id=deck_id, front="Q2 - Sync", back="R2 - Sync")
        db.session.add(new_card)
        db.session.commit()
        new_card_id = new_card.id

    # Verify student automatically sees the new card
    study_resp = client.get(f"/api/v1/decks/{deck_id}/study", headers=student_headers)
    assert study_resp.status_code == 200
    cards = study_resp.json
    assert any(c["id"] == new_card_id for c in cards)

    # 9. Assignment progress automatic updates
    # Teacher creates an assignment
    asgn_resp = client.post(f"/api/v1/classes/{class_id}/assignments", json={
        "binder_id": binder_id,
        "title": "Revision Devoir",
        "due_date": (datetime.utcnow() + timedelta(days=2)).isoformat()
    }, headers=auth_headers)
    assert asgn_resp.status_code == 201

    # Student answers a card
    answer_resp = client.post(f"/api/v1/decks/{deck_id}/study/answer/{card_id}", json={"score": 4}, headers=student_headers)
    assert answer_resp.status_code == 200

    # Verify assignment progress has updated
    mine_resp = client.get("/api/v1/assignments/mine", headers=student_headers)
    assert mine_resp.status_code == 200
    asgn_prog = [a for a in mine_resp.json if a["binder_id"] == binder_id]
    assert len(asgn_prog) == 1
    assert asgn_prog[0]["my_cards_reviewed"] == 1

    # 10. Verify class materials progress endpoint
    materials_progress_resp = client.get(f"/api/v1/classes/{class_id}/materials/progress", headers=auth_headers)
    assert materials_progress_resp.status_code == 200
    progress_data = materials_progress_resp.json
    assert len(progress_data) == 1
    student_prog = progress_data[0]
    assert student_prog["username"] == "student_follow"
    assert len(student_prog["binders_progress"]) == 1
    binder_prog = student_prog["binders_progress"][0]
    assert binder_prog["binder_id"] == binder_id
    assert binder_prog["binder_name"] == "Classeur Biologie"
    assert binder_prog["cards_reviewed"] == 1
    assert binder_prog["total_cards"] == 2
