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
