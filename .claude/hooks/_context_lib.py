"""Bibliotheque partagee : mesure du remplissage de contexte et fraicheur de
PASSATION.md. Utilisee par stop_gate.py, contexte_precompact.py et
session_start_resume.py — un seul endroit pour cette logique (cf. CLAUDE.md,
"une regle un seul endroit").
"""
import json
import os
import pathlib

SEUIL = float(os.environ.get("CLAUDE_SEUIL_PASSATION", "0.90"))
# Fenetre de contexte du modele en tokens. Sonnet 5 : ~200k au moment de
# l'ecriture de ce hook — a ajuster via la variable d'env si le modele
# change ou si l'estimation s'avere fausse en pratique.
FENETRE = int(os.environ.get("CLAUDE_FENETRE_CONTEXTE", "200000"))

RACINE = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
PASSATION = RACINE / "PASSATION.md"
SENTINELLE = RACINE / ".claude" / "state" / "seuil-atteint"


def remplissage(chemin_transcript: str | None) -> float:
    """Taux de remplissage du contexte a partir du dernier message assistant
    du transcript (somme des tokens d'usage / FENETRE)."""
    if not chemin_transcript or not os.path.exists(chemin_transcript):
        return 0.0
    dernier = None
    try:
        with open(chemin_transcript, encoding="utf-8") as f:
            for ligne in f:
                try:
                    e = json.loads(ligne)
                except ValueError:
                    continue
                u = (e.get("message") or {}).get("usage")
                if u:
                    dernier = u
    except OSError:
        return 0.0
    if not dernier:
        return 0.0
    total = sum(
        dernier.get(k, 0)
        for k in (
            "input_tokens",
            "cache_read_input_tokens",
            "cache_creation_input_tokens",
            "output_tokens",
        )
    )
    return total / FENETRE


def fraiche(minutes: int = 10) -> bool:
    import datetime

    if not PASSATION.exists():
        return False
    age = datetime.datetime.now().timestamp() - PASSATION.stat().st_mtime
    return age < minutes * 60
