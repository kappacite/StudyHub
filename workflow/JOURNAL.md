# Journal global — workflow

Chantier actif : backend-ensembles-heterogenes

## Chantiers ouverts

- `backend-ensembles-heterogenes` — **actif**, branche `feature/backend-ensembles-heterogenes`, bloquant pour `bibliotheque-ensembles` et `reviser-hub`
- `editeur-notes-notation-ia` — pas commencé (volet frontend déjà planifié en détail, exécution pas démarrée)
- `bibliotheque-ensembles` — pas commencé, dépend de `backend-ensembles-heterogenes`
- `reviser-hub` — pas commencé, dépend de `backend-ensembles-heterogenes`
- `ecrans-peripheriques-visuels` — pas commencé, indépendant
- `classes-examens-planning` — pas commencé, indépendant

## Historique

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
