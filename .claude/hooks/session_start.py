#!/usr/bin/env python3
"""SessionStart (demarrage normal / resume) — injecte branche, statut git et
ETAT.md. Complementaire de session_start_resume.py (matcher "clear").
"""
import json
import os
import pathlib
import re
import subprocess
import sys

RACINE = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
ETAT = RACINE / "ETAT.md"
PHASE_RE = re.compile(r"^Phase:\s*(\d+)\s*$", re.M)
WORKFLOW = RACINE / "workflow"
JOURNAL_WORKFLOW = WORKFLOW / "JOURNAL.md"
CHANTIER_RE = re.compile(r"^Chantier actif\s*:\s*(.+?)\s*$", re.M)


def git(*args: str) -> str:
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10, cwd=RACINE)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


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

    branche = git("branch", "--show-current") or "(detachee)"
    statut = git("status", "--short") or "(arbre propre)"
    etat = ETAT.read_text(encoding="utf-8") if ETAT.exists() else "(ETAT.md absent)"

    m = PHASE_RE.search(etat) if ETAT.exists() else None
    phase = int(m.group(1)) if m else None

    contexte = (
        f"Branche : {branche}\n"
        f"git status --short :\n{statut}\n\n"
        f"ETAT.md :\n{etat}"
    )
    if phase is not None and phase >= 4:
        contexte += (
            "\n\n(Phase 4 active : verifie la section 'Ecrans migrés' d'ETAT.md "
            "ci-dessus pour la liste des ecrans restants.)"
        )

    slug = chantier_actif()
    if slug:
        contexte += contexte_chantier(slug)

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": contexte,
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
