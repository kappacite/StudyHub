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

RACINE = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
ETAT = RACINE / "ETAT.md"
PHASE_RE = re.compile(r"^Phase:\s*(\d+)\s*$", re.M)


def git(*args: str) -> str:
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True, timeout=10, cwd=RACINE)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


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

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": contexte,
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
