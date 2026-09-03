#!/usr/bin/env python3
"""PreToolUse hook (Write|Edit|MultiEdit) — garde TDD, active a partir de la phase 3.

Refuse l'ecriture d'un fichier de production si le fichier de test
correspondant n'existe pas, ou si son horodatage de derniere modification
est anterieur a celui du fichier de production (signe que le test n'a pas
ete touche dans ce cycle). Liste blanche : .claude/tdd-exempt.txt.
"""
import fnmatch
import json
import os
import pathlib
import re
import sys

RACINE = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
ETAT = RACINE / "ETAT.md"
EXEMPT_FILE = RACINE / ".claude" / "tdd-exempt.txt"
PHASE_RE = re.compile(r"^Phase:\s*(\d+)\s*$", re.M)

BACKEND_PROD_DIRS = ("app/dao/", "app/services/", "app/api/", "app/schemas/", "app/models/")
WEB_PROD_DIRS = ("src/stores/", "src/composables/", "src/components/", "src/views/", "src/services/")


def phase_courante() -> int | None:
    if not ETAT.exists():
        return None
    m = PHASE_RE.search(ETAT.read_text(encoding="utf-8"))
    return int(m.group(1)) if m else None


def is_exempt(rel_path: str) -> bool:
    if not EXEMPT_FILE.exists():
        return False
    for line in EXEMPT_FILE.read_text(encoding="utf-8").splitlines():
        pattern = line.strip()
        if not pattern or pattern.startswith("#"):
            continue
        if fnmatch.fnmatch(rel_path, pattern):
            return True
    return False


def is_production_code(rel_path: str) -> bool:
    norm = rel_path.replace("\\", "/")
    if norm.startswith("backend/"):
        sub = norm[len("backend/"):]
        if not sub.endswith(".py"):
            return False
        return any(sub.startswith(d) for d in BACKEND_PROD_DIRS)
    if norm.startswith("web/"):
        sub = norm[len("web/"):]
        if not sub.endswith((".vue", ".ts", ".js")):
            return False
        if sub.endswith((".spec.ts", ".test.ts", ".spec.js", ".test.js")):
            return False
        return any(sub.startswith(d) for d in WEB_PROD_DIRS)
    return False


def find_test_file(rel_path: str) -> pathlib.Path | None:
    norm = rel_path.replace("\\", "/")
    stem = pathlib.Path(norm).stem
    if norm.startswith("backend/"):
        search_root = RACINE / "backend" / "tests"
        if not search_root.exists():
            return None
        # Convention reelle du depot : certains services testes sous un nom sans
        # le suffixe "_service" (focus_service.py -> test_focus.py), ou sous un
        # nom de fichier plus specifique (stats_service.py -> test_stats_dashboard.py,
        # test_stats_binder.py). Tente le nom exact d'abord ; si plusieurs fichiers
        # matchent le fallback substring (large, sur stem et sa variante raccourcie),
        # retient le plus recemment modifie -- le plus susceptible d'etre celui
        # que le cycle rouge-vert en cours vient de toucher.
        candidates = [stem]
        for suffix in ("_service", "_schema", "_dao"):
            if stem.endswith(suffix):
                candidates.append(stem[: -len(suffix)])
        for cand in candidates:
            for p in search_root.rglob(f"test_{cand}.py"):
                return p
        matches: list[pathlib.Path] = []
        for cand in candidates:
            for p in search_root.rglob(f"*{cand}*.py"):
                if p.name.startswith("test_") and p not in matches:
                    matches.append(p)
        if not matches:
            return None
        return max(matches, key=lambda p: p.stat().st_mtime)
    if norm.startswith("web/"):
        candidates_roots = [RACINE / "web" / "tests", RACINE / "web" / "tests-e2e"]
        targets = {f"{stem}{ext}" for ext in (".spec.ts", ".test.ts", ".spec.js", ".test.js")}
        for root in candidates_roots:
            if not root.exists():
                continue
            # os.walk (pas Path.rglob) : rglob matche via fnmatch, insensible a la
            # casse sous Windows/NTFS -- "Binders.vue" matchait a tort le mauvais
            # fichier ("binders.spec.ts", store, au lieu de "Binders.spec.ts", vue)
            # des que les deux coexistent. os.walk renvoie les noms tels quels sur
            # le disque, comparables en casse exacte.
            for dirpath, _dirnames, filenames in os.walk(root):
                for name in filenames:
                    if name in targets:
                        return pathlib.Path(dirpath) / name
        return None
    return None


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

    phase = phase_courante()
    if phase is None or phase < 3:
        sys.exit(0)

    abs_path = (payload.get("tool_input", {}) or {}).get("file_path", "") or ""
    if not abs_path:
        sys.exit(0)

    try:
        rel_path = str(pathlib.Path(abs_path).resolve().relative_to(RACINE.resolve())).replace("\\", "/")
    except ValueError:
        sys.exit(0)

    if not is_production_code(rel_path) or is_exempt(rel_path):
        sys.exit(0)

    test_file = find_test_file(rel_path)
    if test_file is None:
        deny(
            f"⛔ Ecriture refusee (tdd_guard, phase {phase}) : aucun fichier de "
            f"test trouve pour {rel_path}. Le test precede le code — ecris-le "
            f"d'abord (skill cycle-tdd), ou ajoute une exemption justifiee dans "
            f".claude/tdd-exempt.txt si ce fichier est du pur visuel."
        )

    prod_file = RACINE / rel_path
    if prod_file.exists():
        try:
            if test_file.stat().st_mtime < prod_file.stat().st_mtime:
                deny(
                    f"⛔ Ecriture refusee (tdd_guard, phase {phase}) : le test "
                    f"{test_file.relative_to(RACINE)} n'a pas ete modifie depuis "
                    f"le dernier changement de {rel_path}. Modifie le test "
                    f"d'abord (rouge), puis le code (vert)."
                )
        except OSError:
            pass

    sys.exit(0)


if __name__ == "__main__":
    main()
