# Journal global — workflow

Chantier actif : aucun

## Chantiers ouverts

- `backend-ensembles-heterogenes` — **code clos**, branche `feature/backend-ensembles-heterogenes`
  prête pour push + PR humaine (procédure `gestion-chantier`). Les 4 tâches du plan détaillé sont
  faites (migration + modèles, schémas/fonctions pures, câblage service, clôture) ; toujours
  bloquant pour `bibliotheque-ensembles` et `reviser-hub` jusqu'au merge. Détail :
  `workflow/backend-ensembles-heterogenes/JOURNAL.md`.
- `editeur-notes-notation-ia` — pas commencé (volet frontend déjà planifié en détail, exécution pas démarrée)
- `bibliotheque-ensembles` — pas commencé, dépend de `backend-ensembles-heterogenes`
- `reviser-hub` — pas commencé, dépend de `backend-ensembles-heterogenes`
- `ecrans-peripheriques-visuels` — pas commencé, indépendant
- `classes-examens-planning` — pas commencé, indépendant

## Historique

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
