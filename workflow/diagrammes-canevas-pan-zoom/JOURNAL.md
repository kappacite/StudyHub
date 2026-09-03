# Journal — diagrammes-canevas-pan-zoom

## 2026-09-04 (ouverture)

Chantier ouvert immédiatement après la clôture de `diagrammes-commandes-annulation` (PR #146
mergée). Cycle 3/14 — premier cycle produisant un rendu visuel, mais toujours non routé dans
l'application (le socle se construit en isolation depuis le cycle 1). Investigation en direct
(Chrome) a corrigé la caractérisation de l'existant : hybride DOM+SVG, pas SVG pur. Tentative
de mesure de FPS par simulation d'événements abandonnée (non fiable dans cet environnement,
détail : `CONTEXT.md`) — sans impact sur ce cycle puisque le panoramique/zoom est un coût
constant indépendant du nombre d'éléments une fois le rendu borné à la fenêtre de vue.
Décision : SVG (pas canevas 2D), justifiée par les besoins LaTeX/édition de texte/accessibilité
du module, pas par un chiffre de fps. Plan en 6 tâches : `PLAN.md`. Prochaine action : Task 1
(modèle de caméra).

## 2026-09-04 (Task 1+2 — modèle de caméra, panoramique, zoom centré)

`web/src/diagram/camera.ts` : `Camera {x,y,zoom}` (convention : `x`/`y` = coordonnées monde
au centre de la fenêtre de vue, `zoom` = pixels-écran par unité-monde), `screenToWorld`/
`worldToScreen` (rondtrip vérifié), `panBy` (delta écran converti en delta monde selon le
zoom courant), `zoomAt` (zoom centré sur un point écran, le point ciblé reste fixe en
coordonnées monde -- vérifié par test). 5/5 tests verts. Prochaine action : Task 3 (rendu
borné à la fenêtre de vue).

## 2026-09-04 (Task 3 — rendu borné à la fenêtre de vue)

`web/src/diagram/viewport.ts` : `getVisibleWorldBounds` (rectangle monde visible depuis la
caméra), `elementBounds` (boîte englobante x/y/width/height), `cullElements` (intersection,
pas inclusion stricte -- un élément partiellement visible reste affiché). 8/8 tests verts.
Prochaine action : Task 4 (recadrage sur tout le contenu).
