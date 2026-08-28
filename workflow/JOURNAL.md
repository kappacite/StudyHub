# Journal global — workflow

Chantier actif : bibliotheque-ensembles

## Chantiers ouverts

- `bibliotheque-ensembles` — **code clos**, branche `feature/bibliotheque-ensembles` prête pour
  revue finale de branche puis push + PR humaine. 11 tâches TDD faites (dont 2 ajoutées en
  cours d'exécution — un correctif `TeacherDashboard.vue` et le type `flashcard` manquant dans
  `RevisionItemModal.vue`). Vérification visuelle réelle non faite (environnement de dev déjà
  occupé par d'autres conteneurs) — écart documenté, à combler si l'environnement se stabilise.
- `editeur-notes-notation-ia` — pas commencé (volet frontend déjà planifié en détail, exécution pas démarrée)
- `reviser-hub` — pas commencé, débloqué (`backend-ensembles-heterogenes` mergé)
- `ecrans-peripheriques-visuels` — pas commencé, indépendant
- `classes-examens-planning` — pas commencé, indépendant

## Historique

- 2026-08-28 — [bibliotheque-ensembles] Chantier clos (code) : 11 tâches TDD faites (dont 2
  ajoutées en cours d'exécution suite à des découvertes réelles — `TeacherDashboard.vue`
  cassé par la nullabilité de `RevisionSet.type`, type `flashcard` manquant dans
  `RevisionItemModal.vue`), un tour de correction sur `Binders.vue` (2 constats critiques :
  perte de fonctionnalité dans la fusion Decks+Ensembles, seuil de cartes dues affaibli).
  Portée finale confirmée propre (`git diff --stat`), 319/319 tests verts. Vérification
  visuelle non faite (environnement de dev partagé, risque d'interférence jugé supérieur au
  bénéfice) — écart documenté. Prochaine action : revue finale de branche, puis push + PR.
- 2026-08-28 — [bibliotheque-ensembles] Chantier activé, branche `feature/bibliotheque-ensembles`
  créée depuis `main` à jour (worktree `.worktrees/bibliotheque-ensembles`). Choisi comme
  prochain chantier (recommandation) : premier de l'ordre numérique des flux après le socle
  backend (flux 3, juste après flux 1), fraîchement débloqué, sans ambiguïté à réconcilier
  (contrairement à `editeur-notes-notation-ia`, dont le volet frontend est déjà partiellement
  implémenté sur une branche non mergée — laissé de côté pour l'instant). Prochain point : spec +
  plan détaillé via brainstorming.
- 2026-08-28 — [backend-ensembles-heterogenes] **PR #126 mergée dans `main`** (squash,
  `d2b6305`), CI verte (6/6 checks, dont « Backend · migrations (PostgreSQL) » qui valide la
  migration à froid — confirme a posteriori que la vérification manuelle passée localement
  n'était pas nécessaire). Chantier `clos`. `bibliotheque-ensembles` et `reviser-hub` débloqués.
  Prochaine action : choisir le prochain chantier à ouvrir.
- 2026-08-28 — [backend-ensembles-heterogenes] Chantier clos (code) : Task 4 terminée sur
  décision utilisateur explicite de passer la vérification Postgres manuelle (couverture SQLite
  85% jugée suffisante). Toutes les tâches du plan détaillé faites, commit `0e54608`. Prochaine
  action : demander à l'utilisateur de pousser `feature/backend-ensembles-heterogenes` puis ouvrir
  la PR (procédure `gestion-chantier`).
- 2026-08-28 — [backend-ensembles-heterogenes] Reprise après redémarrage : Tasks 1 et 2
  s'avèrent déjà faites (committées avant l'arrêt, journal pas mis à jour). Task 3 exécutée en
  TDD (câblage `item.type` dans `create_item`/`update_item`/`grade_item`/`answer_item`, bug de
  plan corrigé au passage — mauvaises URLs de test), commit `9c29185`, 85 % coverage. Task 4
  entamée : vérification Postgres réelle bloquée par un volume Docker local incohérent (séquelle
  de l'instabilité de la session précédente) — sa remise à zéro est bloquée par le hook de garde,
  reste à trancher par un humain. Détail complet :
  `workflow/backend-ensembles-heterogenes/JOURNAL.md`.
- 2026-08-28 — [backend-ensembles-heterogenes] Arrêt avant redémarrage PC (Docker Desktop
  instable). Aucun code touché, rien à perdre. Worktree `.worktrees/backend-ensembles-heterogenes`
  prête, venv local de secours documenté si Docker reste capricieux après redémarrage.
  Prochaine action : reprendre `subagent-driven-development` à la Task 1. Détail complet :
  `workflow/backend-ensembles-heterogenes/JOURNAL.md`.
- 2026-08-28 — [backend-ensembles-heterogenes] Spec + plan écrits (4 tâches TDD). Découverte
  majeure : la fusion Deck/Flashcard toucherait 47 fichiers backend, reportée à des chantiers
  futurs distincts — ce chantier se limite au socle schéma (`type` au niveau de l'item, ajout
  du type `flashcard`). Prochain point : Task 1 (migration Alembic + modèles).
- 2026-08-28 — [backend-ensembles-heterogenes] Chantier activé (premier de l'ordre fixé,
  flux 1, bloquant). Branche `feature/backend-ensembles-heterogenes` créée depuis `main`
  à jour. Prochain point : écrire la spec détaillée du modèle de données cible.
- 2026-08-28 — 6 chantiers ouverts, migrés depuis `ETAT.md` § « Plan global par flux —
  extension révision hétérogène + assistant IA (2026-08-27) ». Aucun travail d'implémentation
  migré : tous les flux étaient déjà « pas commencé » ou « plan écrit, exécution pas
  commencée » — seule l'organisation en chantiers change, aucune décision fonctionnelle
  réécrite. Détail du regroupement et des correspondances flux→chantier dans le `CONTEXT.md`
  de chaque chantier. Commit : à suivre.
