# Plan — diagrammes-interactions-clavier (Phase 5, cycle 6)

Une case = une tâche atomique. TDD sans exception pour la géométrie et la navigation (§8.7).
Arbitrages, raccourcis retenus : `CONTEXT.md`.

- [x] Task 1 — Placement sans chevauchement, pur, dans `web/src/diagram/layout.ts` :
  `computeSiblingPosition(originBounds, existingBounds[], gap): Point`. Tests : aucune forme
  existante -> position immédiatement à droite de l'origine (`origin.maxX + gap`) ; une forme
  déjà présente à cette position -> décalée encore plus à droite, sans chevauchement avec
  aucune des formes existantes ; plusieurs formes en chaîne -> la nouvelle position ne
  chevauche aucune d'entre elles (pas seulement la première rencontrée).
- [x] Task 2 — Navigation entre éléments, pure, dans `layout.ts` :
  `getAdjacentElementId(elements, currentId, direction: 'next' | 'previous'): string | null`
  (cycle dans l'ordre du tableau, uniquement les éléments `kind: 'shape'`). Tests : suivant/
  précédent sur une liste de 3 -> l'ordre attendu ; suivant depuis le dernier élément revient
  au premier (cyclique) ; `currentId` absent ou liste vide -> `null`, pas d'exception.
- [x] Task 3 — Créer un frère / un enfant / supprimer / naviguer, câblés sur `keydown` (fenêtre
  entière, comme le panoramique) dans `DiagramCanvas.vue` : Entrée = nouvelle forme via
  `computeSiblingPosition` + `add-element` ; Tab = même chose + un `LinkElement` depuis la
  sélection (deux `execute()` séquentiels, cf. arbitrage) ; flèche droite/gauche =
  `getAdjacentElementId`, sélectionne le résultat (ou le premier élément si rien n'était
  sélectionné) ; Suppr/Retour arrière = `remove-element` sur la sélection. Aucun raccourci
  n'agit si rien n'est sélectionné (sauf flèche droite/gauche). Tests composant : Entrée ajoute
  une forme non chevauchante et la sélectionne ; Tab ajoute une forme ET un lien depuis
  l'origine ; Suppr retire la forme sélectionnée du document émis ; flèche droite cycle vers
  l'élément suivant ; aucun raccourci ne fait rien si `selectedElementId` est `null` (sauf
  flèche).
- [x] Task 4 — Renommage (F2) : entrée de texte HTML superposée (positionnée via
  `worldToScreen` sur les coordonnées écran de la sélection), Entrée commet via
  `update-element`, Échap annule sans commande. Tests composant : F2 sur une sélection affiche
  une entrée de texte pré-remplie avec le libellé actuel ; valider avec une nouvelle valeur
  puis Entrée émet le document avec le libellé mis à jour ; Échap ferme l'entrée sans émettre
  de commande.
- [x] Task 5 — Vérification finale : suite frontend complète verte, `npm run build` propre,
  `Diagrams.vue` toujours non modifié. Clôture ; passation `JOURNAL.md` pour le cycle 7
  (interactions tactiles) : rappel de la rugosité assumée du cycle 6 (créer un enfant = deux
  annulations, pas une) à garder en tête si un futur cycle étend le vocabulaire de commandes.
