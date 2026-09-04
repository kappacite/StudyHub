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
