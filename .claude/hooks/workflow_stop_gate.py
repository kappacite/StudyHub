#!/usr/bin/env python3
"""Hook Stop — garde du workflow par chantiers (complementaire, independant
de stop_gate.py : ne le modifie pas, s'execute en plus).

Actif seulement si workflow/JOURNAL.md declare un chantier actif. Regle
unique bloquante : si des fichiers "reels" (hors workflow/, .claude/,
docs/, ETAT.md, PASSATION.md — meme liste que ALLOW_PREFIXES/ALLOW_FILES
dans workflow_guard.py) sont en attente (git status --porcelain
--untracked-files=all, pour ne pas rater un dossier workflow/<slug>/
encore entierement untracked) sans que workflow/<slug>/JOURNAL.md ne
fasse partie de ce meme diff ni du dernier commit, refuse de s'arreter —
force a journaliser le travail reel avant de committer/s'arreter. Tant
que rien de reel n'est en attente, aucune verification n'est necessaire
(un chantier au tree propre respecte deja "committer regulierement").
"""
import json
import os
import pathlib
import re
import subprocess
import sys

RACINE = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
JOURNAL_GLOBAL = RACINE / "workflow" / "JOURNAL.md"
ACTIF_RE = re.compile(r"^Chantier actif\s*:\s*(.+?)\s*$", re.M)

# Doit rester identique a ALLOW_PREFIXES/ALLOW_FILES dans workflow_guard.py :
# ce que le guard considere comme routine/exempt de plan ne doit pas non
# plus etre considere comme "travail reel" exigeant une entree de journal.
ALLOW_PREFIXES = ("workflow/", ".claude/", "docs/")
ALLOW_FILES = ("ETAT.md", "PASSATION.md")


def lire_chantier_actif() -> str | None:
    if not JOURNAL_GLOBAL.exists():
        return None
    m = ACTIF_RE.search(JOURNAL_GLOBAL.read_text(encoding="utf-8"))
    if not m:
        return None
    valeur = m.group(1).strip()
    return None if valeur.lower() == "aucun" else valeur


def git(*args: str) -> str:
    try:
        r = subprocess.run(
            ["git", *args], capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=15, cwd=RACINE,
        )
        return r.stdout if r.returncode == 0 else ""
    except Exception:
        return ""


def fichiers_en_attente() -> list[str]:
    porcelain = git("status", "--porcelain", "--untracked-files=all")
    out = []
    for line in porcelain.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        out.append(path.replace("\\", "/"))
    return out


def bloque(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(2)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if bool(payload.get("stop_hook_active")):
        sys.exit(0)

    chantier = lire_chantier_actif()
    if chantier is None:
        sys.exit(0)

    fichiers = fichiers_en_attente()
    hors_workflow = [
        f for f in fichiers
        if f not in ALLOW_FILES and not any(f.startswith(p) for p in ALLOW_PREFIXES)
    ]
    if not hors_workflow:
        sys.exit(0)

    journal_chantier = f"workflow/{chantier}/JOURNAL.md"
    if journal_chantier in fichiers:
        sys.exit(0)

    dernier_commit = git("show", "--name-only", "--format=", "HEAD")
    if journal_chantier in [l.strip().replace("\\", "/") for l in dernier_commit.splitlines()]:
        sys.exit(0)

    apercu = ", ".join(hors_workflow[:3]) + ("…" if len(hors_workflow) > 3 else "")
    bloque(
        f"⛔ Stop refuse (workflow_stop_gate) : des fichiers de travail reel "
        f"sont en attente ({apercu}) sans que {journal_chantier} ne soit "
        f"dans le meme diff ni dans le dernier commit. Journalise avant de "
        f"committer/t'arreter."
    )


if __name__ == "__main__":
    main()
