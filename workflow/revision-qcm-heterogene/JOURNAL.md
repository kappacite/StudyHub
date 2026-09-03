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

## 2026-09-03 (Task 1 — backend)

`GRADABLE_TYPES` gagne `"qcm"` ; `check_answer()` gagne la branche `"qcm"` (comparaison
tout-ou-rien des `selected_option_ids` triés contre les options `correct` du payload, même
règle que `_score_qcm_answer`). Tests ajoutés : `test_revision_service.py` (nouveau, tests
unitaires purs de `check_answer`/`GRADABLE_TYPES` sans Flask/DB), `test_revision.py`
(scénario bout en bout QCM dans ensemble hétérogène : check → grade → SM-2/StudySession),
`test_revision_check_grade_split.py` (cas `"qcm"` ajouté à `GRADABLE_CASES`, paramétré avec
les autres types). Non-régression vérifiée : `test_revision_qcm.py` (endpoints dédiés
`check_qcm_answer`/`answer_qcm_item`, garde `rset.type` inchangée) passe toujours. Suite
`test_revision*.py` : 54 tests verts. Prochaine action : Task 2 (frontend).

## 2026-09-03 (Task 2 — frontend)

`RevisionStudy.vue` : nouveau bloc de template QCM (cases à cocher `v-model="qcmSelected"`,
bouton Valider → `submitQcm()` → `checkAndAwaitSelfEval({ selected_option_ids })`, correction
✓/✕ par option sans poids en points, `SelfEvalButtons` → `gradeItem()`), repris visuellement
de `QcmRun.vue` sans le compteur de points ni l'écran de score final. Suppression du filtre
`nonQcmItems` dans `applyItemFilter()` et du message dédié `filterType === 'qcm'` /
bouton "Réviser quand même" masqué pour ce filtre dans l'état vide — un QCM sans item dû
retombe désormais sur l'état vide générique comme tout autre type. Tests (TDD, rouge vérifié
avant implémentation) : 3 tests d'exclusion mis à jour en tests d'inclusion
(`RevisionStudy.spec.ts`), 1 test ajouté pour le flux check/grade qcm complet (sélection →
check → auto-éval → grade). Non-régression : redirection `/run` pour ensemble homogène qcm
inchangée, routage `?type=` toujours fonctionnel. Suite complète : 538 tests frontend verts,
`npm run build` (typecheck) OK. Prochaine action : Task 3 (vérification visuelle réelle).
