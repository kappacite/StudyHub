# Plan — revision-qcm-heterogene

Une case = une tâche atomique. TDD (skill `cycle-tdd`) : le test précède le code.
Détail de l'approche retenue : `CONTEXT.md`.

- [x] Task 1 — Backend : `"qcm"` rejoint `GRADABLE_TYPES`, `check_answer()` gagne la
  branche de comparaison `selected_option_ids`/options correctes. Tests : correction
  correcte/incorrecte/multi-select, `check_item_answer`/`grade_item` acceptent désormais
  un item `qcm` (ne lèvent plus 400), `grade_item` sur un ensemble hétérogène commet bien
  le SM-2 et la `StudySession` (`item_type='qcm'`). Non-régression explicite : les
  endpoints dédiés `check_qcm_answer`/`answer_qcm_item` gardent leur garde `rset.type`
  telle quelle (test existant `test_check_and_answer_reject_non_qcm_set` ne doit pas
  changer).
- [x] Task 2 — Frontend : bloc de template QCM dans `RevisionStudy.vue` (cases à cocher,
  `submitQcm()`, correction ✓/✕ sans points, branché sur `checkAndAwaitSelfEval`/
  `selfEvalGraded`/`gradeItem` déjà génériques). Suppression du filtre `nonQcmItems` et
  du message dédié `filterType === 'qcm'`. Mise à jour des 3 tests qui vérifiaient
  l'exclusion (`RevisionStudy.spec.ts`) ; le test de routage homogène→`/run` reste
  inchangé.
- [x] Task 3 — Vérification visuelle réelle : réviser effectivement un item QCM à
  l'intérieur d'un ensemble hétérogène dans l'app locale (ensemble « Spectroscopie & RMN »
  déjà seedé, contient un QCM), sélection → validation → correction → auto-évaluation →
  SM-2 mis à jour. Non-régression rapide : le mode `/run` homogène route et score toujours
  correctement. Suite complète (backend + frontend) verte.
