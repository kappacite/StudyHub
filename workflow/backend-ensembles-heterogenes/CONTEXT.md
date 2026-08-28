# Backend — migration ensembles de révision hétérogènes

## Pourquoi

Le canevas Direction A (Claude Design, artefact `366dcc95-8da4-41dd-8bbd-1e625a68e2c5`, 37
artboards) modélise des ensembles de révision hétérogènes : un même `RevisionSet` peut mélanger
plusieurs types d'éléments (Flashcards, QCM, Vrai/Faux, Association, Définition, Ordre), y
compris des flashcards. Décision utilisateur actée le 2026-08-27 : garder le canevas tel quel
plutôt que de le faire correspondre à l'architecture actuelle (homogène, flashcards à part dans
`Deck`) — ça impose une vraie migration de schéma plutôt qu'un ajout.

## Comment

- Déplacer le champ `type` de `RevisionSet` vers `RevisionItem` (le type devient une propriété
  de l'élément, pas de l'ensemble).
- Décider du sort des `Deck`/`Flashcard` existants vis-à-vis de `RevisionItem`.
- Migration Alembic.
- Réécrire `validate_item_payload`/`check_answer`
  (`backend/app/services/revision_service.py`) pour dispatcher sur le type de l'item et non
  plus de l'ensemble.

## Dépendances

Bloquant pour les chantiers `bibliotheque-ensembles` et `reviser-hub`. Aucune dépendance amont.

## Historique complet des décisions

`ETAT.md`, section « Plan global par flux — extension révision hétérogène + assistant IA
(2026-08-27) », flux 1.
