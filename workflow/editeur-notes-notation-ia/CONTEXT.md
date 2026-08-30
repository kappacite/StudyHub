# Éditeur de notes, mode Zen, Assistant IA & Notation de la note

Statut : planifié
Branche : (aucune)
PR : (aucune)

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

## Note ajoutée le 2026-08-30 (investigation `bibliotheque-redesign`, écrans de note)

Deux constats faits en comparant les vraies maquettes Direction A à l'occasion d'un autre
chantier (`docs/superpowers/specs/2026-08-30-bibliotheque-redesign-design.md`, § « Écrans
d'une note ») :

1. **La Tâche 5 du plan frontend ci-dessus (« construire `NoteFeynman.vue` et câbler
   l'activité Feynman ») est déjà livrée** — pas par ce chantier, mais par `reviser-hub`
   (Task 3 de sa redesign, mergée dans `main` via PR #130). `NoteFeynman.vue` existe déjà,
   vérifié conforme à `NoteFeynman.dc.html`. À la reprise de `feature/noteedit-migration` :
   cocher cette tâche sans la refaire, et vérifier seulement que le bouton « Feynman » de
   `NoteSidebar.vue` (Tâche 4) pointe bien vers la route déjà existante
   (`notes/:id/feynman`) plutôt que de recréer un flux.
2. **`NoteEvaluation.dc.html` (le fichier de maquette) est la vraie référence visuelle pour la
   future fonctionnalité « Notation »**, pas pour l'écran `NoteEvaluation.vue` qui existe déjà
   dans le code. La maquette montre : score global sur cercle, « Points forts »/« À
   améliorer », « Suggestions » — exactement le contrat de « Notation » décrit au § Pourquoi
   ci-dessus (note de la fiche sur 100). Le fichier actuel `web/src/views/Notes/NoteEvaluation.vue`
   implémente autre chose (l'« Évaluation mixte » : questions générées, score de performance
   de l'élève en %) — collision de nom entre la maquette et le code existant, à garder en tête
   pour ne pas mélanger les deux quand la spec détaillée du volet backend « Notation » sera
   écrite (`PLAN.md`, première case du volet backend, pas encore faite). Le nouvel écran de
   résultat de « Notation » devra probablement vivre dans un fichier au nom différent
   (`NoteGrading.vue`, `NoteNotation.vue`... à trancher) pour éviter la confusion avec
   `NoteEvaluation.vue` existant.
