# Révision SM-2 — notation manuelle généralisée, QCM libres, planning visible

Statut : clos
Branche : feature/revision-flexibilite
PR : #134

## Pourquoi

4 demandes explicites de l'utilisateur (chat, 2026-08-30) sur le système de révision espacée
(SM-2, `RevisionSet`/`RevisionItem`) :

1. Les boutons de notation manuelle (« À revoir/Moyen/Acquis », façon Anki) n'existent
   aujourd'hui que pour `flashcard`/`definition`. Pour `vf`/`association`/`ordre`/`qcm`, la note
   SM-2 est déduite automatiquement et de façon binaire de la correction (juste → 5, faux → 2
   ou 1) — l'utilisateur veut pouvoir affiner cette note lui-même sur tous les types.
2. Le QCM ne peut être révisé « comme on veut » : confirmé en 3 axes précis (question du chat,
   réponses de l'utilisateur) — bloqué par le filtre d'échéance (rejoint le point 3), pas de
   navigation question par question (tout s'affiche d'un bloc, une seule soumission globale),
   et impossible de rejouer une question déjà répondue avant que son échéance SM-2 recalculée
   ne soit repassée.
3. Impossible de réviser en dehors de l'échéancier SM-2 : le message « rien à réviser
   aujourd'hui » bloque toute révision hors date, y compris à la demande explicite de
   l'utilisateur. Décision actée en chat : la révision libre doit avoir un impact SM-2 normal
   (recalcul standard depuis la date réelle de révision, comme le fait déjà une révision en
   retard) — pas de mode « entraînement » séparé à maintenir.
4. La vue Stats d'un ensemble de révision (`RevisionSetStats.vue`) n'affiche aucune date —
   uniquement des compteurs. L'utilisateur veut y voir la prochaine date de révision optimale
   de l'ensemble.

**Périmètre : le système `RevisionSet`/`RevisionItem` (ensembles de révision) uniquement.**
Les decks de flashcards (`Deck`/`Flashcard`, `StudyDeck.vue`) sont une architecture séparée,
non mentionnée par l'utilisateur (qui parle explicitement de « QCM, ordre etc. ») et déjà
dotés d'une notation manuelle de type Anki — pas touchés ici.

## Comment

Investigation complète (fork, lecture seule) avant écriture du plan — voir le plan détaillé
pour les références fichier:ligne exactes. Décisions de conception actées :

- **Notation manuelle généralisée (point 1)** : conserver la correction automatique (juste/faux
  reste objectif pour vf/association/ordre/qcm — il y a une vraie réponse), mais scinder
  chaque soumission en 2 temps : une vérification sans effet de bord (affiche la correction),
  puis un choix de note manuelle par l'utilisateur qui déclenche la mise à jour SM-2 réelle.
  Le serveur revérifie toujours la correction au moment de la validation (jamais de confiance
  aveugle dans un score client).
- **QCM libre (point 2)** : réponse en 2 parties — (a) le filtre par échéance devient
  contournable (point 3, généralisé) ; (b) `QcmRun.vue` passe d'un flux « tout d'un bloc » à
  une navigation question par question, alignée sur le flux déjà existant de
  `RevisionStudy.vue`. La route de passage groupé (`POST /sets/:id/run`) n'a plus aucun
  consommateur une fois ce flux migré — supprimée plutôt que laissée orpheline (vérifié : seuls
  `QcmRun.vue` et ses tests l'appellent).
- **Révision libre (point 3)** : un paramètre explicite (`include_not_due`) sur la route de
  liste d'étude, activé par un bouton « Réviser quand même » dans l'UI (jamais par défaut) —
  la planification SM-2 réelle continue de fonctionner normalement pour qui ne l'utilise pas.
- **Date optimale (point 4)** : agrégée côté backend (`min(next_review)` sur les items de
  l'ensemble, peut être une date passée si l'ensemble a du retard — information réelle, pas
  masquée) et exposée sur `RevisionSetStats`.

Plan détaillé (8 tâches TDD, exécuté en `subagent-driven-development`) :
`docs/superpowers/plans/2026-08-30-revision-flexibilite.md`.

## Dépendances

Aucune dépendance technique bloquante identifiée. Système indépendant des chantiers
`editeur-notes-notation-ia`/`ecrans-peripheriques-visuels`/`classes-examens-planning` déjà
planifiés (aucun ne touche `revision_service.py`/`RevisionStudy.vue`/`QcmRun.vue`).

## Historique complet des décisions

Voir `workflow/revision-flexibilite/JOURNAL.md`.
