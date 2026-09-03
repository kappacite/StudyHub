# Plan — diagrammes-commandes-annulation (Phase 5, cycle 2)

Une case = une tâche atomique. TDD sans exception (§8.7). Arbitrages : `CONTEXT.md`.

- [x] Task 1 — Ajout de `fast-check` en devDependency (`npm install -D fast-check`). Aucun
  test propre à cette tâche (installation de dépendance) ; vérifiée par l'usage en Task 2.
- [x] Task 2 — Invariant d'annulation testé par propriété, **écrit en premier** (§8.7). Dans
  `web/tests/diagram/history.property.spec.ts` : générateur `fast-check` de séquences
  arbitraires de `Command` (add/remove/update sur des éléments générés), propriété : pour
  toute séquence exécutée puis intégralement annulée, le document final est structurellement
  identique (`toEqual`) au document initial. Ce test doit échouer avant l'écriture de
  `commands.ts`/`history.ts` (rouge confirmé), puis passer une fois Tasks 3-4 faites.
- [ ] Task 3 — `Command` (union `add-element`/`remove-element`/`update-element`) et
  `applyCommand(doc, command): DiagramDocumentV1` dans `web/src/diagram/commands.ts`, pure
  (jamais de mutation du document ou d'un élément existant). Tests unitaires ciblés (en plus
  du test de propriété de Task 2) : `add-element` ajoute en fin de tableau (ordre = z-order,
  cf. cycle 1) ; `remove-element` sur un id absent est un no-op (pas d'exception) ;
  `update-element` fusionne les champs donnés sans toucher aux autres, y compris quand l'id
  est absent (no-op).
- [ ] Task 4 — `DiagramHistory` dans `web/src/diagram/history.ts` : `execute(doc, command)`
  (empile `{command, before: doc}`, vide la pile de rétablissement, retourne le nouveau
  document), `undo(current)` (dépile, retourne le document `before` capturé, empile côté
  rétablissement), `redo(current)` (symétrique). Tests : `undo` sans historique est un no-op
  (retourne `current` inchangé) ; un `execute` après un `undo` vide bien la pile de
  rétablissement (rejouer un `redo` après une nouvelle commande ne doit pas restaurer une
  branche annulée) ; `redo` après `undo` restitue exactement le document d'après capturé.
- [ ] Task 5 — Vérification finale : suite frontend complète verte (property test inclus,
  configurer un nombre de runs `fast-check` raisonnable pour ne pas ralentir la CI), `npm run
  build` propre, `Diagrams.vue` toujours non modifié (`git diff` de contrôle). Clôture du
  chantier ; passation dans `JOURNAL.md` pour le cycle 3 (canevas/pan/zoom) : `applyCommand`
  et `DiagramHistory` sont le socle sur lequel les gestes de canevas s'appuieront (chaque
  geste utilisateur = une commande exécutée via `DiagramHistory.execute`).
