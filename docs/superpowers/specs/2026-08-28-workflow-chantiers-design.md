# Design — Workflow de chantiers (`workflow/`)

Date : 2026-08-28, amendé le 2026-08-28 (cycle de vie git). Statut : validé
par l'utilisateur en chat, en attente de relecture avant passage à
`writing-plans`.

## Amendement — cycle de vie git (2026-08-28)

Ajout demandé par l'utilisateur après la mise en place initiale : chaque
chantier doit vivre sur sa propre branche, committer régulièrement, et se
clore par une PR. Contrainte découverte en le concevant : **`git push` est
interdit en toute circonstance dans ce dépôt** (`.claude/hooks/
guard_dangerous_commands.py` + `deny` de `settings.json`, aucune exception).
Politique retenue (confirmée par l'utilisateur) : **le push reste toujours
manuel** — je prépare tout (branche, commits, fichiers), je m'arrête et
demande explicitement à l'utilisateur d'exécuter `git push`, puis j'ouvre la
PR une fois la branche présente sur `origin`. Aucune exception ajoutée au
hook existant.

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
  approche, quelles contraintes. Pas un template lourd. **Porte aussi 3
  lignes d'en-tête parsables par les hooks** (mêmes conventions textuelles
  que `Chantier actif :` / `Phase: N`) :
  ```
  Statut : planifié | ouvert | pr-ouverte | clos
  Branche : (aucune) | feature/<slug-chantier>
  PR : (aucune) | #<numéro>
  ```
  Cycle : `planifié` (dossier créé sans branche — cas des 6 chantiers
  migrés depuis `ETAT.md` le 2026-08-28) → `ouvert` quand la branche est
  créée et le travail démarre → `pr-ouverte` quand la PR est ouverte (tout
  le `PLAN.md` est coché) → `clos` une fois la PR confirmée mergée
  (`gh pr view <numéro> --json state`).
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

**Responsabilité supplémentaire — porte d'ouverture.** Le même hook
intercepte aussi toute écriture sur `workflow/JOURNAL.md` qui changerait la
ligne `Chantier actif :` d'une valeur X vers une valeur Y ≠ X (détecté sur
le `content` de `Write` ou le `new_string` d'`Edit`/`MultiEdit`, comparé à
la valeur actuellement lue sur disque) :
- Si Y = `aucun` : toujours autorisé (clore n'est jamais bloqué par ce
  hook — la vérification de PR mergée a lieu à l'ouverture *suivante*, pas
  à la fermeture).
- Si Y est un slug de chantier (ouverture ou bascule) : refusé sauf si
  **toutes** les conditions suivantes sont vraies :
  1. Aucun chantier de `workflow/*/CONTEXT.md` n'a `Statut : ouvert` ou
     `Statut : pr-ouverte` (couvre à la fois "un chantier tourne encore"
     et "une PR est ouverte, pas encore mergée" — suffisant en
     concurrence à un seul chantier actif, pas besoin d'identifier X
     explicitement).
  2. `workflow/<Y>/CONTEXT.md` et `PLAN.md` existent déjà (discipline
     d'ouverture existante, inchangée).
  3. `main` local est à jour avec `origin/main` : `git fetch origin main
     --quiet` puis comparaison `git rev-parse main` = `git rev-parse
     origin/main`. Message de refus explicite (« git pull d'abord ») si
     différent.

Refuser avec un message explicite nommant la condition en échec (même
style que les autres `deny` du projet).

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

**Responsabilité supplémentaire — commit régulier forcé.** Si un chantier
est actif et que `git status --porcelain` n'est pas vide (changements non
committés, dans ou hors `workflow/`) : **bloquant**. Message : « des
changements non committés existent alors qu'un chantier est actif — commit
avant de t'arrêter (branche `<Branche :>` lue dans le `CONTEXT.md` du
chantier). » Rend mécanique la règle « committer régulièrement » plutôt que
de compter sur le rappel non bloquant déjà présent dans `stop_gate.py`.

### 3. Extension de `session_start.py` et `session_start_resume.py`

Si `workflow/JOURNAL.md` déclare un chantier actif : injecte en plus dans
`additionalContext` le contenu de `workflow/<slug>/CONTEXT.md`,
`workflow/<slug>/PLAN.md`, et les 10 dernières lignes de
`workflow/<slug>/JOURNAL.md`. Reprend le pattern déjà en place pour
`ETAT.md`/`PASSATION.md` dans ces deux fichiers (lecture conditionnelle,
concaténation dans le message de contexte).

## Skill

`.claude/skills/gestion-chantier/SKILL.md` — procédure et gabarits :

1. **Ouvrir un chantier** :
   1. Vérifier qu'aucun chantier n'a `Statut : pr-ouverte` et que le
      dernier actif (s'il y en a un) est `Statut : clos` — sinon
      s'arrêter et le signaler (le hook bloquera de toute façon à la
      dernière sous-étape, mais autant ne pas faire le travail pour rien).
   2. `git status` pour vérifier une copie propre, `git checkout main`,
      `git fetch origin main`, `git pull --ff-only origin main`.
   3. `git checkout -b feature/<slug>`.
   4. Créer `workflow/<slug>/{CONTEXT,PLAN,JOURNAL}.md` — `CONTEXT.md`
      avec l'en-tête `Statut : ouvert` / `Branche : feature/<slug>` /
      `PR : (aucune)`.
   5. Brainstormer si la tâche le justifie (skill
      `superpowers:brainstorming`), écrire le vrai `PLAN.md`.
   6. Déclarer `Chantier actif : <slug>` dans `workflow/JOURNAL.md`.
   7. Commit.
2. **Travailler un point** : prendre la première case non cochée de
   `PLAN.md` comme tâche courante, l'exécuter, **committer** (le hook Stop
   bloque désormais si ce n'est pas fait), ajouter une entrée à
   `workflow/<slug>/JOURNAL.md` (description + id de commit), cocher la
   case dans `PLAN.md`, ajouter une ligne courte à `workflow/JOURNAL.md`
   (index global).
3. **Clôturer un chantier** (toutes les cases de `PLAN.md` cochées) :
   1. Entrée de clôture dans `workflow/<slug>/JOURNAL.md`.
   2. **Demander à l'utilisateur de pousser la branche** — `git push` est
      bloqué pour l'agent (`guard_dangerous_commands.py`, aucune
      exception) : indiquer explicitement la commande
      `git push -u origin feature/<slug>` et attendre confirmation.
   3. Une fois poussée, ouvrir la PR (`gh pr create`, avec confirmation
      utilisateur préalable comme toute action visible/partagée).
   4. Mettre à jour `CONTEXT.md` : `Statut : pr-ouverte`, `PR : #<numéro>`.
   5. Repasser `workflow/JOURNAL.md` à `Chantier actif : aucun`, ligne de
      clôture dans l'index global.
   6. Commit.
4. **Constater une PR mergée** (à vérifier avant la prochaine ouverture,
   étape 1 ci-dessus, ou dès que l'utilisateur signale le merge) :
   `gh pr view <numéro> --json state -q .state` = `MERGED` → mettre à jour
   `CONTEXT.md` : `Statut : clos`. Commit.

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
