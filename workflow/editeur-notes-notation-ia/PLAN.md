# Plan — editeur-notes-notation-ia

## Backend — Notation de la note (flux 2)

- [ ] Écrire la spec détaillée (contrat de notation sur 100, prompt IA, route dédiée) via
  `superpowers:brainstorming` puis `superpowers:writing-plans` — format
  `docs/superpowers/plans/YYYY-MM-DD-notation-note.md`
- [ ] Implémenter la méthode `ai_service` de notation
- [ ] Route dédiée + schémas Pydantic requête/réponse
- [ ] Suite de tests backend verte, coverage ≥ 80 %

## Frontend — NoteEdit / mode Zen / Assistant IA (flux 5)

Plan détaillé déjà écrit : `docs/superpowers/plans/2026-08-25-noteedit-migration-plan.md`.

- [ ] Tâche 1 : extraire `NoteEditHelpModal.vue`
- [ ] Tâche 2 : extraire `NoteInputModal.vue`
- [ ] Tâche 3 : extraire `NoteEvaluationModal.vue`
- [ ] Tâche 4 : construire `NoteSidebar.vue` (remplace la modale d'activité IA) — bouton
  Notation câblé mais désactivé tant que le volet backend ci-dessus n'a pas livré
- [ ] Tâche 5 : construire `NoteFeynman.vue` et câbler l'activité Feynman
- [ ] Tâche 6 : retoner l'en-tête/barre d'outils/popup de partage/tiroir réglages du mode édition
- [ ] Tâche 7 : retoner le HTML généré par `renderMarkup` (lecture active, boutons SM-2, rendu diagramme)
- [ ] Tâche 8 : corriger la lacune d'erreur silencieuse, ajouter le fil d'ariane, retoner l'en-tête du mode lecture
- [ ] Tâche 9 : suite de tests comportementaux complète pour `NoteEdit.vue`
- [ ] Tâche 10 : vérification visuelle + mise à jour `ETAT.md`
- [ ] Activer le bouton Notation une fois le volet backend livré (retirer le `disabled`)
