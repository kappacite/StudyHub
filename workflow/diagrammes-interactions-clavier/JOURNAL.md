# Journal — diagrammes-interactions-clavier

## 2026-09-04 (ouverture)

Chantier ouvert immédiatement après la clôture de `diagrammes-liens-ancrage` (PR #149
mergée). Cycle 6/14 — jusqu'ici toute interaction de `DiagramCanvas.vue` est à la souris ;
§8.4 exige un équivalent clavier complet (« sans ça, personne ne schématise en cours »).
Raccourcis retenus (convention outliner : Entrée = frère, Tab = enfant, F2 = renommer,
flèches = naviguer, Suppr = supprimer) et arbitrages (placement sans chevauchement simplifié,
créer un enfant = deux commandes non atomiques) documentés dans `CONTEXT.md`. Plan en 5
tâches : `PLAN.md`. Prochaine action : Task 1 (placement sans chevauchement).

## 2026-09-04 (Task 1+2 — placement sans chevauchement, navigation)

`web/src/diagram/layout.ts` : `computeSiblingPosition` (candidate à droite de l'origine,
décalée par incréments tant qu'elle chevauche une forme existante -- algorithme simple à une
direction, cf. `CONTEXT.md`) et `getAdjacentElementId` (cycle dans l'ordre du tableau,
`currentId` absent ou liste vide gérés sans exception). 7/7 tests verts. Prochaine action :
Task 3 (créer un frère/enfant/supprimer/naviguer, câblés sur `keydown`).
