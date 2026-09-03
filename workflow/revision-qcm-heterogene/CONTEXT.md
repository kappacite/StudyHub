# Révision individuelle des QCM dans un ensemble hétérogène

Statut : ouvert
Branche : feature/revision-qcm-heterogene
PR : (aucune)

## Pourquoi

Demande explicite de l'utilisateur (2026-09-03) : « les qcm ne peuvent pas être révisés
tout seul ». Confirmé par investigation (`superpowers:systematic-debugging`, Phase 1 root
cause) : limitation connue, différée deux fois sans être traitée.

## Root cause

Deux endroits concordants :

1. **Backend** (`revision_service.py`, `check_qcm_answer`/`answer_qcm_item`) : ces
   fonctions refusent tout QCM tant que **l'ensemble entier** (`rset.type`) n'est pas
   `"qcm"` homogène — alors que la correction elle-même (`_score_qcm_answer`) ne lit que
   le payload de l'*item*, jamais le type de l'ensemble.
2. **Frontend** (`RevisionStudy.vue`) : le flux générique de révision par item (utilisé
   par tout ensemble hétérogène) exclut systématiquement les items QCM
   (`nonQcmItems = studyItems.filter(i => i.type !== 'qcm')`), avec le message :
   *« Les QCM ne se révisent pas encore individuellement — passez par le passage scoré
   depuis l'ensemble »* — message trompeur : ce « passage scoré » (`/run`) n'existe que
   pour un ensemble **homogène** QCM, jamais accessible depuis un ensemble mixte. Un QCM
   dans un ensemble mixte est donc actuellement irrévisable, sans échappatoire.

Historique : différé explicitement dans `backend-ensembles-heterogenes`
(2026-08-28, doc `docs/superpowers/specs/2026-08-28-backend-ensembles-heterogenes-design.md`,
§ Risque accepté : *« run_qcm nécessite une vraie réflexion... hors périmètre... reviser-hub
s'en chargera »*), puis re-signalé mais non résolu par `reviser-hub` (2026-08-29 — a
seulement durci/vérifié le routage homogène↔hétérogène existant, n'a jamais implémenté de
révision individuelle).

## Comment (approche A retenue, brainstorming en chat le 2026-09-03)

**Approche A confirmée par l'utilisateur.** Le QCM devient un type auto-corrigé de plus,
au même titre que vf/association/ordre :

- Backend : `GRADABLE_TYPES` gagne `"qcm"` ; `check_answer()` gagne une branche `"qcm"`
  qui compare `answer["selected_option_ids"]` (trié) aux ids d'options marquées `correct`
  dans le payload — même comparaison que `_score_qcm_answer` (utilisée par les endpoints
  dédiés `check_qcm_answer`/`answer_qcm_item`, **inchangés**, toujours nécessaires pour le
  mode `/run` homogène). `check_item_answer`/`grade_item` n'ont besoin d'aucune autre
  modification : leur garde `item.type not in GRADABLE_TYPES` suffit.
- Frontend (`RevisionStudy.vue`) : suppression du filtre `nonQcmItems` et du message
  dédié `filterType === 'qcm'` — un QCM sans item dû retombe sur l'état vide générique
  (« Rien à réviser » + bouton « Réviser quand même »), comme tout autre type. Nouveau
  bloc de template QCM (liste de cases à cocher, `v-model` sur les ids d'options
  sélectionnées, bouton Valider) suivant exactement le patron déjà en place pour
  vf/association/ordre : `submitQcm()` → `checkAndAwaitSelfEval({ selected_option_ids })`
  (déjà générique, aucune modification) → correction affichée (✓/✕ par option, **sans**
  poids en points — `RevisionStudy.vue` n'affiche de toute façon aucun score agrégé,
  contrairement à `QcmRun.vue`) → `SelfEvalButtons` → `gradeItem()` (déjà générique).
  Options/correction UI reprises visuellement de `QcmRun.vue` (cases à cocher, ✓/✕),
  sans le compteur de points ni l'écran de score final propres au passage noté.

Hors périmètre, inchangé : `QcmRun.vue`, le mode `/run`, le routage homogène→`/run`
(`focusItemTarget.ts`, `Reviews.vue`), les endpoints `check_qcm_answer`/`answer_qcm_item`.

## Dépendances

Aucune dépendance technique bloquante identifiée. Touche `revision_service.py`
(backend) et `RevisionStudy.vue` (frontend) — pas `QcmRun.vue` ni le mode `/run` homogène,
qui restent inchangés dans les deux approches.
