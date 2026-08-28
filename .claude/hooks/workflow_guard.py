#!/usr/bin/env python3
"""PreToolUse hook (Write|Edit|MultiEdit) — garde du workflow par chantiers.

Deux responsabilites :
1. Discipline de plan : une fois un chantier actif (workflow/JOURNAL.md),
   toute ecriture hors workflow/, .claude/, docs/, ETAT.md/PASSATION.md
   est refusee si le PLAN.md du chantier actif n'a plus de case non
   cochee (ou n'existe pas).
2. Porte d'ouverture : refuse un changement de "Chantier actif :" vers un
   nouveau chantier si un autre chantier est encore ouvert/en attente de
   merge (Statut ouvert|pr-ouverte), ou si main local n'est pas a jour
   avec origin/main.

Inactif (sys.exit(0) immediat) si aucun chantier n'est actif : aucun
effet sur le travail non migre vers ce systeme (ex. refonte UI phase 4).
"""
import json
import os
import pathlib
import re
import subprocess
import sys

RACINE = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
WORKFLOW = RACINE / "workflow"
JOURNAL_GLOBAL = WORKFLOW / "JOURNAL.md"
ACTIF_RE = re.compile(r"^Chantier actif\s*:\s*(.+?)\s*$", re.M)
STATUT_RE = re.compile(r"^Statut\s*:\s*(.+?)\s*$", re.M)

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


def lire_statut(slug: str) -> str | None:
    context = WORKFLOW / slug / "CONTEXT.md"
    if not context.exists():
        return None
    m = STATUT_RE.search(context.read_text(encoding="utf-8"))
    return m.group(1).strip() if m else None


def plan_a_des_taches_restantes(slug: str) -> bool:
    plan = WORKFLOW / slug / "PLAN.md"
    if not plan.exists():
        return False
    return "- [ ]" in plan.read_text(encoding="utf-8")


def chemin_relatif(abs_path: str) -> str | None:
    try:
        return str(
            pathlib.Path(abs_path).resolve().relative_to(RACINE.resolve())
        ).replace("\\", "/")
    except ValueError:
        return None


def chemin_autorise_sans_plan(rel_path: str) -> bool:
    if rel_path in ALLOW_FILES:
        return True
    return any(rel_path.startswith(p) for p in ALLOW_PREFIXES)


def git(*args: str) -> str:
    try:
        r = subprocess.run(
            ["git", *args], capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=15, cwd=RACINE,
        )
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def nouvelle_valeur_chantier_actif(tool_name: str, tool_input: dict) -> str | None:
    """Nouvelle valeur de 'Chantier actif :' visee par cette ecriture sur
    workflow/JOURNAL.md, ou None si l'ecriture ne touche pas cette ligne."""
    if tool_name == "Write":
        contenu = tool_input.get("content", "") or ""
    elif tool_name == "MultiEdit":
        contenu = "\n".join(
            (e.get("new_string", "") or "") for e in (tool_input.get("edits") or [])
        )
    elif tool_name == "Edit":
        contenu = tool_input.get("new_string", "") or ""
    else:
        return None
    m = ACTIF_RE.search(contenu)
    return m.group(1).strip() if m else None


def verifier_ouverture(nouveau_slug: str) -> str | None:
    """Message de refus, ou None si l'ouverture est autorisee."""
    if WORKFLOW.exists():
        for dossier in WORKFLOW.iterdir():
            if not dossier.is_dir():
                continue
            statut = lire_statut(dossier.name)
            if statut in ("ouvert", "pr-ouverte"):
                return (
                    f"le chantier '{dossier.name}' a le statut '{statut}' — "
                    f"il doit etre clos (PR mergee) avant d'ouvrir un "
                    f"nouveau chantier."
                )

    cible = WORKFLOW / nouveau_slug
    if not (cible / "CONTEXT.md").exists() or not (cible / "PLAN.md").exists():
        return (
            f"workflow/{nouveau_slug}/CONTEXT.md et PLAN.md doivent exister "
            f"avant de declarer ce chantier actif (skill gestion-chantier)."
        )

    git("fetch", "origin", "main", "--quiet")
    local_main = git("rev-parse", "main")
    origin_main = git("rev-parse", "origin/main")
    if local_main and origin_main and local_main != origin_main:
        return "main local n'est pas a jour avec origin/main — git pull d'abord."

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

    tool_name = payload.get("tool_name")
    if tool_name not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)

    tool_input = payload.get("tool_input", {}) or {}
    abs_path = tool_input.get("file_path", "") or ""
    if not abs_path:
        sys.exit(0)

    rel_path = chemin_relatif(abs_path)
    if rel_path is None:
        sys.exit(0)

    if rel_path == "workflow/JOURNAL.md":
        nouvelle_valeur = nouvelle_valeur_chantier_actif(tool_name, tool_input)
        if nouvelle_valeur is not None:
            ancienne_valeur = lire_chantier_actif() or "aucun"
            if nouvelle_valeur.lower() != "aucun" and nouvelle_valeur != ancienne_valeur:
                raison = verifier_ouverture(nouvelle_valeur)
                if raison:
                    deny(f"⛔ Ouverture de chantier refusee (workflow_guard) : {raison}")
        sys.exit(0)

    chantier = lire_chantier_actif()
    if chantier is None:
        sys.exit(0)

    if chemin_autorise_sans_plan(rel_path):
        sys.exit(0)

    if not plan_a_des_taches_restantes(chantier):
        deny(
            f"⛔ Ecriture refusee (workflow_guard) : le chantier actif "
            f"'{chantier}' n'a pas de workflow/{chantier}/PLAN.md avec au "
            f"moins une case non cochee. Ecris/complete le plan d'abord "
            f"(skill gestion-chantier) avant de toucher {rel_path}."
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
