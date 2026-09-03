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

## 2026-09-03 (Task 3 — vérification visuelle réelle)

Backend (`flask run --port=5000`) + frontend (`npm run dev --port 3000`) lancés en local,
connexion via le compte dev seedé (`dev@studyhub.example.com`, mot de passe réinitialisé
localement pour l'occasion — base SQLite de dev uniquement, non versionnée). Ensemble
« Spectroscopie & RMN » (id 3, hétérogène, contient un QCM + un item association).

Constat en cours de route (hors périmètre du diff, non lié à Task 1/2) : les items QCM 4 et 6
en base de dev avaient des options **sans `id`** (`{"text": ..., "correct": ...}`, ids
manquants) — probablement créés avant l'introduction des ids d'option, ou via un script/appel
API direct qui contournait `RevisionItemModal.vue` (celui-ci génère toujours un id à la
création, `OPTION_IDS[i] || String(i)`). Avec `:value="opt.id"` (undefined pour les deux
options), `v-model` sur les checkboxes ne peut pas distinguer les deux — cocher l'une coche
les deux. Corrigé directement en base de dev locale (backfill `id: 'a'/'b'`) pour permettre la
vérification ; aucun changement de code, ce n'est pas un bug introduit par ce chantier (même
pattern déjà utilisé par `QcmRun.vue`, donc latent aussi pour le mode `/run` homogène sur des
items mal formés). À surveiller si des QCM existants en production s'avèrent avoir le même
défaut — hors périmètre ici, pas d'action corrective au-delà du constat.

Parcours réel effectué avec succès : sélection de la bonne réponse (case à cocher) → Valider →
correction affichée (✓ Correct !, options ✓/✕) → auto-évaluation « Facile » → SM-2 mis à jour
en base (`interval=1, ease_factor=2.6, repetitions=1`) et `StudySession` committée
(`item_type='qcm', grade=5`) → progression automatique vers l'item suivant (association) dans
la même session mixte, sans accroc. Non-régression `/run` homogène et suite automatisée déjà
couvertes par les tests (backend 54/54, frontend 538/538) — pas de set QCM homogène en base de
dev pour un test manuel supplémentaire, jugé redondant avec la couverture automatisée
existante.

## 2026-09-03 (clôture)

Les 3 tâches du plan sont complètes et vérifiées (tests + parcours réel). Chantier clos.
