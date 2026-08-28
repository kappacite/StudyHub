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
