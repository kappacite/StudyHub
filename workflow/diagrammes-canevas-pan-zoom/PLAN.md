# Plan — diagrammes-canevas-pan-zoom (Phase 5, cycle 3)

Une case = une tâche atomique. TDD sans exception pour la géométrie (§8.7 : « fonctions pures
sur des coordonnées... se testent sans canevas ni DOM »). Le rendu visuel du composant Vue
relève de l'exception écran-capture — ses interactions (pan/zoom) restent testées. Arbitrages :
`CONTEXT.md`.

- [x] Task 1 — Modèle de caméra et conversions écran↔monde dans `web/src/diagram/camera.ts` :
  `Camera { x: number; y: number; zoom: number }`, `createDefaultCamera()`,
  `screenToWorld(point, camera, viewportSize)`, `worldToScreen(point, camera, viewportSize)`.
  Tests : rondtrip (`worldToScreen(screenToWorld(p, cam, vp), cam, vp)` ≈ `p`, tolérance
  flottante) ; un zoom de 2 rend un déplacement écran de N px deux fois plus petit en
  coordonnées monde ; caméra par défaut (`zoom: 1`) fait coïncider écran et monde à l'offset
  près.
- [x] Task 2 — Panoramique et zoom centré sur un point, purs, dans `camera.ts` :
  `panBy(camera, dx, dy): Camera` (déplace en coordonnées écran, indépendant du zoom courant),
  `zoomAt(camera, screenPoint, factor, viewportSize): Camera` (le point sous le curseur reste
  visuellement fixe après le zoom — propriété clé, pas juste `zoom *= factor`). Tests :
  `panBy` déplace la caméra sans changer `zoom` ; `zoomAt` change `zoom` sans déplacer le point
  écran ciblé en coordonnées monde (`screenToWorld` du point avant/après reste identique).
- [x] Task 3 — Rendu borné à la fenêtre de vue dans `web/src/diagram/viewport.ts` :
  `getVisibleWorldBounds(camera, viewportSize): Bounds`, `elementBounds(element): Bounds`
  (boîte englobante x/y/width/height, déjà présente sur `BaseElement`),
  `cullElements(elements, camera, viewportSize): DiagramElement[]` (intersection avec les
  bornes visibles, pas d'égalité stricte -- un élément partiellement visible reste affiché).
  Tests : un élément entièrement hors-champ est exclu ; un élément partiellement chevauchant
  la fenêtre de vue est conservé ; un document vide ne casse rien (bornes visibles valides
  même sans élément) ; le zoom réduit agrandit la zone visible en coordonnées monde (plus
  d'éléments passent le filtre).
- [x] Task 4 — Recadrage sur tout le contenu : `computeFitToContent(elements, viewportSize):
  Camera` dans `viewport.ts`. Calcule la boîte englobante de tous les éléments puis la caméra
  qui la centre entièrement dans la fenêtre de vue (avec une marge). Tests : un seul élément
  se retrouve centré ; plusieurs éléments dispersés sont tous inclus dans les bornes visibles
  résultantes ; un document vide retourne la caméra par défaut (pas de division par zéro sur
  une boîte englobante nulle).
- [ ] Task 5 — `DiagramCanvas.vue` (nouveau composant isolé, non routé) dans
  `web/src/diagram/DiagramCanvas.vue` : reçoit un `DiagramDocumentV1` en prop, rend un `<svg>`
  avec `viewBox` piloté par la caméra (Task 1-2), applique `cullElements` (Task 3) avant de
  rendre, molette = zoom centré sur le curseur, glisser sur le fond (pas sur un élément) =
  panoramique. Formes affichées en lecture seule (rectangles/cercles/texte selon `shape`,
  pas d'interaction cycle 4). Tests composant : le nombre d'éléments SVG rendus correspond au
  résultat de `cullElements`, pas au total du document ; la molette modifie le `viewBox` ;
  un glisser sur le fond modifie le `viewBox` sans déclencher de commande (aucune interaction
  avec `DiagramHistory`, hors périmètre de ce cycle).
- [ ] Task 6 — Vérification finale : suite frontend complète verte, `npm run build` propre,
  `Diagrams.vue` toujours non modifié. Clôture du chantier ; passation `JOURNAL.md` pour le
  cycle 4 (placement, sélection, magnétisme) : `DiagramCanvas.vue` est prêt à recevoir la
  détection de clic/glisser sur un élément individuel, qui devra passer par
  `DiagramHistory.execute()` (cycle 2) plutôt que de muter l'état localement.
