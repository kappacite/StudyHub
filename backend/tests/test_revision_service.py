"""Tests unitaires purs de app.services.revision_service (fonctions libres, sans
Flask/DB) -- les tests d'intégration existants (test_revision.py,
test_revision_check_grade_split.py, test_revision_qcm.py) couvrent déjà le
comportement bout en bout via des requêtes HTTP ; ce fichier complète avec le
niveau le plus direct pour la logique pure ajoutée par revision-qcm-heterogene."""

from app.services.revision_service import GRADABLE_TYPES, check_answer


def test_qcm_rejoint_gradable_types():
    """revision-qcm-heterogene, Approche A : le QCM doit être révisable via le
    flux générique check_item_answer/grade_item, pas seulement via le passage
    scoré dédié (check_qcm_answer/answer_qcm_item, réservé à un ensemble
    homogène "qcm")."""
    assert "qcm" in GRADABLE_TYPES


QCM_PAYLOAD = {
    "question": "Capitale de la France ?",
    "options": [
        {"id": "a", "text": "Paris", "correct": True},
        {"id": "b", "text": "Lyon", "correct": False},
    ],
}


def test_check_answer_qcm_selection_correcte():
    assert check_answer("qcm", QCM_PAYLOAD, {"selected_option_ids": ["a"]}) is True


def test_check_answer_qcm_selection_incorrecte():
    assert check_answer("qcm", QCM_PAYLOAD, {"selected_option_ids": ["b"]}) is False


def test_check_answer_qcm_selection_partielle_rejetee():
    """Plusieurs bonnes réponses attendues : une sélection partielle est fausse
    (tout-ou-rien, même règle que _score_qcm_answer)."""
    payload = {
        "question": "Langages typés statiquement ?",
        "options": [
            {"id": "a", "text": "TypeScript", "correct": True},
            {"id": "b", "text": "Python", "correct": False},
            {"id": "c", "text": "Rust", "correct": True},
        ],
    }
    assert check_answer("qcm", payload, {"selected_option_ids": ["a"]}) is False
    assert check_answer("qcm", payload, {"selected_option_ids": ["a", "c"]}) is True


def test_check_answer_qcm_sans_selection():
    assert check_answer("qcm", QCM_PAYLOAD, {}) is False
