#!/usr/bin/env python3
"""SessionStart (matcher "clear") — reprise apres /clear.

Reinjecte PASSATION.md + ETAT.md et relance la prochaine action seule,
sans intervention. Complementaire de session_start.py (demarrage normal).
"""
import json
import os
import pathlib
import re
import sys

RACINE = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
PASSATION = RACINE / "PASSATION.md"
ETAT = RACINE / "ETAT.md"
WORKFLOW = RACINE / "workflow"
JOURNAL_WORKFLOW = WORKFLOW / "JOURNAL.md"
CHANTIER_RE = re.compile(r"^Chantier actif\s*:\s*(.+?)\s*$", re.M)


def chantier_actif() -> str | None:
    if not JOURNAL_WORKFLOW.exists():
        return None
    m = CHANTIER_RE.search(JOURNAL_WORKFLOW.read_text(encoding="utf-8"))
    if not m:
        return None
    valeur = m.group(1).strip()
    return None if valeur.lower() == "aucun" else valeur


def contexte_chantier(slug: str) -> str:
    dossier = WORKFLOW / slug
    context_path = dossier / "CONTEXT.md"
    plan_path = dossier / "PLAN.md"
    journal_path = dossier / "JOURNAL.md"
    context = context_path.read_text(encoding="utf-8") if context_path.exists() else "(absent)"
    plan = plan_path.read_text(encoding="utf-8") if plan_path.exists() else "(absent)"
    journal_tail = ""
    if journal_path.exists():
        lignes = journal_path.read_text(encoding="utf-8").splitlines()
        journal_tail = "\n".join(lignes[-10:])
    return (
        f"\n\n--- Chantier actif : {slug} ---\n"
        f"CONTEXT.md :\n{context}\n\n"
        f"PLAN.md :\n{plan}\n\n"
        f"JOURNAL.md (10 dernieres lignes) :\n{journal_tail}"
    )


def main() -> None:
    try:
        json.load(sys.stdin)
    except Exception:
        pass

    passation = PASSATION.read_text(encoding="utf-8") if PASSATION.exists() else ""
    etat = ETAT.read_text(encoding="utf-8") if ETAT.exists() else ""
    slug = chantier_actif()
    extra = contexte_chantier(slug) if slug else ""

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": f"{passation}\n\n---\n\n{etat}{extra}",
            "initialUserMessage": (
                "Reprends le travail. Lis la passation et ETAT.md ci-dessus, "
                "relis les fichiers listes en priorite, confirme en trois "
                "lignes ce que tu as compris de l'etat, puis execute la "
                "prochaine action indiquee — en TDD si la phase est >= 3, "
                "test d'abord."
            ),
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
