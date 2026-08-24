#!/usr/bin/env python3
"""Hook Stop unifie — porte de sortie + mecanique de passation de contexte.

Un seul hook Stop (remplace l'ancien commit_reminder.py, dont le
comportement de rappel non bloquant est repris ici en dernier recours).
Enchaine, dans l'ordre :
  1. Garde TDD (phase >= 3) : le diff en attente doit contenir au moins un
     fichier de test si du code de production a change.
  2. Tests : vitest local si web/src change, pytest via docker compose si
     backend/app change (et le conteneur tourne — sinon avertissement, pas
     de blocage : demarrer Docker au Stop serait plus surprenant qu'utile).
  3. Avertissements non bloquants : ETAT.md pas touche alors que du travail
     l'a ete, TODO/FIXME ajoute, zone documentee touchee sans doc a jour.
  4. Mesure du remplissage de contexte -> force la passation a 90 %.
  5. A defaut, rappel de commit non bloquant (comportement d'origine).

stop_hook_active : si vrai, on a deja bloque une fois ce cycle -> on ne
rebloque pas (evite la boucle infinie), on se contente d'avertir.
"""
import json
import os
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _context_lib as ctx  # noqa: E402

RACINE = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
ETAT = RACINE / "ETAT.md"
PHASE_RE = re.compile(r"^Phase:\s*(\d+)\s*$", re.M)


def phase_courante() -> int | None:
    if not ETAT.exists():
        return None
    m = PHASE_RE.search(ETAT.read_text(encoding="utf-8"))
    return int(m.group(1)) if m else None


def git(*args: str) -> str:
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15, cwd=RACINE)
        return r.stdout if r.returncode == 0 else ""
    except Exception:
        return ""


def fichiers_changes() -> list[str]:
    """Fichiers modifies/ajoutes, indexes ou non — relatifs a la racine, '/' partout."""
    porcelain = git("status", "--porcelain")
    out = []
    for line in porcelain.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip()
        if " -> " in path:  # rename
            path = path.split(" -> ", 1)[1]
        out.append(path.replace("\\", "/"))
    return out


