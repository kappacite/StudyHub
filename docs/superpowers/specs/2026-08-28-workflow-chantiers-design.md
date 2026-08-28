# Design — Workflow de chantiers (`workflow/`)

Date : 2026-08-28. Statut : validé par l'utilisateur en chat le 2026-08-28, en
attente de relecture du présent document avant passage à `writing-plans`.

## Pourquoi

Le suivi actuel (`ETAT.md`) est conçu pour une progression linéaire à phase
unique (phases 0→6 de la refonte). Il n'existe aucun mécanisme pour ouvrir,
suivre et clore des chantiers de développement indépendants (bug, petite
fonctionnalité, gros chantier annexe) sans les rattacher artificiellement à
`ETAT.md`. Le risque signalé par l'utilisateur : partir en désordre sur une
tâche sans plan écrit ni trace de ce qui a été fait.

Objectif : un système de suivi par chantier, générique et réutilisable pour
tout futur travail, avec une discipline mécaniquement forcée (pas seulement
documentée) une fois qu'un chantier est ouvert.

**Hors scope explicite** : la refonte UI en cours (`ETAT.md` phase 4) n'est
**pas** migrée vers ce système maintenant. Elle continue sous le mécanisme
existant (`ETAT.md`, `PASSATION.md`, hooks `phase_guard`/`tdd_guard`/
`stop_gate`) jusqu'à une décision explicite ultérieure de migration.

## Structure de fichiers

```
workflow/
  JOURNAL.md                 # index global
  <slug-chantier>/
    CONTEXT.md                # bref : pourquoi, comment, contraintes
    PLAN.md                   # checklist d'étapes issue d'un brainstorming
    JOURNAL.md                # une entrée par action : description + commit
```

- `<slug-chantier>` : kebab-case (ex. `rework-bibliotheque`), cohérent avec
  la convention `kebab-case` des endpoints du projet (`CLAUDE.md`).
- `PLAN.md` : liste `- [ ]` / `- [x]`, une case = une tâche atomique
  ("une tâche = un point dans un chantier"). Issu d'un brainstorming
  (skill `superpowers:brainstorming` si la tâche le justifie).
- `CONTEXT.md` : quelques paragraphes — pourquoi ce chantier, quelle
  approche, quelles contraintes. Pas un template lourd.
- `JOURNAL.md` (par chantier) : une entrée par action effectuée —
  description (choix technique/fonctionnel) + id de commit associé.

### Format `workflow/JOURNAL.md` (index global)

Première ligne parsable par les hooks, même mécanique que `Phase: N` dans
`ETAT.md` :

```
Chantier actif : <slug-chantier>
```

ou `Chantier actif : aucun` si rien n'est ouvert. Un seul chantier actif à
la fois (décision utilisateur). En dessous, historique bref
reverse-chronologique :

```
- 2026-08-28 — [rework-bibliotheque] Point 3 (migration DAO) terminé,
  commit a1b2c3d. Prochain : Point 4 (service).
```

## Hooks

Trois hooks, aucun hook existant réécrit en profondeur (ajouts additifs
uniquement sur `session_start.py`/`session_start_resume.py`).

### 1. `workflow_guard.py` (PreToolUse, matcher `Write|Edit|MultiEdit`)

Actif **seulement si** `workflow/JOURNAL.md` déclare un chantier actif
(sinon `sys.exit(0)` immédiat — aucun effet sur le travail non migré).

Si un chantier est actif :
- Autorisé sans condition : écritures sous `workflow/`, `.claude/`,
  `docs/`, ainsi que `ETAT.md`/`PASSATION.md` à la racine.
- Pour tout autre chemin : refusé (`permissionDecision: deny`) si
  `workflow/<slug>/PLAN.md` n'existe pas, est vide, ou ne contient plus
  aucune case `- [ ]` non cochée. Message pointant vers la skill
  `gestion-chantier` pour écrire/compléter le plan.
