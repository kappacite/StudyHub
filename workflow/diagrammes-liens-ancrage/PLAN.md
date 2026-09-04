# Plan — diagrammes-liens-ancrage (Phase 5, cycle 5)

Une case = une tâche atomique. TDD sans exception pour la géométrie (§8.7). Arbitrages :
`CONTEXT.md`.

- [x] Task 1 — Ancrage, pur, dans `web/src/diagram/anchoring.ts` :
  `computeAnchorPoint(bounds, towardPoint): Point` (point où le rayon centre→`towardPoint`
  croise le rectangle englobant). Tests : cible directement à droite -> ancrage au milieu du
  bord droit ; cible directement au-dessus -> ancrage au milieu du bord haut ; cible = centre
  exact -> retourne le centre (dégénère sans `NaN`, pas de division par zéro qui se propage) ;
  pour un carré, une cible en diagonale à 45° -> ancrage exactement au coin.
- [x] Task 2 — Rendu des liens dans `DiagramCanvas.vue` : pour chaque élément `kind: 'link'`
  du document (pas seulement `visibleElements` -- un lien peut relier deux formes dont une
  hors-champ), résout `fromId`/`toId` dans `props.document.elements`, calcule les deux points
  d'ancrage (Task 1) l'un vers l'autre, trace une `<line>` (ou `<polyline>` si
  `routingPoints` non vide) avec pointillé selon `dashed` et un marqueur de flèche selon
  `arrow`. Un lien dont `fromId`/`toId` ne résout à aucune forme est ignoré silencieusement
  (pas d'exception). Tests composant : un lien valide produit un élément de tracé visible ;
  un lien orphelin (id absent) ne casse pas le rendu et ne produit aucun tracé ; un lien avec
  des `routingPoints` passe par ces points (pas une ligne droite directe).
- [ ] Task 3 — Création d'un lien par geste : `Maj` maintenu + glisser depuis une forme vers
  une autre crée un `LinkElement` via `DiagramHistory.execute({type:'add-element', ...})` à la
  relâche, uniquement si le point de relâche est au-dessus d'une forme différente de la forme
  de départ. Sans `Maj`, le comportement reste le déplacement du cycle 4 (inchangé). Tests
  composant : glisser avec `Maj` d'une forme vers une autre ajoute un élément `kind: 'link'`
  au document émis, avec le bon `fromId`/`toId` ; relâcher hors de toute forme (ou sur la
  forme de départ) ne crée rien ; sans `Maj`, un glisser reste un déplacement (non-régression
  du cycle 4).
- [ ] Task 4 — Vérification finale : suite frontend complète verte, `npm run build` propre,
  `Diagrams.vue` toujours non modifié. Clôture ; passation `JOURNAL.md` pour le cycle 6
  (interactions clavier) : rappel des exclusions de ce cycle (édition de points de routage,
  nettoyage des liens orphelins) à ne pas oublier pour de futurs cycles.
