# Plan — editeur-notes-notation-ia

> Réécrit le 2026-08-30 : l'ancien plan frontend (`docs/superpowers/plans/
> 2026-08-25-noteedit-migration-plan.md`, branche `feature/noteedit-migration`) n'est plus
> exécutable tel quel — conflit majeur avec la réécriture de `NoteEdit.vue` par `reviser-hub`
> depuis mergée. Nouveau plan écrit contre `main` actuel et le vrai canevas Direction A. Détail
> complet du ruling : `workflow/editeur-notes-notation-ia/CONTEXT.md`.

## Backend — Notation de la note (flux 2)

Hors périmètre de ce chantier (nécessite son propre brainstorming/spec). Le bouton Notation
(volet frontend ci-dessous) est ajouté désactivé en attendant.

- [ ] Écrire la spec détaillée (contrat de notation sur 100, prompt IA, route dédiée) via
  `superpowers:brainstorming` puis `superpowers:writing-plans`. Référence visuelle de l'écran
  de résultat déjà identifiée : `NoteEvaluation.dc.html` (score sur cercle, « Points forts »/
  « À améliorer », « Suggestions »).
- [ ] Implémenter la méthode `ai_service` de notation, route dédiée + schémas Pydantic, suite
  de tests backend verte (coverage ≥ 80 %).

## Frontend — NoteEdit / mode Zen / Assistant IA

Plan détaillé exécutable : `docs/superpowers/plans/2026-08-30-editeur-notes-redesign.md`.

- [ ] Tâche 1 : extraire `NoteEditHelpModal.vue`
- [ ] Tâche 2 : extraire `NoteInputModal.vue`
- [ ] Tâche 3 : extraire `NoteEvaluationModal.vue`
- [ ] Tâche 4 : construire `NoteSidebar.vue` (3 méthodes canevas-vérifiées) + bouton Notation
  désactivé
- [ ] Tâche 5 : vérifier le câblage Feynman existant (pas de reconstruction)
- [ ] Tâche 6 : retoner l'en-tête/barre d'outils/popup de partage/tiroir réglages du mode édition
- [ ] Tâche 7 : retoner le HTML généré par `renderMarkup`
- [ ] Tâche 8 : corriger la lacune d'erreur silencieuse, ajouter le fil d'ariane (écart canevas
  confirmé), retoner l'en-tête du mode lecture
- [ ] Tâche 9 : suite de tests comportementaux complète pour `NoteEdit.vue`
- [ ] Tâche 10 : vérification visuelle + mise à jour `ETAT.md` + clôture
