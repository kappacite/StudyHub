# Plan — révision SM-2 : notation manuelle généralisée, QCM libres, planning visible

Contexte complet : `workflow/revision-flexibilite/CONTEXT.md`. Pas de spec séparée pour ce
chantier (investigation faite en fork + décisions actées directement en chat, résumées dans
CONTEXT.md) — ce plan est la référence exécutable, la binding authority en cas d'ambiguïté est
CONTEXT.md.

## Global Constraints

- TDD sans exception (phase ≥ 3) : test avant code, il doit échouer pour la bonne raison avant
  le correctif.
- Backend : flux `route → service → DAO → model`, jamais de SQL/ORM direct en service, jamais
  de commit manuel hors DAO (le DAO déjà en place ici committe via `self._item_dao.db.commit()`
  — ne pas changer ce pattern, juste l'étendre).
- **Le serveur revérifie toujours la correction au moment de la validation finale** (jamais de
  confiance dans un booléen ou un score envoyé par le client comme unique source de vérité sur
  ce qui est objectivement juste/faux) — seule la note SM-2 elle-même (1-5) est manuelle.
- Aucune régression sur les ensembles partagés (cours) : la branche élève (`rset.user_id !=
  user_id`) ne touche jamais l'échéancier SM-2 du propriétaire, seulement sa propre
  `StudySession` — ce garde existant doit survivre à chaque modification de service.
- TypeScript strict, pas de `any`. `<script setup lang="ts">`. Aucune valeur de style brute.
- Pas de code mort laissé en place : si une route/fonction/schéma perd son dernier appelant
  dans ce chantier, elle est supprimée dans le même commit (pas de dépréciation silencieuse).
- Coverage backend ≥ 80 %.

## Task 1 : backend — notation manuelle pour vf/association/ordre (scission check/commit)

**Fichiers** : `backend/app/services/revision_service.py`, `backend/app/schemas/revision_schema.py`,
`backend/app/api/v1/revision.py`, `backend/tests/test_revision.py` (ou un nouveau fichier de
test dédié si plus lisible — au choix de l'implémenteur).

Aujourd'hui, `grade_item()` (revision_service.py:443-497) fait tout en un seul appel : corrige
la réponse (`check_answer(item.type, item.payload, answer)`), déduit une note binaire
(`grade = 5 if is_correct else 2`), met à jour SM-2 et écrit la `StudySession`. Il faut scinder
ceci en 2 appels pour permettre à l'utilisateur de voir la correction AVANT de choisir sa note :

1. **Nouvelle méthode `check_item_answer(self, user_id, set_id, item_id, answer) -> bool`**
   (lecture seule, aucune écriture DB) : réutilise `self._get_item_or_404(item_id, set_id,
   user_id, write_required=False)` et `check_answer(item.type, item.payload or {}, answer or
   {})` exactement comme aujourd'hui, vérifie `item.type in GRADABLE_TYPES` (même erreur que
   l'existant sinon), retourne juste le booléen `is_correct`. Zéro `db.add`/`db.commit`.
2. **`grade_item()` modifiée** : signature devient
   `grade_item(self, user_id, set_id, item_id, answer: dict, score: int, duration_seconds: int = 0) -> RevisionGradeResult`
   — `score` n'est plus déduit, il est fourni par l'appelant (1-5, la note choisie par
   l'utilisateur après avoir vu la correction). Le corps recalcule `is_correct` lui-même
   (defense-in-depth, cf. Global Constraints) via `check_answer(...)`, utilise ce
   `is_correct` recalculé pour `cards_correct` de la `StudySession` (comme aujourd'hui), mais
   utilise `score` (et non plus un binaire déduit) dans l'appel à `calculate_sm2(...)`. Le
   reste (garde propriétaire/élève sur ensemble partagé, écriture `StudySession`) est inchangé.
   Le retour `RevisionGradeResult{correct, item}` ne change pas de forme.

**Schémas** (`revision_schema.py`) :
- Nouveau `RevisionCheckRequest(BaseModel): answer: dict[str, Any]` (même shape de `answer` que
  `RevisionGradeRequest`, réutiliser le même commentaire de documentation par type).
- Nouveau `RevisionCheckResult(BaseModel): correct: bool`.
- `RevisionGradeRequest` gagne `score: int = Field(..., ge=1, le=5)` (champ requis, pas de
  défaut — le point de la scission est que le client DOIT fournir la note choisie).

**Routes** (`revision.py`) :
- Nouvelle `POST /sets/<int:set_id>/study/check/<int:item_id>` → `check_item_answer` → 200,
  `RevisionCheckResult`.
- Route existante `POST /sets/<int:set_id>/study/grade/<int:item_id>` : le handler passe
  désormais `data.score` à `revision_service.grade_item(...)` en plus des paramètres actuels.

**Tests** : couvrir au minimum — `check_item_answer` ne touche pas `next_review`/`ease_factor`
ni la base `StudySession` (aucune ligne créée) pour vf/association/ordre, juste/faux ; `type`
non-gradable rejeté (422/ValidationError, comme l'existant) ; `grade_item` avec un `score`
fourni explicitement met à jour SM-2 avec CETTE note (pas une valeur déduite) même quand la
réponse est fausse (ex: faux + score=3 → SM-2 calculé avec score=3, pas avec le score=2
qu'aurait déduit l'ancien code) ; `cards_correct`/`correct` restent basés sur la correction
réelle recalculée côté serveur, indépendamment du `score` fourni ; non-régression sur la
branche « ensemble partagé » (élève : aucune mise à jour SM-2, `StudySession` bien écrite).
`RevisionGradeRequest` sans `score` → 422 (validation Pydantic).

## Task 2 : backend — QCM par question (check/commit) + suppression du passage groupé

**Fichiers** : `backend/app/services/revision_service.py`, `backend/app/schemas/revision_schema.py`,
`backend/app/api/v1/revision.py`, `backend/tests/test_revision_qcm.py`.

Avant de commencer, vérifier qu'aucun autre appelant que `web/src/views/Reviews/QcmRun.vue` et
`backend/tests/test_revision_qcm.py`/`web/tests/stores/revision.spec.ts` n'utilise `run_qcm`/
`runQcm`/`POST /sets/:id/run` (déjà vérifié par le contrôleur au moment d'écrire ce plan — à
reconfirmer avant de supprimer, le code a pu bouger). Si confirmé : le passage groupé est
remplacé, pas gardé en parallèle.

1. **Extraire la logique de correction d'une question** de la boucle actuelle de `run_qcm()`
   (revision_service.py:381-405) dans une fonction/méthode privée réutilisable, ex.
   `_score_qcm_answer(item: RevisionItem, selected_option_ids: list[str]) -> tuple[bool, int, int, list[str]]`
   retournant `(is_correct, earned, points, correct_option_ids)` — logique inchangée
   (comparaison des ids triés, tout-ou-rien sur multi-sélection, `points = payload.get("points", 1)`).
2. **Nouvelle méthode `check_qcm_answer(self, user_id, set_id, item_id, selected_option_ids: list[str]) -> RevisionQcmCheckResult`**
   (lecture seule) : vérifie `rset.type == "qcm"` (même erreur que l'existant), récupère l'item
   via `_get_item_or_404`, appelle `_score_qcm_answer(...)`, retourne le résultat SANS écrire
   en base.
3. **Nouvelle méthode `answer_qcm_item(self, user_id, set_id, item_id, selected_option_ids, score: int, duration_seconds: int = 0) -> RevisionQcmCheckResult`**
   (avec effet de bord) : revérifie `_score_qcm_answer(...)` (defense-in-depth), applique
   `calculate_sm2(score=score, ...)` avec le `score` fourni par le client (remplace le
   `grade = 5 if is_correct else 1` actuel) — uniquement si `rset.user_id == user_id` (même
   garde élève/propriétaire que l'existant), écrit une `StudySession` unique pour cette
   question (`cards_reviewed=1`, `cards_correct=1 if is_correct else 0`, `grade=score`,
   `duration_seconds` = celle fournie par le client pour CETTE question — la répartition
   `divmod` du lot disparaît, chaque question a désormais sa propre durée réelle mesurée
   côté frontend, comme `grade_item`/`answer_item` le font déjà).
4. **Supprimer** : `run_qcm()`, la route `POST /sets/<id>/run`, les schémas
   `RevisionRunAnswer`/`RevisionRunRequest`/`RevisionRunQuestionResult`/`RevisionRunResult`
   devenus inutiles (garder seulement ce qui est réutilisé — `_score_qcm_answer` remplace leur
   usage interne).

**Schémas** (`revision_schema.py`) :
- `RevisionQcmAnswerRequest(BaseModel): selected_option_ids: list[str] = []`
- `RevisionQcmCommitRequest(BaseModel): selected_option_ids: list[str] = []; score: int = Field(..., ge=1, le=5); duration_seconds: int = Field(0, ge=0)`
- `RevisionQcmCheckResult(BaseModel): correct: bool; earned: int; points: int; correct_option_ids: list[str]`
- `RevisionQcmAnswerResult(RevisionQcmCheckResult): item: RevisionItemResponse` (hérite des 4
  champs ci-dessus + l'item mis à jour)

**Routes** (`revision.py`) :
- Nouvelle `POST /sets/<int:set_id>/study/qcm-check/<int:item_id>` → `check_qcm_answer` → 200,
  `RevisionQcmCheckResult`.
- Nouvelle `POST /sets/<int:set_id>/study/qcm-answer/<int:item_id>` → `answer_qcm_item` → 200,
  `RevisionQcmAnswerResult`.
- Supprimer `POST /sets/<int:set_id>/run`.

**Tests** (`test_revision_qcm.py`, réécrit sur les 2 nouvelles routes — migrer la SUBSTANCE des
tests existants, pas leur forme batch) : pondération multi-points correcte, tout-ou-rien sur
sélection multiple, `check_qcm_answer` n'écrit rien en base (aucune `StudySession`, aucun
changement de `next_review`), `answer_qcm_item` applique le `score` fourni (pas un binaire
déduit) au calcul SM-2, rejet sur ensemble non-qcm, item_type de la `StudySession` = type réel
de l'item (pas du set), branche élève sur ensemble partagé (aucune mise à jour SM-2). Les tests
de répartition `divmod` du lot (186-332 de l'ancien fichier) sont supprimés — plus pertinents,
chaque question a sa propre durée désormais.

## Task 3 : backend — réviser même si rien n'est dû (`include_not_due`)

**Fichiers** : `backend/app/dao/revision_dao.py`, `backend/app/services/revision_service.py`,
`backend/app/api/v1/revision.py`, `backend/tests/test_revision.py`.

1. `RevisionItemDAO.get_items_to_study(self, set_id: int, include_not_due: bool = False) -> List[RevisionItem]`
   (revision_dao.py:119-128) : construire la requête de base (filtre `set_id`, tri
   `position, id`), n'ajouter le filtre `next_review <= datetime.utcnow()` QUE si
   `include_not_due` est `False`. Quand `True`, retourne tous les items de l'ensemble
   (équivalent de `get_by_set` mais dans la même méthode pour ne pas dupliquer la logique de tri
   — au choix de l'implémenteur : soit un `if`/`else` sur la construction de la query, soit
   déléguer explicitement à `get_by_set` quand `include_not_due=True`).
2. `RevisionService.get_study_items(self, user_id: int, set_id: int, include_not_due: bool = False) -> list[RevisionItemResponse]`
   (revision_service.py:297-306) : transmet `include_not_due` à `get_items_to_study` sur la
   branche propriétaire. La branche élève (`get_by_set`) est déjà non filtrée — inchangée,
   `include_not_due` y est un no-op silencieux (jamais d'erreur si un élève l'envoie).
3. Route `GET /sets/<int:set_id>/study` (revision.py:126-131) : lit
   `request.args.get("include_not_due", "false").lower() == "true"`, le transmet au service.

**Tests** : `get_items_to_study(set_id, include_not_due=True)` retourne un item dont
`next_review` est dans le futur (pas seulement les items dus) ; `include_not_due=False`
(défaut, comportement actuel) reste inchangé — test de non-régression explicite ; le paramètre
query `?include_not_due=true` sur la route est bien transmis de bout en bout (test API, pas
seulement unitaire DAO/service) ; branche élève avec `include_not_due=true` ne casse rien.

## Task 4 : backend — prochaine date de révision optimale dans les stats

**Fichiers** : `backend/app/services/revision_stats_service.py`, `backend/app/schemas/revision_schema.py`,
`backend/tests/test_revision_stats.py`.

1. `_SetAggregate` (revision_stats_service.py:157-173) : ajouter
   `next_review_at: datetime | None = None`.
2. Dans `_aggregate_set()` (boucle ligne 285-324), pour chaque item : mettre à jour
   `agg.next_review_at` au minimum de `item.next_review` rencontré (tous les items, dus ou
   non — une date passée signifie que l'ensemble a du retard, c'est une information réelle à
   ne pas masquer). Pas de filtre `> now` : le champ répond à « quelle est la prochaine
   échéance SM-2 de cet ensemble », qui peut être dans le passé.
3. `RevisionSetStats` (revision_schema.py:226-247) : ajouter `next_review_at: datetime | None = None`.
4. `get_set_stats()` (revision_stats_service.py:352-371) : passer `next_review_at=agg.next_review_at`
   au constructeur de `RevisionSetStats`.

**Tests** : ensemble avec des items à échéances variées → `next_review_at` = la plus proche
(min) ; ensemble sans aucun item (`items_count == 0`) → `next_review_at is None` (pas
d'exception sur un `min()` vide) ; ensemble dont tous les items sont en retard → la date
retournée est bien dans le passé (pas masquée/nullifiée).

## Task 5 : frontend — notation manuelle vf/association/ordre dans `RevisionStudy.vue`

**Fichiers** : `web/src/stores/revision.ts`, `web/src/views/Reviews/RevisionStudy.vue`,
`web/tests/views/Reviews/RevisionStudy.spec.ts`, `web/tests/stores/revision.spec.ts`.

Dépend de Task 1 (contrat backend). Le flux actuel (`submitVf`/`submitAssoc`/`submitOrdre` →
`gradeItem()` → `applyResult(correct)` → phase `'feedback'` → bouton Suivant) devient :

1. **Store** (`revision.ts`) :
   - Nouvelle `checkItemAnswer(setId: number, itemId: number, answer: Record<string, unknown>): Promise<{ correct: boolean }>`
     → `POST /revision/sets/${setId}/study/check/${itemId}`.
   - `gradeItem(setId, itemId, answer, score: number, durationSeconds = 0)` : signature gagne
     le paramètre `score` (obligatoire, positionné avant `durationSeconds`), l'envoie dans le
     corps (`{ answer, score, duration_seconds }`).
2. **`RevisionStudy.vue`** : ajouter une valeur `'self-eval'` au type de `phase` (actuellement
   `'answer' | 'reveal' | 'feedback'`). Nouveau flux pour vf/association/ordre :
   - `submitVf(value)`/`submitAssoc()`/`submitOrdre()` appellent désormais
     `revisionStore.checkItemAnswer(setId, current.value.id, <answer>)`, stockent la réponse
     soumise dans un ref local (ex. `lastAnswer = ref<Record<string, unknown>>({})`, réassigné
     à chaque soumission — nécessaire pour renvoyer la même réponse à l'étape de validation),
     posent `lastCorrect.value = res.correct`, puis `phase.value = 'self-eval'` (au lieu de
     `applyResult` qui posait directement `'feedback'`).
   - En phase `'self-eval'` : afficher le message de correction existant (inchangé, déjà dans
     le template par type) **et** les 3 boutons d'auto-évaluation (même libellés/couleurs/
     `data-test` que ceux déjà utilisés pour flashcard/definition : `self-eval-a-revoir`/
     `self-eval-moyen`/`self-eval-acquis`, scores 1/3/5).
   - Cliquer un bouton auto-éval appelle une fonction commune, ex.
     `selfEvalGraded(score: number)`, qui appelle
     `revisionStore.gradeItem(setId, current.value.id, lastAnswer.value, score, elapsedSeconds())`
     puis pose `if (score >= 3) correctCount.value++` et `phase.value = 'feedback'` (le bouton
     Suivant existant, inchangé, se déclenche déjà sur `phase === 'feedback'`).
   - **Factoriser la duplication** : le bloc de 3 boutons d'auto-évaluation est aujourd'hui
     dupliqué à l'identique entre flashcard et definition (lignes ~119-141 et ~166-184). Ajouter
     ce même bloc une 3e fois (pour vf/association/ordre en phase self-eval) rendrait la
     duplication x4-x6 (chaque type auto-corrigé a sa propre section `v-else-if`) — extraire un
     petit composant local (ex. `web/src/components/revision/SelfEvalButtons.vue`, props
     `disabled?: boolean` si besoin, emit `select: [score: number]`) réutilisé par les 5
     endroits (flashcard, definition, vf, association, ordre). Garder les mêmes `data-test`.
   - Le `flashcard`/`definition` restent sur leur flux actuel (`selfEval(score)` →
     `answerItem()` directement) — pas de check préalable pour eux, ils n'ont pas de correction
     objective, rien à changer côté backend/flux pour ces 2 types.

**Tests** : après soumission d'une réponse vf/association/ordre, les boutons de notation
manuelle apparaissent (et pas le bouton Suivant) ; cliquer un bouton de notation appelle
`gradeItem` avec le score choisi ET la réponse initialement soumise ; le flux avance ensuite
normalement (Suivant/Terminer) ; `correctCount` reflète toujours la correction réelle
(`res.correct` du check), indépendamment du score choisi ensuite.

## Task 6 : frontend — `QcmRun.vue` en navigation question par question + révision libre

**Fichiers** : `web/src/stores/revision.ts`, `web/src/views/Reviews/QcmRun.vue`,
`web/tests/views/Reviews/QcmRun.spec.ts` (créer s'il n'existe pas déjà — vérifier),
`web/tests/stores/revision.spec.ts`.

Dépend de Task 2 (contrat backend) et Task 3 (`include_not_due`). Remplace entièrement le flux
actuel « tout d'un bloc, une soumission globale » par un flux question par question aligné sur
`RevisionStudy.vue` (Task 5) :

1. **Store** : supprimer `runQcm()` (plus d'appelant après cette tâche). Ajouter :
   - `checkQcmAnswer(setId, itemId, selectedOptionIds: string[]): Promise<QcmCheckResult>` →
     `POST /revision/sets/${setId}/study/qcm-check/${itemId}`.
   - `answerQcmItem(setId, itemId, selectedOptionIds, score, durationSeconds = 0): Promise<QcmAnswerResult>`
     → `POST /revision/sets/${setId}/study/qcm-answer/${itemId}`.
   - `fetchStudyItems(setId, includeNotDue = false)` : ajoute `?include_not_due=true` à l'URL
     quand `includeNotDue` est vrai (même changement que Task 5/7 ci-dessous, un seul endroit
     dans le store à modifier, partagé par tous les appelants).
   - Types `QcmCheckResult`/`QcmAnswerResult` (ou noms similaires) reflétant les schémas
     backend de Task 2. Supprimer les types `RunAnswer`/`RunResult` devenus inutiles si plus
     aucun import ne les référence après cette tâche.
2. **`QcmRun.vue`** : remplacer l'affichage « toutes les questions + 1 bouton Valider global »
   par un état `index`/`current` et un `phase` (`'answer' | 'self-eval' | 'feedback'`), sur le
   modèle de `RevisionStudy.vue` :
   - Phase `answer` : la question courante, cases à cocher (markup existant repris pour UNE
     question au lieu d'une boucle sur toutes), bouton « Valider » appelant
     `checkQcmAnswer(...)`.
   - Phase `self-eval` : affiche la correction de CETTE question (bonnes/mauvaises réponses
     cochées, `earned`/`points` — réutiliser le markup déjà existant dans le bloc "Result"
     actuel, ligne 84-103, adapté à une seule question) + les mêmes boutons d'auto-évaluation
     que Task 5 (réutiliser `SelfEvalButtons.vue`).
   - Choisir un score appelle `answerQcmItem(...)`, accumule le résultat dans un tableau local
     (`results: ref<QcmAnswerResult[]>`) pour le récapitulatif final, passe `phase = 'feedback'`
     puis au clic sur Suivant avance `index` (ou termine si dernière question).
   - **Écran final** (actuel bloc "Result", ligne 41-112) : reconstruire `score`/`max_score`/
     `percentage` à partir de la somme des `earned`/`points` accumulés localement (plus de
     réponse batch du backend à consommer) — même présentation visuelle qu'aujourd'hui.
3. **Révision libre** : sur l'état vide (« Aucune question à réviser pour l'instant », ligne
   24-38), ajouter un bouton « Réviser quand même » qui relance `fetchStudyItems(setId, true)`
   et recharge `questions`. Ce changement, une fois `include_not_due=true` posé, couvre aussi
   nativement « rejouer une question déjà répondue » (Task 3 : `get_by_set` ne filtre déjà pas
   par échéance du tout, question déjà répondue incluse).

**Tests** : navigation une question à la fois (une seule question visible en phase answer, pas
tout le lot) ; les boutons de notation apparaissent après le check, avant de passer à la
question suivante ; le score final agrège correctement les réponses individuelles (vérifier sur
un cas multi-questions avec points différents, comme les tests batch existants le faisaient) ;
le bouton « Réviser quand même » sur liste vide relance bien avec `include_not_due=true` et
affiche alors des questions (y compris une question déjà répondue, next_review dans le futur).

## Task 7 : frontend — bouton « Réviser quand même » sur `RevisionStudy.vue` + date optimale dans les stats

**Fichiers** : `web/src/stores/revision.ts` (si pas déjà fait en Task 6),
`web/src/views/Reviews/RevisionStudy.vue`, `web/src/views/Reviews/RevisionSetStats.vue`,
`web/tests/views/Reviews/RevisionStudy.spec.ts`, `web/tests/views/Reviews/RevisionSetStats.spec.ts`.

Dépend de Task 3 (`include_not_due`) et Task 4 (`next_review_at`). Deux changements
indépendants regroupés dans une même tâche (petits, même famille « planning visible ») :

1. **`RevisionStudy.vue`** : même bouton « Réviser quand même » que Task 6, sur l'état vide
   existant (ligne 24-41 — le message actuel distingue déjà `filterType === 'qcm'` d'un cas
   générique ; le bouton s'ajoute au cas générique, pas au message qcm qui redirige déjà
   ailleurs). Au clic : refetch `fetchStudyItems(setId, true)`, réappliquer le même filtrage
   `nonQcmItems`/`filterType` qu'à `onMounted`, relancer `setupItem()` si des items reviennent.
2. **`SetStats` (interface TS, `revision.ts`)** : ajouter `next_review_at: string | null`.
3. **`RevisionSetStats.vue`** : afficher la date, à l'endroit qui semble le plus naturel parmi
   les stats déjà affichées (au choix de l'implémenteur — cohérent avec le reste de l'écran).
   Formater en français (chercher d'abord un utilitaire de date déjà partagé dans le projet
   avant d'en écrire un nouveau ; à défaut, `toLocaleDateString('fr-FR', ...)` inline suffit
   pour un seul usage). Cas `next_review_at === null` (ensemble sans item) : ne pas afficher la
   ligne plutôt qu'une valeur factice — cf. contrainte globale anti-fabrication du projet.

**Tests** : bouton « Réviser quand même » sur `RevisionStudy.vue` déclenche bien un refetch avec
`include_not_due=true` ; `RevisionSetStats.vue` affiche la date quand `next_review_at` est
fourni, n'affiche rien (pas de date factice) quand `null`.

## Task 8 : vérification visuelle réelle + non-régression + clôture

Même discipline que les chantiers précédents (`bibliotheque-redesign`, `reviser-hub`) :
environnement natif (venv backend + Vite frontend, pas de Docker — voir la mémoire
`studyhub-backend-tests-no-docker` si besoin de rappel sur la commande `python` exacte),
données de test créées via l'API couvrant les 4 types auto-corrigés + qcm, avec au moins un
item en retard et un item pas encore dû par ensemble.

Vérifier en direct (pas seulement via les tests unitaires) :
- Chaque type (vf/association/ordre/qcm) montre bien les 3 boutons de notation manuelle après
  correction, et PAS avant.
- QCM se joue question par question, score final correct sur un ensemble multi-questions à
  points hétérogènes.
- « Réviser quand même » fonctionne sur `RevisionStudy.vue` et `QcmRun.vue`, y compris pour
  rejouer une question déjà répondue.
- La révision libre met bien à jour l'échéancier normalement (next_review recalculé, pas un
  mode sans effet).
- `RevisionSetStats.vue` affiche la date optimale, absente pour un ensemble vide.
- Non-régression : flashcard/definition (self-eval direct, inchangé), ensemble partagé (élève
  ne touche jamais l'échéancier du propriétaire), stats existantes (grade_distribution,
  due_count, etc.) inchangées par l'ajout de `next_review_at`.

Puis : mise à jour `workflow/revision-flexibilite/{PLAN,JOURNAL}.md` + `workflow/JOURNAL.md`,
commit, revue finale de branche (modèle le plus capable), boucle de correction si besoin, puis
clôture `gestion-chantier` (push demandé à l'utilisateur, jamais exécuté par l'agent — PR,
attente CI, merge, PR de clôture de suivi comme pour `bibliotheque-redesign`/`reviser-hub`).
