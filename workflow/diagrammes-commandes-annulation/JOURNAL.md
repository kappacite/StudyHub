# Journal — diagrammes-commandes-annulation

## 2026-09-03 (ouverture)

Chantier ouvert immédiatement après la clôture de `diagrammes-modele-document` (PR #145
mergée) — l'utilisateur a demandé de poursuivre tous les cycles restants (« Fais tout »).
Cycle 2/14 de la refonte Phase 5 des diagrammes : commandes d'édition + annulation, testées
par propriété (§8.7). Détail et arbitrages : `CONTEXT.md`. Plan en 5 tâches : `PLAN.md`.
Prochaine action : Task 1 (`fast-check`).

## 2026-09-03 (Task 1+2 — fast-check, invariant d'annulation écrit en premier)

`fast-check` ajouté en devDependency (aucune lib de test par propriété existante). Invariant
d'annulation écrit dans `web/tests/diagram/history.property.spec.ts` **avant**
`commands.ts`/`history.ts` (§8.7 : « il doit être écrit en premier ») — rouge confirmé
(imports non résolus, `commands.ts`/`history.ts` n'existent pas encore). Générateur : pool
fixe de 3 ids candidats (pas `fc.uuid()`) pour que `remove-element`/`update-element` ciblent
souvent un élément réellement présent plutôt que systématiquement un no-op sur id absent.
Prochaine action : Task 3 (`Command`/`applyCommand`).
