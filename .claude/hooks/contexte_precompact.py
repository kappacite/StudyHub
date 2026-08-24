#!/usr/bin/env python3
"""PreCompact (matcher "auto") — ce projet coupe au lieu de compacter.

Filet de securite si le seuil interne de compaction est atteint avant celui
de stop_gate.py. Bloque sauf si PASSATION.md est deja fraiche (< 10 min) —
sinon une session bloquee en boucle par ce hook serait pire qu'une
compaction subie.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _context_lib as ctx  # noqa: E402


def main() -> None:
    try:
        json.load(sys.stdin)
    except Exception:
        pass

    if ctx.fraiche():
        sys.exit(0)

    print(json.dumps({
        "decision": "block",
        "reason": (
            "Compaction refusee : ce projet coupe au lieu de compacter. "
            "Ecris PASSATION.md (40 lignes max, format impose), archive-la "
            "dans docs/passations/, mets ETAT.md a jour, puis demande un /clear."
        ),
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
