# Journal — diagrammes-liens-ancrage

## 2026-09-04 (ouverture)

Chantier ouvert immédiatement après la clôture de `diagrammes-placement-selection` (PR #148
mergée). Cycle 5/14 — les liens existent dans le modèle depuis le cycle 1 (et sont déjà migrés
depuis le format v0) mais n'ont jamais été rendus par `DiagramCanvas.vue`. Ce cycle corrige ça
et ajoute la création de lien par geste. Exclusions explicites (édition de points de routage,
nettoyage de lien orphelin) documentées dans `CONTEXT.md`. Plan en 4 tâches : `PLAN.md`.
Prochaine action : Task 1 (ancrage).

## 2026-09-04 (Task 1 — ancrage)

`web/src/diagram/anchoring.ts` : `computeAnchorPoint(bounds, towardPoint)` -- rayon
centre→cible croisant le rectangle englobant, dégénère proprement vers le centre si la cible
coïncide avec lui (évite `0 * Infinity = NaN`). 4/4 tests verts. Prochaine action : Task 2
(rendu des liens).
