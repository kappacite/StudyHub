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

## 2026-09-03 (Task 2 — frontend, routage planning)

`planningService.ts`/`stores/planning.ts` : `DeckBreakdown` généralisé en `BreakdownItem`
(`kind`/`id`/`name`), `advanceReview(kind, id, ...)` poste `deck_id`/`set_id` selon le cas.
`WeekCalendar.vue`/`MonthCalendar.vue`/`PlanningPage.vue` : `item.deck_id`/`item.deck_name` →
`item.id`/`item.name`. Décision (simplification assumée, documentée) : un clic « Réviser » sur
un ensemble de révision route directement vers `/revision/sets/:id/study?include_not_due=true`
(révision libre) sans passer par `prepareAdvanceReview`/`advance_review_set` — `RevisionStudy.vue`
n'a pas d'équivalent de « cartes dues ce jour précis », contrairement à `StudyDeck.vue` ; le
backend `advance_review_set` (Task 1) reste complet et testé mais n'est pour l'instant appelé
que par ce futur usage plus précis si besoin. `advanceReviewCards` du store reste `Flashcard[]`
(seul `StudyDeck.vue` le consomme, jamais alimenté pour un ensemble). Tests (TDD, rouge vérifié
avant implémentation) : service, store (dont non-régression deck), `WeekCalendar`/
`MonthCalendar` (rendu des deux `kind`), `PlanningPage` (routage deck vs revision_set via
`document.body` — `BaseModal`/headlessui teleporte, même idiome que
`RevisionSetModal.spec.ts`). Suite complète : 547/547 tests frontend verts, `npm run build`
propre. Prochaine action : Task 3 (fix ciblé, fuite `<!--- sectionbody`).

## 2026-09-03 (Task 3 — fix ciblé, fuite HTML dans l'extrait)

`noteExcerpt()` (`Binders.vue`) retire désormais les commentaires HTML (`<!--[\s\S]*?-->`)
avant le nettoyage Markdown existant. Test dédié avec un contenu `<!--- sectionbody -->`
suivi de texte réel, vérifie qu'aucune trace de `<!--`/`-->`/`sectionbody` ne fuit dans
l'extrait rendu. Suite complète : 548/548 tests frontend verts. Prochaine action : Task 4
(backend, Notation IA).

## 2026-09-03 (Task 4 — backend, Notation IA)

`AIService.grade_note(note_title, note_content)` (patron `analyze_feynman`, JSON structuré :
`score` 0-100, `verdict`, `points_forts`, `ameliorations`, `suggestions`). Nouveau blueprint
`app/api/v1/notation.py` (`POST /api/v1/notation/grade`, `GET /api/v1/notation/tasks/<id>`) --
même patron exact que `feynman.py` (Celery + repli synchrone via `dispatch_or_run`,
`check_note_access` pour autoriser aussi une note partagée en lecture). Écart volontaire par
rapport au PLAN.md initial : route top-level `/notation/grade` (body `note_id`) plutôt que
`/notes/<id>/grade` imbriquée — aligné sur le vrai patron des fonctionnalités sœurs
(feynman/blurting), découvert en lisant le code plutôt que deviné à l'ouverture du chantier.
Pas de `StudySession` créée (Notation n'est pas une session d'étude, contrairement à
Feynman/Blurting). Tests : service (`test_ai_service.py`, clé API manquante + succès mocké) +
route (`test_notation.py`, nouveau fichier — validation, 404, 403 isolation `user_id`, cycle
complet check→poll). Suite complète backend (hors `test_pdfs.py`/`test_import.py`, échecs
Windows préexistants sans rapport) : 100% verte. Prochaine action : Task 5 (frontend, brancher
le bouton Notation).

## 2026-09-03 (Task 5 — frontend, bouton Notation)

`notationService.ts` (patron `feynmanService.ts`) + `NoteGradeModal.vue` (nouveau, présentationnel
pur — reçoit `open`/`loading`/`error`/`result`, `NoteEdit.vue` gère l'appel/le polling, même
convention que `NoteEvaluationModal.vue`) : score en cercle `/10` à une décimale (backend
renvoie 0-100, converti à l'affichage), verdict, colonnes Points forts/Améliorations,
Suggestions. Bouton « Notation » (`NoteEdit.vue`) retiré de son état `disabled`, câblé sur
`openGradeModal()` (même flux Celery+polling que `evaluateFeynman()`). Détail piégeux trouvé en
testant : `BaseModal` (headlessui `TransitionRoot`/Dialog) rend son contenu téléporté vers
`document.body` de façon asynchrone — un `nextTick()` est nécessaire après `mount()` avant
d'interroger `document.body.textContent`, sans quoi le contenu est vide (pas d'erreur, juste un
faux négatif silencieux) ; noté pour la prochaine fois qu'un composant s'appuie sur `BaseModal`
en test. Tests : `notationService`, `NoteGradeModal` (4 états), `NoteEdit.vue` (bouton actif,
appel + résultat, état de chargement). Suite complète : 556/556 tests frontend verts, `npm run
build` propre. Prochaine action : Task 6 (Blurting).
