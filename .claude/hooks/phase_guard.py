#!/usr/bin/env python3
"""PreToolUse hook (Edit|Write|MultiEdit) — audit en lecture seule (phase 2).

Tant que ETAT.md indique "Phase: 2", toute ecriture hors docs/audit/ est
refusee. C'est ce qui rend reelle la regle "aucune correction pendant
l'audit" et la restriction d'ecriture du subagent auditeur-securite.
"""
import json
import os
import pathlib
import re
import sys

RACINE = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
ETAT = RACINE / "ETAT.md"
PHASE_RE = re.compile(r"^Phase:\s*(\d+)\s*$", re.M)


def phase_courante() -> int | None:
    if not ETAT.exists():
        return None
    m = PHASE_RE.search(ETAT.read_text(encoding="utf-8"))
    return int(m.group(1)) if m else None


def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if payload.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)

    if phase_courante() != 2:
        sys.exit(0)

    path = (payload.get("tool_input", {}) or {}).get("file_path", "") or ""
    if not path:
        sys.exit(0)

    normalized = path.replace("\\", "/")
    docs_audit = "/docs/audit/" in f"/{normalized}" or normalized.startswith("docs/audit/")
    etat_md = normalized.endswith("/ETAT.md") or normalized == "ETAT.md"
    if docs_audit or etat_md:
        sys.exit(0)

    deny(
        f"⛔ Ecriture refusee (phase_guard) : ETAT.md indique la phase 2 "
        f"(revue technique, lecture seule). Seul docs/audit/ peut etre "
        f"modifie pendant cette phase — {path} est hors perimetre."
    )


if __name__ == "__main__":
    main()
