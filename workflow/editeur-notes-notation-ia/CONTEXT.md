# Éditeur de notes, mode Zen, Assistant IA & Notation de la note

## Pourquoi

Écran 4 de la refonte phase 4 (`web/src/views/Notes/NoteEdit.vue`), étendu le 2026-08-27 pour
couvrir l'Assistant IA à 3 méthodes (Évaluation mixte, Feuille blanche, Feynman) et un nouveau
bouton « Notation » distinct — note la qualité de la fiche sur 100, à ne pas confondre avec
l'Évaluation mixte qui note la performance de l'élève sur des exercices générés.

## Comment

Deux volets :
- **Backend** (flux 2 d'`ETAT.md`) : nouvelle méthode `ai_service` de notation de fiche + route
  dédiée. Indépendant du chantier `backend-ensembles-heterogenes`.
- **Frontend** : plan déjà écrit et committé, 10 tâches TDD complètes —
  `docs/superpowers/plans/2026-08-25-noteedit-migration-plan.md`. Le bouton Notation (Tâche 4)
  reste désactivé tant que le volet backend n'a pas livré sa cible.

C'est le chantier le plus avancé de cette liste : branche git `feature/noteedit-migration`
déjà ouverte, plan frontend déjà écrit.

## Dépendances

Aucune dépendance amont. Le bouton Notation (volet frontend) dépend du volet backend de ce
même chantier.

## Historique complet des décisions

`ETAT.md`, section « Plan global par flux... », flux 2 et flux 5. Plan frontend détaillé :
`docs/superpowers/plans/2026-08-25-noteedit-migration-plan.md`.
