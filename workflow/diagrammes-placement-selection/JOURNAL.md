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

## 2026-09-04 (Task 4 — déplacement, magnétisme, une commande par geste)

`DiagramCanvas.vue` : `onElementMouseDown` étendu -- au-delà du seuil de clic, suit la souris
(delta converti en unités monde selon le zoom), essaie l'alignement (`computeAlignmentSnap`)
puis retombe sur la grille (`snapToGrid`) si aucun guide trouvé, sauf `Alt` maintenu (position
brute). À la relâche seulement : **une** `DiagramHistory.execute(...)` avec la position finale,
émise via `update:document` (le composant ne mute jamais `props.document`, conforme au
principe posé dès le cycle 1). `history` exposé pour permettre l'annulation côté appelant.
10/10 tests composant verts (dont : une seule entrée d'historique par glisser complet, undo
restitue la position d'avant geste, Alt désactive la magnétisation). Prochaine action : Task 5
(rendu visuel : contour de sélection, guides d'alignement).

## 2026-09-04 (Task 5 — contour de sélection, guides d'alignement)

`DiagramCanvas.vue` : `dragPreview` (override d'affichage pendant un glisser actif, jamais
persisté) + `displayElements` (visibleElements avec l'override appliqué) remplace
`visibleElements` dans le template. `selectedElementBounds` pilote un `<rect>` de contour
(`data-test="selection-outline"`), `activeGuides` pilote des `<line>` (`data-test="alignment-
guide"`), peuplées pendant `onMove` (vidées si `Alt` ou aucun alignement trouvé) et vidées à
la relâche. 12/12 tests composant verts, 60/60 tests diagrammes. Prochaine action : Task 6
(vérification finale, clôture).

## 2026-09-04 (Task 6 — vérification finale, clôture du cycle 4)

Suite frontend complète : 632/632 (16 nouveaux pour ce chantier). `npm run build` propre.
`Diagrams.vue` toujours non modifié. Rappel de passation (déjà noté dans `CONTEXT.md`) :
redimensionnement/rotation/z-order/duplication/copier-coller/sélection multiple/groupes/
verrouillage (§8.4) restent hors périmètre de tout le cycle 4 -- à ne pas oublier pour un
futur cycle, aucun des 10 cycles restants ne les couvre par son titre littéral. Passation pour
le cycle 5 (liens, ancrage, routage) : la sélection/déplacement d'élément existent désormais,
un lien pourra s'ancrer sur l'élément sélectionné ou survolé, en réutilisant
`DiagramHistory.execute()` de la même façon. Chantier clos (code). Prochaine action : pousser
`feature/diagrammes-placement-selection`, ouvrir la PR.
