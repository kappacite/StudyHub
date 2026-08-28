# Outillage workflow de chantiers (hooks + skill) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construire les hooks et la skill qui rendent mécanique le système de
suivi par chantiers (`workflow/`) déjà en place : discipline de plan, cycle de
vie git (branche dédiée, commit régulier journalisé, PR à la clôture, gate
d'ouverture), et injection de contexte au démarrage de session.

**Architecture:** Deux nouveaux hooks (`workflow_guard.py` en PreToolUse,
`workflow_stop_gate.py` en Stop), chacun inactif tant qu'aucun chantier n'est
actif (`workflow/JOURNAL.md`), donc sans effet sur le travail non migré
(refonte UI phase 4). Extension additive de `session_start.py`/
`session_start_resume.py`. Une skill `gestion-chantier` documente et exécute
la procédure (git checkout/pull/branch, `gh pr create`) que les hooks ne
peuvent que vérifier a posteriori, jamais orchestrer eux-mêmes.

**Tech Stack:** Python 3 stdlib uniquement (`json`, `pathlib`, `re`,
`subprocess`, `os`, `sys`) — même contrainte que les hooks existants
(`.claude/hooks/*.py`), aucune dépendance externe. `git` et `gh` CLI via
`subprocess`.

**Spec:** `docs/superpowers/specs/2026-08-28-workflow-chantiers-design.md`

## Global Constraints

- Un seul chantier actif à la fois, pointeur `Chantier actif : <slug>` en
  tête de `workflow/JOURNAL.md`, `aucun` si rien n'est ouvert.
- État de chaque chantier dans `workflow/<slug>/CONTEXT.md` : lignes
  `Statut : planifié|ouvert|pr-ouverte|clos`, `Branche : ...`, `PR : ...`.
- Aucun hook existant n'est réécrit en profondeur ; `session_start.py` et
  `session_start_resume.py` reçoivent uniquement des ajouts additifs.
- `git push` est interdit en toute circonstance dans ce dépôt
  (`.claude/hooks/guard_dangerous_commands.py` + `deny` de
  `settings.json`) — aucun hook de ce plan ne doit tenter de pousser ;
  la skill s'arrête et demande à l'utilisateur de le faire.
- Convention de nommage des branches de chantier : `feature/<slug>`
  (`CLAUDE.md` : branches `feature/*`/`fix/*`).
- Pas de dépendance externe ajoutée ; encodage `utf-8`, `errors="replace"`
  sur tous les `subprocess.run` (cohérent avec les hooks existants).
- Pas de suite pytest pour `.claude/hooks/` dans ce dépôt (vérifié :
  aucun test ne couvre ce dossier) — vérification par « drill » manuel
  (payload JSON via stdin, lecture de la sortie/code retour), même
  méthode que celle documentée dans `ETAT.md` phase 1 pour les hooks
  existants.

---

### Task 1: `workflow_guard.py` — discipline de plan + porte d'ouverture

**Files:**
- Create: `.claude/hooks/workflow_guard.py`

**Interfaces:**
- Consumes : rien (script autonome, lit `workflow/JOURNAL.md` et
  `workflow/<slug>/{CONTEXT,PLAN}.md` sur disque, lit stdin JSON du hook
  PreToolUse).
- Produces : rien consommé par une autre tâche de ce plan (les autres
  hooks ont leur propre copie de la logique de lecture, cf. Global
  Constraints — pas de module partagé, cohérent avec l'existant
  `phase_guard.py`/`tdd_guard.py`).

- [ ] **Step 1 : écrire le hook**

```python
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
```

- [ ] **Step 2 : drill — aucun chantier actif, écriture hors workflow/ autorisée**

Run (depuis la racine du dépôt, `workflow/JOURNAL.md` doit contenir
`Chantier actif : aucun` à ce stade — c'est le cas actuel) :

```bash
echo '{"tool_name": "Write", "tool_input": {"file_path": "web/src/views/Notes/Notes.vue"}}' | CLAUDE_PROJECT_DIR="$(pwd)" python .claude/hooks/workflow_guard.py; echo "exit: $?"
```

Expected: aucune sortie, `exit: 0`.

- [ ] **Step 3 : drill — chantier actif sans tâche restante, écriture bloquée**

```bash
mkdir -p /tmp/wf-drill && cd /tmp/wf-drill
mkdir -p workflow/test-slug
printf 'Chantier actif : test-slug\n' > workflow/JOURNAL.md
printf 'Statut : ouvert\n' > workflow/test-slug/CONTEXT.md
printf '# Plan\n- [x] tout fait\n' > workflow/test-slug/PLAN.md
echo '{"tool_name": "Write", "tool_input": {"file_path": "web/src/views/Notes/Notes.vue"}}' | CLAUDE_PROJECT_DIR="$(pwd)" python /path/vers/StudyHub/.claude/hooks/workflow_guard.py; echo "exit: $?"
```

(Remplacer `/path/vers/StudyHub` par le chemin réel du dépôt — le script
est invoqué depuis un dossier isolé pour ne pas polluer `workflow/` du
vrai dépôt pendant le drill.)

Expected: sortie JSON avec `"permissionDecision": "deny"` mentionnant
`test-slug` et `PLAN.md`, `exit: 0` (le hook renvoie toujours 0, c'est le
JSON qui porte le refus — cohérent avec `phase_guard.py`/`tdd_guard.py`).

- [ ] **Step 4 : drill — chantier actif avec tâche restante, écriture autorisée**

Même dossier `/tmp/wf-drill`, remplacer `PLAN.md` :

```bash
printf '# Plan\n- [ ] a faire\n' > workflow/test-slug/PLAN.md
echo '{"tool_name": "Write", "tool_input": {"file_path": "web/src/views/Notes/Notes.vue"}}' | CLAUDE_PROJECT_DIR="$(pwd)" python /path/vers/StudyHub/.claude/hooks/workflow_guard.py; echo "exit: $?"
```

Expected: aucune sortie, `exit: 0`.

- [ ] **Step 5 : drill — porte d'ouverture refusée si un autre chantier est ouvert**

Même dossier, ajouter un second chantier ouvert et tenter de basculer :

```bash
mkdir -p workflow/autre-slug
printf 'Statut : ouvert\n' > workflow/autre-slug/CONTEXT.md
printf '# Plan\n- [ ] x\n' > workflow/autre-slug/PLAN.md
mkdir -p workflow/nouveau-slug
printf 'Statut : planifie\n' > workflow/nouveau-slug/CONTEXT.md
printf '# Plan\n- [ ] x\n' > workflow/nouveau-slug/PLAN.md
echo '{"tool_name": "Edit", "tool_input": {"file_path": "workflow/JOURNAL.md", "old_string": "Chantier actif : test-slug", "new_string": "Chantier actif : nouveau-slug"}}' | CLAUDE_PROJECT_DIR="$(pwd)" python /path/vers/StudyHub/.claude/hooks/workflow_guard.py; echo "exit: $?"
```

Expected: `"permissionDecision": "deny"` mentionnant `autre-slug` et
`ouvert`.

- [ ] **Step 6 : drill — fermeture vers "aucun" toujours autorisée**

```bash
echo '{"tool_name": "Edit", "tool_input": {"file_path": "workflow/JOURNAL.md", "old_string": "Chantier actif : test-slug", "new_string": "Chantier actif : aucun"}}' | CLAUDE_PROJECT_DIR="$(pwd)" python /path/vers/StudyHub/.claude/hooks/workflow_guard.py; echo "exit: $?"
cd /path/vers/StudyHub
rm -rf /tmp/wf-drill
```

Expected: aucune sortie, `exit: 0`. Nettoyer le dossier de drill ensuite.

- [ ] **Step 7 : commit**

```bash
git add .claude/hooks/workflow_guard.py
git commit -m "feat(hooks): ajoute workflow_guard (discipline de plan + porte d'ouverture)"
```

---

### Task 2: `workflow_stop_gate.py` — journalisation forcée à l'arrêt

**Files:**
- Create: `.claude/hooks/workflow_stop_gate.py`

**Interfaces:**
- Consumes : rien (lit `workflow/JOURNAL.md` sur disque, stdin JSON du
  hook Stop, `git status --porcelain` / `git show`).
- Produces : rien.

- [ ] **Step 1 : écrire le hook**

```python
#!/usr/bin/env python3
"""Hook Stop — garde du workflow par chantiers (complementaire, independant
de stop_gate.py : ne le modifie pas, s'execute en plus).

Actif seulement si workflow/JOURNAL.md declare un chantier actif. Regle
unique bloquante : si des fichiers hors workflow/ sont en attente
(git status --porcelain) sans que workflow/<slug>/JOURNAL.md ne fasse
partie de ce meme diff ni du dernier commit, refuse de s'arreter — force
a journaliser le travail reel avant de committer/s'arreter. Tant que rien
de reel n'est en attente, aucune verification n'est necessaire (un
chantier au tree propre respecte deja "committer regulierement").
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
    porcelain = git("status", "--porcelain")
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
    hors_workflow = [f for f in fichiers if not f.startswith("workflow/")]
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
        f"⛔ Stop refuse (workflow_stop_gate) : des fichiers hors workflow/ "
        f"sont en attente ({apercu}) sans que {journal_chantier} ne soit "
        f"dans le meme diff ni dans le dernier commit. Journalise avant de "
        f"committer/t'arreter."
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 2 : drill — aucun chantier actif, hook silencieux**

Depuis la racine du vrai dépôt (`workflow/JOURNAL.md` = `Chantier actif :
aucun` actuellement) :

```bash
echo '{}' | CLAUDE_PROJECT_DIR="$(pwd)" python .claude/hooks/workflow_stop_gate.py; echo "exit: $?"
```

Expected: aucune sortie, `exit: 0`.

- [ ] **Step 3 : drill — chantier actif, fichier hors workflow en attente sans journal**

```bash
mkdir -p /tmp/wf-stop-drill/workflow/test-slug
cd /tmp/wf-stop-drill
git init -q
printf 'Chantier actif : test-slug\n' > workflow/JOURNAL.md
printf '# Journal\n' > workflow/test-slug/JOURNAL.md
git add -A && git commit -q -m init
echo "changement" >> workflow/JOURNAL.md
mkdir -p web/src
echo "changement" > web/src/fichier.ts
echo '{}' | CLAUDE_PROJECT_DIR="$(pwd)" python /path/vers/StudyHub/.claude/hooks/workflow_stop_gate.py; echo "exit: $?"
```

Expected: message sur stderr mentionnant `web/src/fichier.ts` et
`workflow/test-slug/JOURNAL.md`, `exit: 2`.

- [ ] **Step 4 : drill — même situation mais journal du chantier dans le diff en attente**

```bash
echo "entree" >> workflow/test-slug/JOURNAL.md
echo '{}' | CLAUDE_PROJECT_DIR="$(pwd)" python /path/vers/StudyHub/.claude/hooks/workflow_stop_gate.py; echo "exit: $?"
```

Expected: aucune sortie, `exit: 0`.

- [ ] **Step 5 : drill — stop_hook_active=true ne bloque jamais**

```bash
git add -A && git commit -q -m "wip sans journal"
echo "encore un changement" > web/src/autre.ts
echo '{"stop_hook_active": true}' | CLAUDE_PROJECT_DIR="$(pwd)" python /path/vers/StudyHub/.claude/hooks/workflow_stop_gate.py; echo "exit: $?"
cd /path/vers/StudyHub
rm -rf /tmp/wf-stop-drill
```

Expected: aucune sortie, `exit: 0`. Nettoyer le dossier de drill ensuite.

- [ ] **Step 6 : commit**

```bash
git add .claude/hooks/workflow_stop_gate.py
git commit -m "feat(hooks): ajoute workflow_stop_gate (journalisation forcee a l'arret)"
```

---

### Task 3: Extension de `session_start.py` — injection du chantier actif

**Files:**
- Modify: `.claude/hooks/session_start.py`

**Interfaces:**
- Consumes : rien de nouveau.
- Produces : rien consommé ailleurs (le format du texte injecté n'est
  pas contractuel pour d'autres tâches).

- [ ] **Step 1 : lire le fichier actuel pour connaître le point d'insertion exact**

Le fichier actuel (`.claude/hooks/session_start.py`, 59 lignes) construit
`contexte` puis l'imprime dans `main()`. Insertion : ajouter la lecture du
chantier actif juste après la lecture d'`ETAT.md`, et concaténer à
`contexte` avant le `print`.

- [ ] **Step 2 : ajouter les imports et fonctions, juste après le bloc `PHASE_RE`**

```python
WORKFLOW = RACINE / "workflow"
JOURNAL_WORKFLOW = WORKFLOW / "JOURNAL.md"
CHANTIER_RE = re.compile(r"^Chantier actif\s*:\s*(.+?)\s*$", re.M)


def chantier_actif() -> str | None:
    if not JOURNAL_WORKFLOW.exists():
        return None
    m = CHANTIER_RE.search(JOURNAL_WORKFLOW.read_text(encoding="utf-8"))
    if not m:
        return None
    valeur = m.group(1).strip()
    return None if valeur.lower() == "aucun" else valeur


def contexte_chantier(slug: str) -> str:
    dossier = WORKFLOW / slug
    context_path = dossier / "CONTEXT.md"
    plan_path = dossier / "PLAN.md"
    journal_path = dossier / "JOURNAL.md"
    context = context_path.read_text(encoding="utf-8") if context_path.exists() else "(absent)"
    plan = plan_path.read_text(encoding="utf-8") if plan_path.exists() else "(absent)"
    journal_tail = ""
    if journal_path.exists():
        lignes = journal_path.read_text(encoding="utf-8").splitlines()
        journal_tail = "\n".join(lignes[-10:])
    return (
        f"\n\n--- Chantier actif : {slug} ---\n"
        f"CONTEXT.md :\n{context}\n\n"
        f"PLAN.md :\n{plan}\n\n"
        f"JOURNAL.md (10 dernieres lignes) :\n{journal_tail}"
    )
```

- [ ] **Step 3 : brancher dans `main()`, juste avant le `print(json.dumps(...))`**

Remplacer :

```python
    if phase is not None and phase >= 4:
        contexte += (
            "\n\n(Phase 4 active : verifie la section 'Ecrans migrés' d'ETAT.md "
            "ci-dessus pour la liste des ecrans restants.)"
        )
```

par :

```python
    if phase is not None and phase >= 4:
        contexte += (
            "\n\n(Phase 4 active : verifie la section 'Ecrans migrés' d'ETAT.md "
            "ci-dessus pour la liste des ecrans restants.)"
        )

    slug = chantier_actif()
    if slug:
        contexte += contexte_chantier(slug)
```

- [ ] **Step 4 : drill — pas de chantier actif, comportement inchangé**

```bash
echo '{}' | CLAUDE_PROJECT_DIR="$(pwd)" python .claude/hooks/session_start.py | python -c "import json,sys; d=json.load(sys.stdin); print('Chantier actif' in d['hookSpecificOutput']['additionalContext'])"
```

Expected: `False` (le mot « Chantier actif » n'apparaît que si un
chantier est réellement actif — ici `workflow/JOURNAL.md` contient
`Chantier actif : aucun`, donc rien n'est injecté).

- [ ] **Step 5 : drill — chantier actif, contexte injecté**

```bash
cp workflow/JOURNAL.md /tmp/journal-backup.md
sed -i 's/Chantier actif : aucun/Chantier actif : editeur-notes-notation-ia/' workflow/JOURNAL.md
echo '{}' | CLAUDE_PROJECT_DIR="$(pwd)" python .claude/hooks/session_start.py | python -c "import json,sys; d=json.load(sys.stdin); c=d['hookSpecificOutput']['additionalContext']; print('editeur-notes-notation-ia' in c and 'NoteFeynman' in c)"
cp /tmp/journal-backup.md workflow/JOURNAL.md
rm /tmp/journal-backup.md
```

Expected: `True` (le `PLAN.md` du chantier `editeur-notes-notation-ia`
mentionne `NoteFeynman.vue`). Le fichier `workflow/JOURNAL.md` réel est
restauré à `Chantier actif : aucun` immédiatement après.

- [ ] **Step 6 : commit**

```bash
git add .claude/hooks/session_start.py
git commit -m "feat(hooks): injecte le chantier actif au demarrage de session"
```

---

### Task 4: Extension de `session_start_resume.py` — injection après `/clear`

**Files:**
- Modify: `.claude/hooks/session_start_resume.py`

**Interfaces:**
- Consumes : `chantier_actif()`/`contexte_chantier()` réimplémentées
  localement (même choix que Task 1-3 : pas de module partagé, cohérent
  avec l'existant).

- [ ] **Step 1 : ajouter les mêmes fonctions que Task 3, Step 2, en tête du fichier**

Après le bloc `PASSATION = ...` / `ETAT = ...` :

```python
WORKFLOW = RACINE / "workflow"
JOURNAL_WORKFLOW = WORKFLOW / "JOURNAL.md"
CHANTIER_RE = re.compile(r"^Chantier actif\s*:\s*(.+?)\s*$", re.M)


def chantier_actif() -> str | None:
    if not JOURNAL_WORKFLOW.exists():
        return None
    m = CHANTIER_RE.search(JOURNAL_WORKFLOW.read_text(encoding="utf-8"))
    if not m:
        return None
    valeur = m.group(1).strip()
    return None if valeur.lower() == "aucun" else valeur


def contexte_chantier(slug: str) -> str:
    dossier = WORKFLOW / slug
    context_path = dossier / "CONTEXT.md"
    plan_path = dossier / "PLAN.md"
    journal_path = dossier / "JOURNAL.md"
    context = context_path.read_text(encoding="utf-8") if context_path.exists() else "(absent)"
    plan = plan_path.read_text(encoding="utf-8") if plan_path.exists() else "(absent)"
    journal_tail = ""
    if journal_path.exists():
        lignes = journal_path.read_text(encoding="utf-8").splitlines()
        journal_tail = "\n".join(lignes[-10:])
    return (
        f"\n\n--- Chantier actif : {slug} ---\n"
        f"CONTEXT.md :\n{context}\n\n"
        f"PLAN.md :\n{plan}\n\n"
        f"JOURNAL.md (10 dernieres lignes) :\n{journal_tail}"
    )
```

Ajouter aussi `import re` en tête du fichier (absent actuellement).

- [ ] **Step 2 : brancher dans `main()`**

Remplacer :

```python
    passation = PASSATION.read_text(encoding="utf-8") if PASSATION.exists() else ""
    etat = ETAT.read_text(encoding="utf-8") if ETAT.exists() else ""

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": f"{passation}\n\n---\n\n{etat}",
```

par :

```python
    passation = PASSATION.read_text(encoding="utf-8") if PASSATION.exists() else ""
    etat = ETAT.read_text(encoding="utf-8") if ETAT.exists() else ""
    slug = chantier_actif()
    extra = contexte_chantier(slug) if slug else ""

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": f"{passation}\n\n---\n\n{etat}{extra}",
```

- [ ] **Step 3 : drill — pas de chantier actif, comportement inchangé**

```bash
echo '{}' | CLAUDE_PROJECT_DIR="$(pwd)" python .claude/hooks/session_start_resume.py | python -c "import json,sys; d=json.load(sys.stdin); print('Chantier actif' in d['hookSpecificOutput']['additionalContext'])"
```

Expected: `False`.

- [ ] **Step 4 : drill — chantier actif, contexte injecté**

```bash
cp workflow/JOURNAL.md /tmp/journal-backup.md
sed -i 's/Chantier actif : aucun/Chantier actif : backend-ensembles-heterogenes/' workflow/JOURNAL.md
echo '{}' | CLAUDE_PROJECT_DIR="$(pwd)" python .claude/hooks/session_start_resume.py | python -c "import json,sys; d=json.load(sys.stdin); c=d['hookSpecificOutput']['additionalContext']; print('backend-ensembles-heterogenes' in c and 'RevisionItem' in c)"
cp /tmp/journal-backup.md workflow/JOURNAL.md
rm /tmp/journal-backup.md
```

Expected: `True`.

- [ ] **Step 5 : commit**

```bash
git add .claude/hooks/session_start_resume.py
git commit -m "feat(hooks): injecte le chantier actif a la reprise apres /clear"
```

---

### Task 5: Enregistrer les deux nouveaux hooks dans `.claude/settings.json`

**Files:**
- Modify: `.claude/settings.json`

**Interfaces:**
- Consumes : `workflow_guard.py` (Task 1), `workflow_stop_gate.py` (Task 2).

- [ ] **Step 1 : ajouter `workflow_guard.py` au bloc `PreToolUse` existant (matcher `Write|Edit|MultiEdit`)**

Dans le tableau `hooks` de l'entrée `PreToolUse` dont le `matcher` vaut
`"Write|Edit|MultiEdit"`, ajouter un troisième élément après
`tdd_guard.py` :

```json
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/workflow_guard.py\""
          }
```

- [ ] **Step 2 : ajouter `workflow_stop_gate.py` au bloc `Stop` existant**

Dans le tableau `hooks` de l'entrée `Stop` (`matcher: ""`), ajouter un
second élément après `stop_gate.py` :

```json
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/workflow_stop_gate.py\""
          }
