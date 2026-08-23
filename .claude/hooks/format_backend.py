#!/usr/bin/env python3
"""PostToolUse hook (Write|Edit|MultiEdit) — formatage auto du backend Python.

Sur tout fichier backend/**.py touche : `ruff check --fix` puis `ruff format`.
Non bloquant : une erreur ruff est juste signalee, elle n'annule pas l'ecriture
deja faite.
"""
import json
import pathlib
import subprocess
import sys

RACINE = pathlib.Path(__file__).resolve().parents[2]


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if payload.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)

    path = (payload.get("tool_input", {}) or {}).get("file_path", "") or ""
    if not path or not path.endswith(".py"):
        sys.exit(0)

    norm = path.replace("\\", "/")
    if "/backend/" not in f"/{norm}" and not norm.startswith("backend/"):
        sys.exit(0)
    if "/migrations/" in norm or "/scratch/" in norm:
        sys.exit(0)

    file_path = pathlib.Path(path)
    if not file_path.exists():
        sys.exit(0)

    messages = []
    for args in (["ruff", "check", "--fix", str(file_path)], ["ruff", "format", str(file_path)]):
        try:
            result = subprocess.run(args, capture_output=True, text=True, timeout=30, cwd=RACINE / "backend")
        except FileNotFoundError:
            sys.exit(0)  # ruff pas installe : ne bloque rien, silencieux
        except Exception:
            continue
        if result.returncode not in (0, 1):
            messages.append(f"{' '.join(args[:2])} a echoue : {result.stderr.strip()[:300]}")

    if messages:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": "⚠️ format_backend : " + " | ".join(messages),
            }
        }))
    sys.exit(0)


if __name__ == "__main__":
    main()
