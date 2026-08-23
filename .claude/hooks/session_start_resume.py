#!/usr/bin/env python3
"""SessionStart (matcher "clear") — reprise apres /clear.

Reinjecte PASSATION.md + ETAT.md et relance la prochaine action seule,
sans intervention. Complementaire de session_start.py (demarrage normal).
"""
import json
import os
import pathlib
import sys

RACINE = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
PASSATION = RACINE / "PASSATION.md"
ETAT = RACINE / "ETAT.md"


def main() -> None:
    try:
        json.load(sys.stdin)
    except Exception:
        pass

    passation = PASSATION.read_text(encoding="utf-8") if PASSATION.exists() else ""
    etat = ETAT.read_text(encoding="utf-8") if ETAT.exists() else ""

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": f"{passation}\n\n---\n\n{etat}",
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
