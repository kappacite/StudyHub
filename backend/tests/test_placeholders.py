import pytest
from app.utils.placeholder_parser import extract_placeholders_from_text
from app.models.study_session import StudySession
from app.extensions import db

def test_placeholder_parsing_logic():
    content = (
        "Le chat {{trou::mange}} la souris.\n"
        "{{qcm::Qui a écrit Les Misérables ?::Zola|*Victor Hugo*|Maupassant}}\n"
        "{{ordre::Cycle de l'eau::Évaporation > Condensation > Précipitation}}\n"
        "{{assoc::Capitales::France=Paris | Espagne=Madrid}}\n"
        "{{vf::La Terre est plate::Faux::La Terre est ronde.}}\n"
        "[La PVM]{def:Python Virtual Machine, exécute le bytecode.}"
    )

    placeholders = extract_placeholders_from_text(content, note_id=1)

    assert len(placeholders) == 6

    # 1. Trou
    assert placeholders[0]["type"] == "trou"
    assert "Le chat [...] la souris." in placeholders[0]["front"]
    assert placeholders[0]["back"] == "mange"

    # 2. QCM
    assert placeholders[1]["type"] == "qcm"
    assert "Qui a écrit Les Misérables ?" in placeholders[1]["front"]
    assert placeholders[1]["back"] == "Victor Hugo"

    # 3. Ordre
    assert placeholders[2]["type"] == "ordre"
    assert "Cycle de l'eau" in placeholders[2]["front"]
    assert placeholders[2]["back"] == "Évaporation > Condensation > Précipitation"

    # 4. Assoc
    assert placeholders[3]["type"] == "assoc"
    assert "Capitales" in placeholders[3]["front"]
    assert placeholders[3]["back"] == "France=Paris | Espagne=Madrid"

    # 5. VF
    assert placeholders[4]["type"] == "vf"
    assert "La Terre est plate" in placeholders[4]["front"]
    assert "Faux" in placeholders[4]["back"]
    assert "La Terre est ronde" in placeholders[4]["back"]

    # 6. Def
    assert placeholders[5]["type"] == "def"
    assert "La PVM" in placeholders[5]["front"]
    assert "Python Virtual Machine" in placeholders[5]["back"]


def test_review_card_direct_api(client, auth_headers):
    # 1. Créer un deck réel + une carte (plus de deck fantôme auto).
    deck_resp = client.post("/api/v1/decks", json={
        "name": "Notes Physiques", "description": "Formules"
    }, headers=auth_headers)
    deck_id = deck_resp.json["id"]
    card_resp = client.post(f"/api/v1/decks/{deck_id}/cards", json={
        "front": "Définition : F=ma", "back": "La formule de la force"
    }, headers=auth_headers)
    assert card_resp.status_code == 201
    card_id = card_resp.json["id"]

    # 2. Réviser la carte via l'API globale PATCH
    review_data = {"score": 4}
    response = client.patch(f"/api/v1/flashcards/{card_id}/review", json=review_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json["interval"] > 0

    # 3. Vérifier qu'une session d'étude a été enregistrée
    with client.application.app_context():
        session = db.session.query(StudySession).filter_by(flashcard_id=card_id).first()
        assert session is not None
        assert session.grade == 4
        assert session.module == "flashcard"
