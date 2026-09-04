# Plan — diagrammes-interactions-tactiles (Phase 5, cycle 7)

Une case = une tâche atomique. TDD sans exception pour la géométrie et les interactions
(§8.7). Arbitrages, limite de vérification sur appareil réel : `CONTEXT.md`.

- [x] Task 1 — Géométrie de pincement, pure, dans `web/src/diagram/touch.ts` :
  `computeDistance(p1, p2): number`, `computeMidpoint(p1, p2): Point`. Tests : distance sur
  un cas simple (3-4-5) ; distance nulle pour deux points identiques ; point médian de deux
  points connus.
- [x] Task 2 — Glisser à un doigt (panoramique du fond / déplacement d'élément) dans
  `DiagramCanvas.vue` : `touchstart`/`touchmove`/`touchend` sur le fond et sur chaque élément,
  même seuil clic/glisser et même logique de magnétisme que la souris (réutilisée telle
  quelle, pas dupliquée). Tests composant : un glisser à un doigt sur le fond modifie le
  `viewBox` ; un glisser à un doigt sur un élément le déplace et émet **une** commande à la
  levée du doigt (pas une par `touchmove`, même invariant que le cycle 4) ; un tap (sans
  déplacement dépassant le seuil) sélectionne/désélectionne comme un clic.
- [ ] Task 3 — Pincer pour zoomer : détecte exactement deux points de contact actifs,
  recalcule le zoom à chaque `touchmove` à partir du ratio de distance courante/initiale,
  centré sur le point médian (réutilise `zoomAt`, Task 1). Tests composant : un pincement qui
  rapproche les deux doigts diminue le zoom, qui les éloigne l'augmente ; le point médian reste
  visuellement stable (même propriété que `zoomAt` déjà testée au cycle 3) ; passer de deux à
  un doigt en cours de geste ne casse rien (retombe sur le glisser à un doigt, pas d'exception).
- [ ] Task 4 — Appui long sur un élément entre en mode création de lien (équivalent tactile de
  `Maj` + glisser, cycle 5) : un contact maintenu sans déplacement au-delà du seuil pendant une
  durée seuil (ex. 500 ms) sur un élément déclenche le même flux que `startLinking` ; un
  déplacement avant l'expiration du délai annule l'appui long et retombe sur le déplacement de
  Task 2. Tests composant (horloge simulée `vi.useFakeTimers`) : un appui long suivi d'un
  glissé vers un autre élément crée un lien ; relâcher avant l'expiration du délai ne crée
  rien ; un déplacement précoce annule l'appui long et déplace l'élément à la place.
- [ ] Task 5 — Vérification finale : suite frontend complète verte, `npm run build` propre,
  `Diagrams.vue` toujours non modifié. Clôture ; passation `JOURNAL.md` pour le cycle 8
  (conteneurs, texte libre, images, LaTeX) -- **rappel explicite à l'utilisateur** : la
  sensation tactile réelle (pincement, confort des cibles ≥ 44 px, absence de conflit avec le
  geste de retour natif du système) n'a pas pu être vérifiée sur un appareil réel dans cet
  environnement, contrairement à l'exigence explicite du §8.4 -- à faire dès qu'un appareil
  tactile réel est disponible.
