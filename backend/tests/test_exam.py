import json
from app.models.binder import Binder
from app.models.deck import Deck
from app.models.flashcard import Flashcard
from app.models.note import Note
from app.models.quiz import Quiz, QuizQuestion
from app.models.exam import ExamSession
from app.extensions import db

def test_exam_flow(client, auth_headers, test_user, app):
    with app.app_context():
        # 1. Préparation des données d'étude pour l'examen (classeur, note, deck, flashcard, quiz)
        binder = Binder(user_id=test_user["id"], name="Classeur Pharmacie")
        db.session.add(binder)
        db.session.commit()
        binder_id = binder.id

        # Création d'une note et d'un quiz associé avec 1 question
        note = Note(user_id=test_user["id"], binder=binder, title="Note Pharmacopée", content="L'aspirine est un anti-inflammatoire.")
        db.session.add(note)
        db.session.commit()

        quiz = Quiz(note=note, user_id=test_user["id"])
        db.session.add(quiz)
        db.session.commit()

        q1 = QuizQuestion(
            quiz_id=quiz.id,
            question_text="Quelle est la classe thérapeutique de l'aspirine ?",
            options=[
                {"id": "a", "text": "Antibiotique", "correct": False},
                {"id": "b", "text": "Anti-inflammatoire", "correct": True},
                {"id": "c", "text": "Antidépresseur", "correct": False},
                {"id": "d", "text": "Anesthésique", "correct": False}
            ]
        )
        db.session.add(q1)

        # Création d'un deck et d'une flashcard
        deck = Deck(user_id=test_user["id"], name="Deck Aspirine", binder=binder)
        db.session.add(deck)
        db.session.commit()

        fc = Flashcard(deck_id=deck.id, front="Formule de l'aspirine", back="C9H8O4")
        db.session.add(fc)
        db.session.commit()

        fc_id = fc.id
        q1_id = q1.id

    # 2. Démarrer l'examen
    start_resp = client.post("/api/v1/exam/start", json={
        "binder_id": binder_id,
        "duration_minutes": 20,
        "include_flashcards": True,
        "include_qcm": True,
        "question_limit": 10
    }, headers=auth_headers)
    
    assert start_resp.status_code == 201
    exam_data = start_resp.json
    session_id = exam_data["id"]
    assert len(exam_data["items"]) == 2  # 1 flashcard + 1 QCM
    
    # Vérifier que les réponses sont bien masquées (triche évitée)
    qcm_item = next(item for item in exam_data["items"] if item["item_type"] == "qcm")
    fc_item = next(item for item in exam_data["items"] if item["item_type"] == "flashcard")
    
    assert fc_item["back"] == "C9H8O4"  # Visible pour auto-évaluation
    for opt in qcm_item["options"]:
        assert opt.get("correct") is None  # Masqué

    # 3. Récupérer la session d'examen (doit aussi masquer les réponses)
    get_resp = client.get(f"/api/v1/exam/{session_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json["completed_at"] is None
    
    # 4. Soumettre la réponse au QCM (Bonne réponse: b)
    ans_qcm_resp = client.post(
        f"/api/v1/exam/{session_id}/questions/{qcm_item['id']}/answer",
        json={"answer": "b"},
        headers=auth_headers
    )
    assert ans_qcm_resp.status_code == 200
    assert ans_qcm_resp.json["is_correct"] is True

    # 5. Soumettre la réponse à la flashcard (Auto-évaluation: Incorrecte)
    ans_fc_resp = client.post(
        f"/api/v1/exam/{session_id}/questions/{fc_item['id']}/answer",
        json={"answer": "incorrect"},
        headers=auth_headers
    )
    assert ans_fc_resp.status_code == 200
    assert ans_fc_resp.json["is_correct"] is False

    # 6. Finaliser l'examen (1 correct sur 2 => 50% de réussite)
    complete_resp = client.post(f"/api/v1/exam/{session_id}/complete", headers=auth_headers)
    assert complete_resp.status_code == 200
    result_data = complete_resp.json
    
    assert result_data["score_pct"] == 50.0
    assert result_data["qcm_score"] == 100.0
    assert result_data["flashcard_score"] == 0.0
    assert result_data["completed_at"] is not None
    
    # Vérifier que les réponses sont désormais révélées
    fc_item_res = next(item for item in result_data["items"] if item["item_type"] == "flashcard")
    assert fc_item_res["back"] == "C9H8O4"  # Révélé !

    # 7. Tenter de soumettre une réponse après la complétion (doit échouer)
    fail_ans_resp = client.post(
        f"/api/v1/exam/{session_id}/questions/{fc_item['id']}/answer",
        json={"answer": "correct"},
        headers=auth_headers
    )
    assert fail_ans_resp.status_code == 403

def test_exam_snapshot_immutability(client, auth_headers, test_user, app):
    # Vérifie que les modifications de flashcards en base après le début de l'examen n'impactent pas l'examen
    with app.app_context():
        binder = Binder(user_id=test_user["id"], name="Classeur Immuable")
        db.session.add(binder)
        db.session.commit()
        binder_id = binder.id

        deck = Deck(user_id=test_user["id"], name="Deck Immuable", binder=binder)
        db.session.add(deck)
        db.session.commit()

        fc = Flashcard(deck_id=deck.id, front="Original Front", back="Original Back")
        db.session.add(fc)
        db.session.commit()
        fc_id = fc.id

    # Lancement de l'examen
    start_resp = client.post("/api/v1/exam/start", json={"binder_id": binder_id}, headers=auth_headers)
    assert start_resp.status_code == 201
    session_id = start_resp.json["id"]

    # Modification de la flashcard originale en DB
    with app.app_context():
        card = db.session.get(Flashcard, fc_id)
        card.front = "Modified Front"
        card.back = "Modified Back"
        db.session.commit()

    # Finalisation de l'examen
    complete_resp = client.post(f"/api/v1/exam/{session_id}/complete", headers=auth_headers)
    result_data = complete_resp.json
    
    fc_item_res = result_data["items"][0]
    # Doit contenir les valeurs d'origine figées dans le snapshot
    assert fc_item_res["front"] == "Original Front"
    assert fc_item_res["back"] == "Original Back"

def test_exam_user_isolation(client, auth_headers, test_user, app):
    # Créer un classeur pour un autre utilisateur
    with app.app_context():
        other_binder = Binder(user_id=999, name="Autre Classeur")
        db.session.add(other_binder)
        db.session.commit()
        other_binder_id = other_binder.id

    # Essayer de démarrer un examen dessus (doit échouer)
    start_resp = client.post("/api/v1/exam/start", json={"binder_id": other_binder_id}, headers=auth_headers)
    assert start_resp.status_code == 403
