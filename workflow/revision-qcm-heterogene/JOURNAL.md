# Journal — revision-qcm-heterogene

## 2026-09-03 (ouverture)

Chantier ouvert à la demande explicite de l'utilisateur (« les qcm ne peuvent pas être
révisés tout seul »).

Investigation (`superpowers:systematic-debugging`, Phase 1) : root cause identifié avant
tout code — garde backend sur `rset.type` (au lieu de `item.type`, déjà correct) dans
`check_qcm_answer`/`answer_qcm_item`, et `RevisionStudy.vue` qui exclut systématiquement
les items QCM d'un ensemble hétérogène, avec un message renvoyant vers un mode (`/run`)
inaccessible pour ce genre d'ensemble. Limitation connue, différée deux fois
(`backend-ensembles-heterogenes` 2026-08-28, `reviser-hub` 2026-08-29) sans être traitée.

Brainstorming (`superpowers:brainstorming`, path architectural — touche un service partagé
et restructure comment un type d'item s'intègre dans deux flux de révision) : 2 approches
présentées en chat, **A retenue** (étendre le flux générique déjà utilisé pour
vf/association/ordre, `GRADABLE_TYPES`/`check_item_answer`/`grade_item`) plutôt que
d'assouplir les endpoints QCM dédiés + construire une UI de réponse QCM séparée dans
l'écran d'étude. Détail complet des deux approches et de la décision : `CONTEXT.md`.

Plan en 3 tâches (backend, frontend, vérification). Prochaine action : Task 1.
