# Plan — editeur-notes-notation-ia

> Détail ajouté le 2026-08-30 suite à l'investigation `bibliotheque-redesign`
> (`docs/superpowers/specs/2026-08-30-bibliotheque-redesign-design.md`, § « Écrans d'une
> note ») : une vraie maquette existe déjà pour l'écran de résultat de cette fonctionnalité,
> jamais mentionnée avant — voir Tâche 4bis ci-dessous. **Toujours pas de brainstorming fait**,
> ce détail cadre la future spec, ne la remplace pas.

## Backend — Notation de la note (flux 2)

- [ ] Écrire la spec détaillée (contrat de notation sur 100, prompt IA, route dédiée) via
  `superpowers:brainstorming` puis `superpowers:writing-plans` — format
  `docs/superpowers/plans/YYYY-MM-DD-notation-note.md`. **Inclure dans le brainstorming** : la
  maquette `NoteEvaluation.dc.html` (score sur cercle, « Points forts »/« À améliorer »,
  « Suggestions ») est la référence visuelle de l'écran de résultat — son contrat de données
  (score global, liste de points forts, liste de points à améliorer, un paragraphe de
  suggestion) doit guider le schéma Pydantic de réponse, pas être décidé indépendamment puis
  recalé après coup sur la maquette.
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
- [ ] **Tâche 4bis (ajoutée le 2026-08-30, pas dans le plan détaillé d'origine)** : construire
  l'écran de résultat de la Notation selon `NoteEvaluation.dc.html` — score global (cercle),
  section « Points forts », section « À améliorer », section « Suggestions ». **Ne pas nommer
  le fichier `NoteEvaluation.vue`** (déjà pris par l'écran existant d'Évaluation mixte, une
  fonctionnalité différente — collision de nom déjà signalée) : `NoteGrading.vue` ou
  `NoteNotation.vue` à trancher au moment du plan détaillé. Dépend du backend ci-dessus.
- [x] Tâche 5 : construire `NoteFeynman.vue` et câbler l'activité Feynman — **déjà livrée par
  un autre chantier** (`reviser-hub`, Task 3, mergée PR #130), vérifiée conforme à
  `NoteFeynman.dc.html`. À la reprise de `feature/noteedit-migration` : vérifier seulement que
  le bouton Feynman de `NoteSidebar.vue` pointe vers la route existante (`notes/:id/feynman`),
  ne pas reconstruire.
- [ ] Tâche 6 : retoner l'en-tête/barre d'outils/popup de partage/tiroir réglages du mode édition
- [ ] Tâche 7 : retoner le HTML généré par `renderMarkup` (lecture active, boutons SM-2, rendu diagramme)
- [ ] Tâche 8 : corriger la lacune d'erreur silencieuse, ajouter le fil d'ariane, retoner l'en-tête du mode lecture
- [ ] Tâche 9 : suite de tests comportementaux complète pour `NoteEdit.vue`
- [ ] Tâche 10 : vérification visuelle + mise à jour `ETAT.md`
- [ ] Activer le bouton Notation une fois le volet backend livré (retirer le `disabled`)
