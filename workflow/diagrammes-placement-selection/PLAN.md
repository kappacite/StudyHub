# Plan — diagrammes-placement-selection (Phase 5, cycle 4)

Une case = une tâche atomique. TDD sans exception pour la géométrie (magnétisme/alignement :
fonctions pures, §8.7). Arbitrages : `CONTEXT.md`.

- [x] Task 1 — Magnétisme sur grille, pur, dans `web/src/diagram/snapping.ts` :
  `snapToGrid(point, gridSize): Point` (arrondit x/y au multiple de `gridSize` le plus
  proche). Tests : un point déjà sur la grille reste inchangé ; un point à mi-chemin arrondit
  au plus proche (comportement d'arrondi standard, pas de biais systématique vers le bas) ;
  `gridSize` de 1 est un no-op (pas d'arrondi visible).
- [x] Task 2 — Guides d'alignement, purs, dans `snapping.ts` :
  `computeAlignmentSnap(draggedBounds, otherBounds[], thresholdPx, zoom): { snapped: Point;
  guides: AlignmentGuide[] }`. Compare les bords/centres (gauche/droite/haut/bas/centre-x/
  centre-y) de l'élément déplacé à ceux de chaque autre élément ; si un écart est sous le
  seuil (converti en unités monde selon le zoom), aligne exactement dessus et retourne un
  guide (ligne à afficher). Tests : alignement gauche-sur-gauche avec un voisin proche ;
  aucun voisin dans le seuil -> pas de snap (position inchangée, pas de guide) ; plusieurs
  voisins candidats -> le plus proche gagne (pas un guide par voisin).
- [ ] Task 3 — Sélection dans `DiagramCanvas.vue` : `selectedElementId` (état local, jamais
  persisté dans `DiagramDocumentV1`), clic sur un élément le sélectionne, clic sur le fond
  désélectionne. Distinction clic/glisser via un seuil de déplacement (quelques pixels) --
  sous le seuil = clic, au-delà = le comportement existant (panoramique sur le fond, cf.
  Task 4 pour un élément). Tests composant : clic sur un élément expose son id comme
  sélectionné ; clic sur le fond après une sélection la retire ; un glisser (dépassant le
  seuil) sur le fond ne modifie pas la sélection courante (reste le panoramique du cycle 3).
- [ ] Task 4 — Déplacement d'un élément sélectionné : glisser sur un élément (au-delà du
  seuil de Task 3) suit la souris avec un état de position « live » local (pas de commande
  tant que le geste continue), applique le magnétisme (Task 1) et les guides d'alignement
  (Task 2) à chaque mouvement, sauf si `Alt` est maintenu (désactivation temporaire, §8.4).
  À la relâche : **une seule** `DiagramHistory.execute(doc, {type:'update-element', id,
  changes:{x,y}})` avec la position finale déjà magnétisée. Tests composant : un glisser
  complet produit exactement une entrée dans l'historique (pas une par `mousemove`) ; annuler
  après un glisser restitue la position d'avant le geste ; maintenir `Alt` pendant le glisser
  place l'élément à la position brute (non magnétisée).
- [ ] Task 5 — Rendu visuel : contour de sélection (élément sélectionné) et lignes de guide
  d'alignement (pendant un glisser actif seulement) dans le template de `DiagramCanvas.vue`.
  Relève partiellement de l'exception écran-capture (§8.7) pour l'apparence exacte, mais la
  présence conditionnelle est testable : contour rendu seulement si `selectedElementId` est
  défini ; guides rendus seulement pendant un glisser actif avec un alignement détecté.
- [ ] Task 6 — Vérification finale : suite frontend complète verte, `npm run build` propre,
  `Diagrams.vue` toujours non modifié. Clôture ; passation `JOURNAL.md` pour le cycle 5
  (liens, ancrage, routage) : la sélection et le déplacement d'élément existent désormais --
  un lien pourra s'ancrer sur l'élément sélectionné/survolé. Rappel explicite dans la
  passation : redimensionnement/rotation/z-order/duplication/copier-coller/sélection
  multiple/groupes/verrouillage restent hors périmètre de tout le cycle 4, à ne pas oublier
  pour un futur cycle.
