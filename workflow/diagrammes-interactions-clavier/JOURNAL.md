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

## 2026-09-04 (Task 3 — créer un frère/enfant/supprimer/naviguer)

`DiagramCanvas.vue` : `onKeyDown` monté sur `window` (`onMounted`/`onUnmounted`, même
principe que le panoramique mais pour toute la durée de vie du composant, pas un geste).
Entrée/Tab créent une forme via `computeSiblingPosition` (cycle 6, Task 1) + `add-element` ;
Tab ajoute en plus un `LinkElement` via un second `execute()` séquentiel (rugosité assumée,
cf. `CONTEXT.md`) ; flèches utilisent `getAdjacentElementId` (Task 2) ; Suppr/Retour arrière
réutilisent `remove-element` (cycle 2, aucun changement). Rien n'agit sans sélection sauf les
flèches. Détail piégeux trouvé en écrivant les tests : un composant jamais démonté entre deux
tests laisse son listener `window` actif et réagit aux événements clavier du test suivant --
`afterEach` du fichier de test étendu pour appeler `wrapper.unmount()` sur chaque wrapper
monté (déclenche `onUnmounted`), pas seulement vider `document.body`. 24/24 tests composant
verts, 83/83 tests diagrammes. Prochaine action : Task 4 (renommage F2).