def bloque(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(2)


def check_tdd_diff(fichiers: list[str], phase: int) -> str | None:
    if phase < 3:
        return None
    prod_touche = any(
        (f.startswith("backend/app/") and f.endswith(".py"))
        or (f.startswith("web/src/") and f.endswith((".vue", ".ts", ".js")))
        for f in fichiers
        if not f.endswith((".spec.ts", ".test.ts"))
    )
    if not prod_touche:
        return None
    test_touche = any(
        (f.startswith("backend/tests/") and f.endswith(".py"))
        or (("/tests/" in f or "/tests-e2e/" in f) and f.endswith((".spec.ts", ".test.ts")))
        for f in fichiers
    )
    if test_touche:
        return None
    return (
        "⛔ Stop refuse (stop_gate, phase >= 3) : du code de production a change "
        "sans qu'aucun fichier de test ne fasse partie du diff en attente. "
        "Cycle TDD incomplet — ajoute/modifie le test avant de t'arreter."
    )


def check_tests(fichiers: list[str]) -> tuple[str | None, list[str]]:
    """Retourne (message de blocage ou None, avertissements non bloquants)."""
    avertissements = []
    web_change = any(f.startswith("web/src/") and f.endswith((".vue", ".ts", ".js")) for f in fichiers)
    backend_change = any(f.startswith("backend/app/") and f.endswith(".py") for f in fichiers)

    if web_change:
        vitest = RACINE / "web" / "node_modules" / ".bin" / "vitest.cmd"
        if not vitest.exists():
            vitest = RACINE / "web" / "node_modules" / ".bin" / "vitest"
        if vitest.exists():
            try:
                r = subprocess.run(
                    [str(vitest), "run"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180,
                    cwd=RACINE / "web", shell=True,
                )
                if r.returncode != 0:
                    return (
                        "⛔ Stop refuse (stop_gate) : vitest est rouge.\n"
                        + (r.stdout + r.stderr)[-2000:]
                    ), avertissements
            except Exception as e:
                avertissements.append(f"vitest n'a pas pu etre execute : {e}")
        else:
            avertissements.append("web/src a change mais vitest est introuvable localement.")

    if backend_change:
        ps = git("-C", ".")  # noop pour forcer cwd coherent avant docker
        try:
            r = subprocess.run(
                ["docker", "compose", "ps", "--status", "running", "--format", "json", "backend"],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15, cwd=RACINE,
            )
            backend_up = bool(r.stdout.strip())
        except Exception:
            backend_up = False

        if backend_up:
            try:
                r = subprocess.run(
                    ["docker", "compose", "exec", "-T", "backend", "pytest"],
                    capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300, cwd=RACINE,
                )
                if r.returncode != 0:
                    return (
                        "⛔ Stop refuse (stop_gate) : pytest est rouge (docker compose exec backend).\n"
                        + (r.stdout + r.stderr)[-2000:]
                    ), avertissements
            except Exception as e:
                avertissements.append(f"pytest (docker) n'a pas pu etre execute : {e}")
        else:
            avertissements.append(
                "backend/app a change mais le conteneur 'backend' ne tourne pas — "
                "tests non verifies (demarrage automatique volontairement evite ici)."
            )

    return None, avertissements


def check_etat_frais(fichiers: list[str]) -> str | None:
    travail_reel = [f for f in fichiers if not f.startswith(".claude/") and f != "ETAT.md"]
    if not travail_reel:
        return None
    if "ETAT.md" in fichiers:
        return None
    dernier_commit_touche_etat = "ETAT.md" in git("show", "--name-only", "--format=", "HEAD")
    if dernier_commit_touche_etat:
        return None
    return (
        "ETAT.md n'a ete touche ni dans ce diff ni dans le dernier commit, "
        "alors que d'autres fichiers ont change — verifie qu'il reflete "
        "toujours la phase et la checklist reelles."
    )


def check_todo_fixme(fichiers: list[str]) -> str | None:
    diff = git("diff", "HEAD", "--unified=0", "--", *fichiers) if fichiers else ""
    hits = [
        line for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
        and re.search(r"\b(TODO|FIXME)\b", line)
        and not re.search(r"docs/audit|#\d+", line)
    ]
    if not hits:
        return None
    apercu = "\n".join(h[:120] for h in hits[:5])
    return f"TODO/FIXME ajoute(s) sans reference (docs/audit ou #issue) :\n{apercu}"


def check_doc_correlation(fichiers: list[str]) -> str | None:
    zones = {
        "diagrammes": lambda f: "Diagrams" in f,
        "composants UI": lambda f: "web/src/components/ui/" in f,
        "schema de donnees": lambda f: f.startswith("backend/app/models/"),
        "environnement/deploiement": lambda f: f in ("docker-compose.yml",) or f.startswith("backend/Dockerfile") or f.startswith("web/Dockerfile"),
    }
    touchees = [nom for nom, pred in zones.items() if any(pred(f) for f in fichiers)]
    if not touchees:
        return None
    if any(f.startswith("docs/") and f.endswith(".md") for f in fichiers):
        return None
    return (
        f"Zone(s) documentee(s) touchee(s) sans .md correspondant modifie : "
        f"{', '.join(touchees)}. A verifier (pas bloquant, la correlation est trop imprecise)."
    )


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    stop_hook_active = bool(payload.get("stop_hook_active"))
    fichiers = fichiers_changes()
    phase = phase_courante() or 1
    avertissements: list[str] = []

    if not stop_hook_active:
        msg = check_tdd_diff(fichiers, phase)
        if msg:
            bloque(msg)

        msg, av = check_tests(fichiers)
        avertissements.extend(av)
        if msg:
            bloque(msg)

        for check in (check_etat_frais, check_todo_fixme, check_doc_correlation):
            msg = check(fichiers)
            if msg:
                avertissements.append(msg)

    # --- Mecanique de passation de contexte (voir _context_lib) ---
    if not stop_hook_active:
        taux = ctx.remplissage(payload.get("transcript_path"))
        if taux < ctx.SEUIL:
            ctx.SENTINELLE.unlink(missing_ok=True)
        elif ctx.SENTINELLE.exists() and ctx.fraiche():
            ctx.SENTINELLE.unlink(missing_ok=True)
            print(json.dumps({
                "systemMessage": (
                    f"Contexte a {taux:.0%}. Passation ecrite. Tape /clear — "
                    "la reprise est automatique."
                )
            }))
            sys.exit(0)
        else:
            ctx.SENTINELLE.parent.mkdir(parents=True, exist_ok=True)
            ctx.SENTINELLE.touch()
            bloque(
                f"Contexte a {taux:.0%}, au-dessus du seuil de {ctx.SEUIL:.0%}. "
                "Termine le cycle TDD en cours s'il y en a un (vert + commit), "
                "puis ecris PASSATION.md (40 lignes max, format impose), "
                "archive-la dans docs/passations/, mets ETAT.md a jour, "
                "et arrete-toi. N'entame aucune nouvelle tache."
            )

    # --- Rappel de commit (comportement d'origine, non bloquant) ---
    porcelain = git("status", "--porcelain")
    changed_count = len(porcelain.strip().splitlines()) if porcelain.strip() else 0
    if changed_count:
        avertissements.append(
            f"{changed_count} fichier(s) non commite(s). Checklist CLAUDE.md — "
            "commit apres chaque modification (Conventional Commits) et mettre a jour "
            "docs/development_journal.md."
        )

    if avertissements:
        print(json.dumps({"systemMessage": "📝 " + " | ".join(avertissements)}))
    sys.exit(0)


if __name__ == "__main__":
    main()
