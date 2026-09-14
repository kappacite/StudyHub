# Journal — diagrammes-interactions-tactiles

## 2026-09-04 (ouverture)

Chantier ouvert immédiatement après la clôture de `diagrammes-interactions-clavier` (PR #150
mergée). Cycle 7/14 — `DiagramCanvas.vue` n'écoute que des événements souris jusqu'ici. Le
`<svg>` porte déjà `touch-none` depuis le cycle 3 (aucun conflit avec le défilement/geste de
retour natif, déjà en place). Arbitrage : écouteurs tactiles additifs (pas de bascule vers
Pointer Events, trop large surface de changement pour un seul chantier) réutilisant la même
logique de décision que la souris. Limite honnête documentée : aucun appareil tactile réel
disponible dans cet environnement, la sensation réelle reste non vérifiée malgré l'exigence du
§8.4 -- signalé à l'utilisateur en clôture, pas dissimulé. Plan en 5 tâches : `PLAN.md`.
Prochaine action : Task 1 (géométrie de pincement).

## 2026-09-04 (Task 1 — géométrie de pincement)

`web/src/diagram/touch.ts` : `computeDistance`, `computeMidpoint`. 3/3 tests verts. Prochaine
action : Task 2 (glisser à un doigt).

## 2026-09-04 (Task 2 — glisser à un doigt)

Refactor préalable (sans régression, 27/27 déjà verts) : la décision magnétisme/grille de
`onElementMouseDown` extraite dans `computeSnappedElementPosition`, réutilisée telle quelle
par le nouveau `onElementTouchStart` (Task 2) -- pas de duplication de cette logique entre
souris et tactile. `onBackgroundTouchStart` : répartiteur qui annule le geste tactile
précédent (`activeTouchCleanup`) avant d'en démarrer un nouveau à chaque `touchstart` -- prépare
la transition 1 doigt (panoramique, cette tâche) -> 2 doigts (pincement, Task 3) sans état
incohérent. `onElementTouchStart` : même seuil clic/glisser et même commande unique à la levée
du doigt que la souris (cycle 4). 31/31 tests composant verts, 93/93 tests diagrammes.
Prochaine action : Task 3 (pincer pour zoomer).

## 2026-09-04 (Task 3 — pincer pour zoomer)

`startPinchZoomTouch` : zoom incrémental (ratio de distance depuis le dernier `touchmove`,
pas depuis le début du geste) recentré sur le point médian courant à chaque mouvement --
réutilise `zoomAt` (cycle 3) tel quel. `onBackgroundTouchStart` étendu pour brancher sur le
pincement quand `touches.length === 2`. Limite documentée (pas testée, hors périmètre) : lever
un seul doigt pendant un pincement à deux doigts nettoie le geste sans reprendre
automatiquement un panoramique à un doigt pour le doigt restant -- il faut lever puis
retoucher. 34/34 tests composant verts, 96/96 tests diagrammes. Prochaine action : Task 4
(appui long -> création de lien).

## 2026-09-14 (Task 4 — appui long -> création de lien)

Appui long tactile (500 ms) implémenté sur les éléments SVG (`startLinkingTouch` et gestionnaire
de délai avec annulation sur mouvement précoce). Tracé fantôme et émission de commande `add-element`
au relâchement sur une cible. 37/37 tests unitaires `DiagramCanvas.spec.ts` passants (simulés avec
`vi.useFakeTimers`). Prochaine action : Task 5 (vérification finale).

## 2026-09-14 (Task 5 — vérification finale & clôture)

Suite frontend 671/671 tests verts, build de production propre (`npm run build` en 2.01s).
Rappel explicite : la sensation tactile réelle (pincement, confort des cibles ≥ 44 px, absence
de conflit avec le geste de retour natif du système) n'a pas pu être testée sur un appareil
physique dans cet environnement, à tester dès qu'un écran tactile est disponible.
Cycle 7 terminé, prêt pour fusion ou enchaînement sur le Cycle 8.