- Si `PLAN.md` existe avec au moins une case non cochée : autorisé (la
  correspondance fine "ce fichier appartient bien à ce point du plan" reste
  une discipline portée par la skill, pas mécaniquement vérifiable par
  chemin de fichier).

Miroir direct de `phase_guard.py` (même structure : lecture d'un pointeur
textuel, allow-list de chemins, `deny` avec message explicite).

### 2. `workflow_stop_gate.py` (Stop)

Si un chantier est actif et que le diff en attente (`git status
--porcelain`) contient des fichiers hors `workflow/` :
- **Bloquant** (`exit(2)`, même mécanique que la garde TDD de
  `stop_gate.py`) si `workflow/<slug>/JOURNAL.md` ne fait pas partie du
  diff en attente ni du dernier commit — force la journalisation avant de
  s'arrêter.
- **Avertissement non bloquant** (`systemMessage`) si `workflow/JOURNAL.md`
  (l'index global) n'a pas été modifié dans les dernières entrées récentes
  du chantier — rappel, pas un blocage (la fréquence de mise à jour de
  l'index global est plus laxiste que le journal par chantier).

`stop_hook_active` (déjà lu par `stop_gate.py`) respecté ici aussi pour
éviter une boucle de blocage infinie.

### 3. Extension de `session_start.py` et `session_start_resume.py`

Si `workflow/JOURNAL.md` déclare un chantier actif : injecte en plus dans
`additionalContext` le contenu de `workflow/<slug>/CONTEXT.md`,
`workflow/<slug>/PLAN.md`, et les 10 dernières lignes de
`workflow/<slug>/JOURNAL.md`. Reprend le pattern déjà en place pour
`ETAT.md`/`PASSATION.md` dans ces deux fichiers (lecture conditionnelle,
concaténation dans le message de contexte).

## Skill

`.claude/skills/gestion-chantier/SKILL.md` — procédure et gabarits :

1. **Ouvrir un chantier** : créer `workflow/<slug>/`, écrire `CONTEXT.md`
   (bref), brainstormer si la tâche le justifie (skill
   `superpowers:brainstorming`), écrire `PLAN.md` (checklist), déclarer
   `Chantier actif : <slug>` dans `workflow/JOURNAL.md`.
2. **Travailler un point** : prendre la première case non cochée de
   `PLAN.md` comme tâche courante, l'exécuter, committer, ajouter une
   entrée à `workflow/<slug>/JOURNAL.md` (description + id de commit),
   cocher la case dans `PLAN.md`, ajouter une ligne courte à
   `workflow/JOURNAL.md` (index global).
3. **Clôturer un chantier** : toutes les cases de `PLAN.md` cochées,
   entrée de clôture dans `workflow/<slug>/JOURNAL.md`, repasser
   `workflow/JOURNAL.md` à `Chantier actif : aucun`, ligne de clôture dans
   l'index global.

Gabarits des 3 fichiers inclus dans la skill (blocs de code prêts à copier).

## Ce qui n'est pas fait ici

- Pas de subagent dédié (décision utilisateur — skill + hooks suffisent).
- Pas de migration de la refonte UI (`ETAT.md`) vers ce système.
- Pas de mécanisme pour plusieurs chantiers actifs en parallèle.
- Pas de mise à jour de `CLAUDE.md` au-delà d'une ligne de renvoi vers la
  skill, pour rester sous la limite de 60 lignes du fichier.

## Risque accepté (confirmé en chat)

Une fois un chantier actif, `workflow_guard.py` bloque *toute* écriture
hors `workflow/`/`.claude/`/`docs/`/`ETAT.md`/`PASSATION.md`, même sur des
fichiers sans rapport direct avec ce chantier — cohérent avec la
concurrence à un seul chantier actif à la fois, et avec la demande
explicite de forcer le passage par le système plutôt que de tenter une
détection fine (et donc fragile) par chemin de fichier.