```

- [ ] **Step 3 : valider le JSON**

```bash
python -c "import json; json.load(open('.claude/settings.json', encoding='utf-8'))" && echo OK
```

Expected: `OK`.

- [ ] **Step 4 : drill de bout en bout — les deux hooks sont bien invoqués sans erreur**

```bash
echo '{"tool_name": "Write", "tool_input": {"file_path": "docs/test.md"}}' | CLAUDE_PROJECT_DIR="$(pwd)" python .claude/hooks/workflow_guard.py; echo "guard exit: $?"
echo '{}' | CLAUDE_PROJECT_DIR="$(pwd)" python .claude/hooks/workflow_stop_gate.py; echo "stop exit: $?"
```

Expected: `guard exit: 0`, `stop exit: 0` (aucun chantier actif
actuellement — comportement transparent confirmé une dernière fois après
l'enregistrement).

- [ ] **Step 5 : commit**

```bash
git add .claude/settings.json
git commit -m "chore(hooks): enregistre workflow_guard et workflow_stop_gate dans settings.json"
```

---

### Task 6: Skill `gestion-chantier`

**Files:**
- Create: `.claude/skills/gestion-chantier/SKILL.md`

**Interfaces:**
- Consumes : les 2 hooks (Task 1, 2) et les gabarits de fichiers déjà en
  usage réel dans `workflow/*/` (créés lors de la migration précédente).
- Produces : rien.

- [ ] **Step 1 : écrire la skill**

```markdown
---
name: gestion-chantier
description: >
  Procedure pour ouvrir, faire avancer et clore un chantier de developpement
  dans workflow/ — branche dediee, plan, journal, PR a la cloture. A charger
  des qu'on demarre, reprend, ou termine un chantier hors refonte UI.
---

# Gestion de chantier

Un chantier = un sous-dossier `workflow/<slug>/` avec `CONTEXT.md` (pourquoi/
comment), `PLAN.md` (checklist d'etapes) et `JOURNAL.md` (une entree par
action + id de commit). Un seul chantier actif a la fois, declare dans
`workflow/JOURNAL.md` (`Chantier actif : <slug>` ou `aucun`).

Deux hooks rendent la discipline mecanique :
- `workflow_guard.py` (PreToolUse) : bloque l'ecriture de code hors plan
  une fois un chantier actif, et bloque l'ouverture d'un nouveau chantier
  si un autre est encore ouvert/en attente de merge ou si `main` n'est pas
  a jour.
- `workflow_stop_gate.py` (Stop) : bloque l'arret si du travail reel est
  en attente sans mise a jour du journal du chantier.

**`git push` est interdit en toute circonstance dans ce depot** — a chaque
etape ci-dessous qui le demande, s'arreter et attendre que l'utilisateur
l'execute lui-meme.

## Ouvrir un chantier

1. Verifier qu'aucun chantier n'a `Statut : ouvert` ou `Statut :
   pr-ouverte` dans `workflow/*/CONTEXT.md` (le hook bloquera de toute
   facon a l'etape 6, autant le savoir avant de faire le travail).
2. `git status` (copie propre attendue), `git checkout main`,
   `git fetch origin main`, `git pull --ff-only origin main`.
3. `git checkout -b feature/<slug>`.
4. Creer `workflow/<slug>/CONTEXT.md` avec l'en-tete :
   ```
   Statut : ouvert
   Branche : feature/<slug>
   PR : (aucune)
   ```
   puis le reste en prose (Pourquoi / Comment / Dependances).
5. Brainstormer si la tache le justifie (skill
   `superpowers:brainstorming`), puis ecrire le vrai `workflow/<slug>/
   PLAN.md` (checklist `- [ ]`, une case = une tache atomique) et
   `workflow/<slug>/JOURNAL.md` (vide, premiere entree a l'etape suivante).
6. Declarer `Chantier actif : <slug>` dans `workflow/JOURNAL.md` (le hook
   `workflow_guard.py` verifie a ce moment les conditions d'ouverture).
7. Commit.

## Travailler un point

1. Prendre la premiere case non cochee de `PLAN.md` comme tache courante.
2. L'executer (TDD si le code de production est concerne, cf.
   `cycle-tdd` / `migration-ecran` selon le cas).
3. Ajouter une entree a `workflow/<slug>/JOURNAL.md` : description
   (choix technique/fonctionnel) + id de commit.
4. Cocher la case dans `PLAN.md`.
5. Ajouter une ligne courte a l'historique de `workflow/JOURNAL.md`
   (index global) : `- YYYY-MM-DD — [<slug>] <point> termine, commit
   <sha>. Prochain : <point suivant>.`
6. Commit (le hook Stop bloque si du travail reel reste en attente sans
   que le journal du chantier ne soit dans le meme diff/commit — committer
   le code et la mise a jour du journal ensemble evite tout blocage).

## Clore un chantier (toutes les cases de `PLAN.md` cochees)

1. Entree de cloture dans `workflow/<slug>/JOURNAL.md`.
2. Commit.
3. **Demander a l'utilisateur de pousser la branche** : indiquer
   explicitement `git push -u origin feature/<slug>` et attendre
   confirmation — ne jamais tenter cette commande soi-meme.
4. Une fois la branche poussee, ouvrir la PR (`gh pr create`, avec
   confirmation utilisateur prealable — action visible/partagee comme
   toute autre).
5. Mettre a jour `workflow/<slug>/CONTEXT.md` : `Statut : pr-ouverte`,
   `PR : #<numero>`.
