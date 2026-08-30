# Journal — revision-flexibilite

## 2026-08-30 (ouverture du chantier)

4 demandes explicites de l'utilisateur sur le système de révision SM-2 : notation manuelle
généralisée (actuellement déduite automatiquement pour vf/association/ordre/qcm), révision QCM
plus libre, révision possible en dehors de l'échéancier (« rien à réviser aujourd'hui »),
prochaine date de révision optimale visible dans les stats d'un ensemble.

Investigation complète faite en fork (lecture seule) sur `main` à jour avant d'écrire le plan :
notation manuelle déjà présente pour flashcard/definition uniquement (`RevisionStudy.vue`) ;
vf/association/ordre auto-gradés côté backend (`grade_item`, note binaire 5/2) ; qcm auto-gradé
en lot (`run_qcm`, note binaire 5/1), seul point d'entrée pour ce type, sans navigation
question par question ; filtre d'échéance unique et centralisé côté DAO
(`get_items_to_study`, `next_review <= now`), déjà contourné pour les ensembles partagés
(`get_by_set`, jamais pour le propriétaire lui-même) ; stats d'ensemble n'affichent aucune date,
uniquement des compteurs, alors que `RevisionItem.next_review` existe déjà en base.

2 questions de clarification posées en chat (`AskUserQuestion`) avant d'écrire le plan
exécutable :
- Le blocage QCM couvre en réalité 3 problèmes distincts (confirmé par l'utilisateur, réponse
  multiple) : le filtre d'échéance (réglé par le point 3, généralisé), l'absence de navigation
  question par question, et l'impossibilité de rejouer une question déjà répondue avant son
  échéance recalculée — les 3 sont donc dans le périmètre de ce chantier.
- La révision libre doit avoir un impact SM-2 normal (recalcul standard depuis la date réelle
  de révision, comme une révision en retard le fait déjà) — pas de mode « entraînement » séparé
  à maintenir. Décision confirmée par l'utilisateur (option recommandée).

Décisions de conception actées (détail complet : `CONTEXT.md`) : scission check/commit pour
toute notation manuelle sur un type auto-corrigé (le serveur revérifie toujours la correction
au moment de la validation finale — jamais de confiance dans un score client) ; suppression du
passage QCM groupé (`run_qcm`/`POST /sets/:id/run`) une fois la navigation question par
question en place, plutôt que laissé en code mort (vérifié : aucun autre appelant) ; date
optimale = `min(next_review)` sur tous les items de l'ensemble, y compris en retard (information
réelle, pas masquée).

Périmètre : `RevisionSet`/`RevisionItem` uniquement — les decks de flashcards
(`Deck`/`Flashcard`, architecture séparée, déjà dotés d'une notation manuelle) ne sont pas
mentionnés par l'utilisateur et restent hors scope.

Plan détaillé (8 tâches TDD) : `docs/superpowers/plans/2026-08-30-revision-flexibilite.md`.
Branche `feature/revision-flexibilite` créée depuis `main` à jour (worktree
`.worktrees/revision-flexibilite`). Chantier `ouvert`. Exécution démarrée en
`subagent-driven-development`, suite ci-dessous.

## 2026-08-30 (8 tâches exécutées, vérification visuelle faite, chantier prêt à clôturer)

Les 8 tâches du plan exécutées via `subagent-driven-development` (implémenteur frais + revue
par tâche + revue finale à venir). Détail complet dans le ledger
`.superpowers/sdd/2026-08-30-revision-flexibilite/progress.md`.

- Task 1 (commit `e727f1d`) : scission check/grade pour vf/association/ordre — `score` fourni
  par l'appelant pilote SM-2, `is_correct` toujours recalculé serveur en défense en profondeur.
- Task 2 (commit `52f5a44`) : même principe pour le QCM, par question — suppression complète du
  passage groupé (`run_qcm`/`POST /sets/:id/run`) devenu mort. L'implémenteur a lui-même trouvé
  et migré 2 fichiers de test non prévus par le brief qui dépendaient encore de l'ancienne
  route (vérifié fidèle par le reviewer : les métriques de stats ne dépendent que de `grade`,
  jamais de `cards_correct`).
- Task 3 (commit `02f897b` + 2 tours de correction `bd8b1d5`/`b6018d7`) : paramètre
  `include_not_due`. 2 tours de correction nécessaires — tous deux sur le MÊME test de
  non-régression élève (jamais sur le code de production, resté correct dès le premier jet) :
  d'abord un stub sans assertion remplacé par un vrai test, puis un bug d'authentification
  (`register` au lieu de `login`) jamais détecté faute d'avoir exécuté pytest avant de rapporter
  DONE — leçon retenue et appliquée explicitement aux briefs des tâches suivantes (« n'affirme
  jamais DONE sans avoir vu une sortie verte de tes propres yeux »).
- Task 4 (commit `798173d`) : agrégat `next_review_at` (min sur tous les items, y compris en
  retard, jamais masqué) dans les stats d'ensemble.
- Task 5 (commit `80df14b`) : notation manuelle vf/association/ordre dans `RevisionStudy.vue`,
  composant `SelfEvalButtons.vue` extrait et réutilisé (évite une 5e duplication). Déviation
  assumée par l'implémenteur sur `correctCount` (reflète la correction réelle, pas le score
  choisi) confirmée juste par le reviewer et alignée avec le principe déjà appliqué côté
  backend.
- Task 6 (commit `77cc51e`, tâche la plus grosse et la plus risquée) : réécriture complète de
  `QcmRun.vue` en navigation question par question, score final reconstruit côté client,
  bouton « Réviser quand même ». Code mort (`runQcm`/`RunAnswer`/`RunResult`) confirmé
  intégralement supprimé par grep repo entier.
- Task 7 (commit `d1afc38`) : bouton « Réviser quand même » sur `RevisionStudy.vue` + date
  optimale affichée dans `RevisionSetStats.vue`, masquée pour un ensemble vide.
- Task 8 : vérification visuelle réelle (environnement natif, backend SQLite direct sans
  `flask run`, frontend Vite — données de test créées via l'API couvrant vf/association/ordre/
  qcm avec des échéances variées : future, due maintenant, en retard, ensemble vide). Les 4
  demandes de l'utilisateur confirmées fonctionnelles en direct dans le navigateur (capture
  d'écran à chaque étape) : boutons de notation manuelle après correction (pas avant) sur les 4
  types ; QCM en navigation question par question ; « Réviser quand même » fonctionnel sur
  `RevisionStudy.vue` ET `QcmRun.vue`, y compris pour rejouer une question déjà répondue ; date
  optimale affichée dans les stats (future, passée pour un ensemble en retard — non masquée —,
  absente pour un ensemble vide). Vérifié aussi en mobile 375px + mode sombre. Suite complète
  re-exécutée en clôture : 424/424 tests frontend, 335/340 backend (5 échecs pré-existants
  `test_import.py`, verrou fichier Windows, sans rapport avec ce chantier).

Environnement natif de vérification démonté. Les 8 tâches sont marquées complètes dans
`PLAN.md`. Reste : revue finale de branche complète (`subagent-driven-development`), puis
clôture (`gestion-chantier`).
