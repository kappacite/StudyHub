# Journal — diagrammes-placement-selection

## 2026-09-04 (ouverture)

Chantier ouvert immédiatement après la clôture de `diagrammes-canevas-pan-zoom` (PR #147
mergée). Cycle 4/14 — premier cycle où les éléments deviennent interactifs (sélection,
déplacement, magnétisme, guides d'alignement). Portée volontairement restreinte au titre
littéral du cycle : redimensionnement/rotation/z-order/duplication/copier-coller/sélection
multiple/groupes/verrouillage (§8.4) restent hors périmètre, signalés dans `CONTEXT.md` pour
ne pas être oubliés. Plan en 6 tâches : `PLAN.md`. Prochaine action : Task 1 (magnétisme sur
grille).

## 2026-09-04 (Task 1+2 — magnétisme sur grille, guides d'alignement)

`web/src/diagram/snapping.ts` : `snapToGrid` (arrondi au multiple le plus proche, fonctionne
sur des valeurs négatives). `computeAlignmentSnap` : compare gauche/centre/droite (X) et
haut/centre/bas (Y) de l'élément déplacé à chaque autre élément, indépendamment par axe ; le
voisin le plus proche dans le seuil gagne, aucun snap si rien n'est assez proche. 7/7 tests
verts. Prochaine action : Task 3 (sélection).

## 2026-09-04 (Task 3 — sélection, distinction clic/glisser)

`DiagramCanvas.vue` : `selectedElementId` (état local, exposé). `onElementMouseDown` (nouveau,
`@mousedown.stop` sur chaque élément) sélectionne à la relâche. `onBackgroundMouseDown` révisé
: suit le déplacement depuis le point de départ, sous le seuil (`CLICK_THRESHOLD_PX = 4`) la
relâche désélectionne, au-delà c'est le panoramique existant (cycle 3) et la sélection reste
intacte. 6/6 tests composant verts. Prochaine action : Task 4 (déplacement d'un élément
sélectionné, magnétisme, une seule commande par geste).
