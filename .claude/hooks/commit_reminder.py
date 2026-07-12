#!/usr/bin/env python3
"""Stop hook: when the working tree has uncommitted changes, gently remind to
commit (Conventional Commits) and update docs/development_journal.md.

Non-blocking and loop-safe: respects stop_hook_active and never forces a re-run.
"""
import json
import subprocess
import sys

try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)

# Avoid re-triggering if we already ran in this stop cycle.
if payload.get("stop_hook_active"):
    sys.exit(0)

try:
    out = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=5,
    )
except Exception:
    sys.exit(0)

if out.returncode != 0 or not out.stdout.strip():
    sys.exit(0)

changed = len(out.stdout.strip().splitlines())
print(json.dumps({
    "systemMessage": (
        f"📝 Rappel : {changed} fichier(s) non commités. Checklist CLAUDE.md — "
        "commit après chaque modification (Conventional Commits) et mettre à jour "
        "docs/development_journal.md."
    )
}))
sys.exit(0)
