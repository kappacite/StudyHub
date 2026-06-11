import json
from unittest.mock import patch
from app.models.binder import Binder
from app.models.note import Note
from app.models.deck import Deck
from app.models.quiz import Quiz, QuizQuestion
from app.extensions import db

@patch("app.services.ai_service.AIService.generate_quiz")
def test_quiz_flow(mock_generate_quiz, client, auth_headers, test_user, app):
    # Mock de la réponse de l'IA pour générer 2 questions
    mock_generate_quiz.return_value = [
        {
            "question": "Quelle est la capitale de la France ?",
            "options": [
                {"id": "a", "text": "Londres", "correct": False},
                {"id": "b", "text": "Paris", "correct": True},
                {"id": "c", "text": "Berlin", "correct": False},
                {"id": "d", "text": "Madrid", "correct": False}
            ]
        },
        {
            "question": "Combien font 2 + 2 ?",
            "options": [
                {"id": "a", "text": "3", "correct": False},
                {"id": "b", "text": "4", "correct": True},
                {"id": "c", "text": "5", "correct": False},
                {"id": "d", "text": "22", "correct": False}
            ]
        }
    ]

    with app.app_context():
        # 1. Créer une note
        binder = Binder(user_id=test_user["id"], name="Classeur Test")
        db.session.add(binder)
        db.session.commit()
        
        note = Note(user_id=test_user["id"], binder_id=binder.id, title="Note Géographie", content="La capitale de la France est Paris. Deux plus deux font quatre.")
        db.session.add(note)
        db.session.commit()
        
        note_id = note.id
        
        # 2. Créer un deck
        deck = Deck(user_id=test_user["id"], name="Deck Quiz Mistakes")
        db.session.add(deck)
        db.session.commit()
        deck_id = deck.id

    # 3. Générer le QCM
    gen_resp = client.post("/api/v1/quizzes/generate", json={
        "note_id": note_id,
        "question_count": 2
    }, headers=auth_headers)
    
    assert gen_resp.status_code == 201
    quiz_data = gen_resp.json
    quiz_id = quiz_data["id"]
    assert quiz_data["note_id"] == note_id
    assert len(quiz_data["questions"]) == 2
    
    q1_id = quiz_data["questions"][0]["id"]
    q2_id = quiz_data["questions"][1]["id"]
    
    # 4. Récupérer la liste des QCM associés à une note
    list_resp = client.get(f"/api/v1/quizzes/note/{note_id}", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json) == 1
    assert list_resp.json[0]["id"] == quiz_id

    # 5. Récupérer un QCM par son ID
    get_resp = client.get(f"/api/v1/quizzes/{quiz_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json["id"] == quiz_id

    # 6. Répondre à la première question correctement (b)
    ans1_resp = client.post(
        f"/api/v1/quizzes/{quiz_id}/questions/{q1_id}/answer",
        json={"answer_id": "b"},
        headers=auth_headers
    )
    assert ans1_resp.status_code == 200
    assert ans1_resp.json["user_answer_id"] == "b"

    # 7. Répondre à la deuxième question faussement (a)
    ans2_resp = client.post(
        f"/api/v1/quizzes/{quiz_id}/questions/{q2_id}/answer",
        json={"answer_id": "a"},
        headers=auth_headers
    )
    assert ans2_resp.status_code == 200
    assert ans2_resp.json["user_answer_id"] == "a"

    # 8. Compléter le QCM (Score attendu: 50%)
    complete_resp = client.post(f"/api/v1/quizzes/{quiz_id}/complete", headers=auth_headers)
    assert complete_resp.status_code == 200
    assert complete_resp.json["score_pct"] == 50.0
    assert complete_resp.json["completed_at"] is not None

    # 9. Tenter de modifier une réponse après complétion (doit échouer)
    fail_ans_resp = client.post(
        f"/api/v1/quizzes/{quiz_id}/questions/{q2_id}/answer",
        json={"answer_id": "b"},
        headers=auth_headers
    )
    assert fail_ans_resp.status_code == 403

    # 10. Créer des flashcards depuis les mauvaises réponses
    flash_resp = client.post(
        f"/api/v1/quizzes/{quiz_id}/create-flashcards",
        json={
            "deck_id": deck_id,
            "question_ids": [q1_id, q2_id]  # q1 est correct, q2 est faux
        },
        headers=auth_headers
    )
    assert flash_resp.status_code == 201
    created_cards = flash_resp.json
    # Seul q2 (faux) doit donner lieu à une flashcard
    assert len(created_cards) == 1
    assert created_cards[0]["front"] == "Combien font 2 + 2 ?"
    assert "4" in created_cards[0]["back"]

def test_quiz_unauthorized_access(client, auth_headers, test_user, app):
    # Création d'une note appartenant à un autre utilisateur
    with app.app_context():
        other_binder = Binder(user_id=999, name="Autre Classeur")
        db.session.add(other_binder)
        db.session.commit()
        
        other_note = Note(user_id=999, binder_id=other_binder.id, title="Note Secrète", content="Top secret")
        db.session.add(other_note)
        db.session.commit()
        other_note_id = other_note.id

    # Essayer de générer un quiz sur la note de l'autre (doit échouer)
    gen_resp = client.post("/api/v1/quizzes/generate", json={
        "note_id": other_note_id,
        "question_count": 5
    }, headers=auth_headers)
    assert gen_resp.status_code == 403