6. Repasser `workflow/JOURNAL.md` a `Chantier actif : aucun`, ligne de
   cloture dans l'historique.
7. Commit.

## Constater une PR mergee

A verifier avant d'ouvrir le prochain chantier (etape 1 ci-dessus), ou
des que l'utilisateur signale le merge :

```bash
gh pr view <numero> --json state -q .state
```

Si `MERGED` : mettre a jour `workflow/<slug>/CONTEXT.md` : `Statut :
clos`. Commit.
```

- [ ] **Step 2 : vérifier que la skill est bien détectée**

```bash
test -f .claude/skills/gestion-chantier/SKILL.md && echo OK
```

Expected: `OK`.

- [ ] **Step 3 : commit**

```bash
git add .claude/skills/gestion-chantier/SKILL.md
git commit -m "docs(skill): ajoute gestion-chantier (procedure complete workflow/)"
```

---

### Task 7: Vérification finale de bout en bout

**Files:** aucune création/modification (vérification uniquement).

- [ ] **Step 1 : suite de tests existante non cassée**

```bash
cd web && npx vitest run 2>&1 | tail -20
```

Expected: tous les tests toujours verts (aucun fichier de production
touché par ce plan — uniquement `.claude/` et `docs/`).

- [ ] **Step 2 : les 3 gardes existantes (phase_guard, tdd_guard, stop_gate) toujours fonctionnelles**

```bash
cd /path/vers/StudyHub
echo '{"tool_name": "Write", "tool_input": {"file_path": "web/src/views/Notes/Notes.vue"}}' | CLAUDE_PROJECT_DIR="$(pwd)" python .claude/hooks/tdd_guard.py; echo "exit: $?"
```

Expected : comportement identique à avant ce plan (refus si aucun test
correspondant, phase courante ≥ 3 — non modifié par ce plan).

- [ ] **Step 3 : `ETAT.md` — noter la fin de ce chantier d'outillage**

Ajouter une ligne dans `ETAT.md` (section phase 4, sous le pointeur déjà
ajouté vers `workflow/`) confirmant que l'outillage (hooks +
`gestion-chantier`) est en place, avec la date.

- [ ] **Step 4 : commit final**

```bash
git add ETAT.md
git commit -m "docs(phase4): outillage workflow (hooks + skill gestion-chantier) en place"
```
