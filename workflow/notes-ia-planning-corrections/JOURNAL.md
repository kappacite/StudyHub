# Journal — notes-ia-planning-corrections

## 2026-09-03 (ouverture)

Chantier ouvert à la demande explicite de l'utilisateur, 6 points groupés en un seul message
(Notation IA, Blurting, Feynman, planning toujours vide, fuite `<!--- sectionbody` dans
l'aperçu bibliothèque, refonte densité éditeur). L'utilisateur a explicitement délégué tous les
arbitrages ("prend les décisions d'arbitrage par toi-même, ne me demande rien, je vais dormir")
— aucune question en chat prévue sur ce chantier, toutes les décisions sont actées et
documentées dans `CONTEXT.md`.

Investigation complète avant tout code :
- Canevas relu en direct dans le navigateur (artefact Claude Design, contenu chargé
  dynamiquement — capture zoomée par artboard) pour Notation, Blurting, Feynman.
- Root cause du planning vide identifié par lecture de `planning_service.py` :
  `Flashcard`/`Deck` uniquement, jamais `RevisionItem`/`RevisionSet` (devenu le mode d'étude
  principal). Même classe de bug que celui trouvé pendant `reviser-hub`.
- Root cause de la fuite `<!--- sectionbody` identifié : `noteExcerpt()` (`Binders.vue`) ne
  nettoie pas les commentaires HTML, seulement un jeu fixe de caractères Markdown. Recherche
  exhaustive : ce marqueur ne vient d'aucun service IA ni template du dépôt — contenu collé par
  l'utilisateur depuis une source externe.
- `Blurting.vue` et `NoteFeynman.vue` lus en entier et comparés à leur canevas respectif.
  Feynman déjà proche (juste le format du score à harmoniser). Blurting largement divergent
  (structure) — arbitrage : ne pas supprimer la génération/import de flashcards (fonctionnalité
  réelle, perte de fonctionnalité déjà traitée comme défaut Critical dans un chantier
  précédent), retoner la carte d'analyse primaire pour suivre le canevas et conserver le reste
  en section secondaire.
- `NoteEdit.vue` (mode édition + lecture) lu en entier : 9 contrôles en ligne 1 de l'en-tête
  d'édition, 5 groupes en ligne 2. Pas de canevas cible strict pour la densité — refonte par
  jugement UX (regroupement par fréquence d'usage, aucune fonction supprimée).

Plan en 9 tâches (détail : `PLAN.md`). Prochaine action : Task 1 (backend, planning vide).

## 2026-09-03 (Task 1 — backend, planning vide)

`RevisionItemDAO.get_items_due_between()` (nouveau, symétrique de
`FlashcardDAO.get_cards_due_between`) + `PlanningService.get_calendar()` agrège désormais
`RevisionItem` en plus de `Flashcard`, `breakdown` généralisé (`BreakdownItemSchema` :
`kind`/`id`/`name`/`count`, remplace `DeckBreakdownSchema`). `advance_review_set()` (nouveau,
symétrique de `advance_review`) + route `/planning/advance` accepte désormais `set_id` en plus
de `deck_id`. Bug trouvé et corrigé au passage : `app/schemas/__init__.py` réexportait encore
l'ancien nom `DeckBreakdownSchema` (cassait l'import de tout le module schemas au démarrage),
couvert par un test de non-régression dédié. Tests : 22 tests planning (dont 8 nouveaux :
isolation `user_id` sur les `RevisionItem`, jour mixte deck+ensemble, `advance_review_set`,
export du barrel). Suite complète backend (hors `test_pdfs.py`/`test_import.py`, échecs
Windows préexistants sans rapport, cf. journal `revision-qcm-heterogene`) : 100% verte.
Prochaine action : Task 2 (frontend, routage planning selon le type d'item).
