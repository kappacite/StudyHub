# Research — Phase 5 : Refonte Éditeur de Diagrammes en Canevas Libre

## Contexte Architectural & Statut Actuel
- **Objectif global de la phase** : Remplacer l'ancien éditeur contraint par un canevas SVG libre infini (`DiagramCanvas.vue`) avec modèle versionné v1, undo/redo, pan, zoom géométrique, sélection/magnétisme, liens d'ancrage magnétiques, et interactions tactiles/clavier (14 cycles ordonnés).
- **Cycles déjà livrés et mergés (1 à 6)** :
  - Cycle 1 : Modèle de document v1 & sérialisation JSON (`web/src/diagram/document.ts`)
  - Cycle 2 : Commandes, exécution et pile d'annulation Undo/Redo (`web/src/diagram/commands.ts`, `history.ts`)
  - Cycle 3 : Canevas infini, panoramique et zoom géométrique centré (`web/src/diagram/geometry.ts`)
  - Cycle 4 : Placement, sélection multiple et magnétisme (`web/src/diagram/selection.ts`, `snap.ts`)
  - Cycle 5 : Liens d'ancrage magnétiques et routage (`web/src/diagram/routing.ts`, `LinkElement`)
  - Cycle 6 : Interactions clavier, raccourcis et suppression (`DiagramCanvas.vue`)
- **Cycle 7 actif : Interactions Tactiles (`feature/diagrammes-interactions-tactiles`)** :
  - Livré : Géométrie pure `touch.ts` (`computeDistance`, `computeMidpoint`), glisser à un doigt (fond/élément) avec seuil clic/glisser et émission d'une commande unique au relâchement, pincer pour zoomer centré sur le point médian.
  - En cours : Appui long (500 ms) sur un élément pour entrer en mode création de lien (équivalent tactile de `Maj` + glisser), avec test `vi.useFakeTimers`.
  - À venir : Clôture du cycle 7 avec vérification de la suite frontend (508+ tests).
- **Cycle 8 à planifier ensuite** : Conteneurs visuels, texte libre, images, et rendu LaTeX dans les formes du diagramme.

## Fichiers Clés & Dépendances
- `web/src/diagram/DiagramCanvas.vue` : Composant principal du canevas SVG interactif.
- `web/src/diagram/touch.ts` : Fonctions pures de calcul tactile (distance, point médian).
- `web/src/diagram/document.ts` : Types de données `DiagramDocumentV1`, `DiagramElement`, `LinkElement`.
- `web/src/diagram/geometry.ts` : Fonctions géométriques pures (`screenToWorld`, `zoomAt`, etc.).
- `web/tests/diagram/DiagramCanvas.spec.ts` : Tests de composants Vitest pour le canevas.
- `web/tests/diagram/touch.spec.ts` : Tests unitaires de géométrie tactile.

## Règles & Invariants
- Tests unitaires TDD stricts avant toute implémentation.
- Ne jamais dégrader la suite existante (508 tests web actuellement verts).
- Écouteurs d'événements tactiles additifs sur le `<svg>` (`touch-action: none`).
- Pas de `git push` autonome.
