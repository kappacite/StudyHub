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

## 2026-09-03 (Task 6 — Blurting)

`Blurting.vue` : la jauge circulaire animée + bloc « Bilan de votre tuteur » séparés
remplacés par une carte « Analyse » unique (score `/10` à une décimale, badge circulaire
`accent-soft`, paragraphe de bilan) — même convention visuelle que Notation/Feynman,
structure du canevas `Blurting.dc.html`. Couleurs Tailwind brutes retirées
(`getStatusBadgeClass` : `emerald-50`/`amber-50`/`rose-50` → `success-soft`/`warning-soft`/
`danger-soft`). Conforme à l'arbitrage du `CONTEXT.md` : « Concepts clés » et « Flashcards
suggérées + import » **conservés** en section secondaire — aucun changement de schéma côté
`AIService.analyze_blurting` (le `retention_score` 0-100 existant est juste réaffiché divisé
par 10). Tests (TDD, rouge vérifié avant implémentation, nouveau fichier `Blurting.spec.ts` —
aucun test n'existait avant) : non-régression étape rédaction, format `/10` du score,
conservation concepts/flashcards, absence de couleurs brutes dans le HTML rendu. Suite
complète : 561/561 tests frontend verts, `npm run build` propre. Prochaine action : Task 7
(harmonisation mineure Feynman).

## 2026-09-03 (Task 7 — harmonisation Feynman)

`NoteFeynman.vue` : score affiché `/10` à une décimale (`formattedScore` computed, même
patron que Blurting/Notation) au lieu de `%`. Aucun changement structurel (déjà conforme).
2 tests existants mettaient à jour des assertions sur le format brut de l'ancien score
(`'82'`/`'60'`) — corrigés vers le nouveau format (`'8,2'`/`'6,0'`), légitime puisque le
format d'affichage change intentionnellement. Suite complète : 561/561 tests frontend
verts, `npm run build` propre. Prochaine action : Task 8 (refonte densité éditeur de notes).

## 2026-09-03 (Task 8 — densité de l'éditeur de notes)

Mode édition : Ligne 1 passe de 9 contrôles visibles à 4 (Titre, statut de sauvegarde,
Visualiser, Public) + un bouton « Réglages » regroupant Classeur/Tags/Contexte-Liens/
Aperçu/Guide dans un popover (même patron que le popup Partage déjà présent dans ce
fichier — pas de composant Menu générique introduit, YAGNI). Ligne 2 : Définition
(Info-bulle) + insertion de diagramme (usage occasionnel) regroupés dans un bouton
« Insérer », Format/LaTeX/Code restent visibles (usage très fréquent). Mode lecture laissé
inchangé après inspection réelle — seulement 5 contrôles, pas de clutter constaté
contrairement au mode édition (écart avec l'intention initiale du `CONTEXT.md`, corrigé
ici par jugement direct plutôt que suivi mécanique). Aucune fonctionnalité supprimée,
uniquement regroupée. Bug trouvé en cours de route (TDD) : mon premier remaniement du Row 1
laissait un second bouton « Guide » dupliqué hors du popover (`old_string` de l'édition ne
couvrait pas toute la zone) — détecté par le test de décluttering lui-même, corrigé.

Vérification visuelle réelle faite (app locale, serveur backend relancé au passage — il
tournait sur du code d'avant les Tasks 4-8, `/notation/grade` répondait 404) : popover
Réglages et popover Insérer tous deux fonctionnels et lisibles à 1440px, desktop clair
comme attendu (thème sombre actif par défaut). Limite honnête : la vérification à 375px
n'a pas pu être faite mécaniquement (l'outil de redimensionnement de fenêtre n'affecte pas
la fenêtre réellement capturée dans cet environnement, confirmé via `window.innerWidth`
resté à 1144 après la commande) — risque de régression jugé faible : le changement réduit
strictement le nombre d'éléments toujours visibles par rapport à l'existant, sur une rangée
qui a déjà son correctif `flex-wrap` d'un chantier précédent. Tests : 53/53 sur
`NoteEdit.spec.ts`, suite complète 563/563 tests frontend, `npm run build` propre.
Prochaine action : Task 9 (vérification finale, clôture).

## 2026-09-03 (Task 9 — vérification finale, clôture)

Suite complète backend (hors `test_pdfs.py`/`test_import.py`, échecs Windows préexistants
sans rapport, cf. journal `revision-qcm-heterogene`) : 100% verte, exit code 0. Suite
frontend complète : 563/563, `npm run build` propre. Backend redémarré pour charger le code
réel des Tasks 1-8 (le serveur tournait sur du code antérieur, `/notation/grade` répondait
404 avant redémarrage — bug de méthode, pas de code, mais qui aurait invalidé toute
vérification visuelle faite avant ce constat).

Vérification visuelle réelle (app locale, compte dev) :
- **Planning** (bug original, item 4) : confirmé résolu — la page affiche désormais les
  ensembles de révision dus par jour (« Spectroscopie & RMN », « Stéréochimie »,
  « Mécanismes SN1 / SN2 »), « Total à réviser : 7 cartes » au lieu d'un planning vide en
  permanence.
- **Aperçu bibliothèque** (item 5) : extraits de notes rendus proprement, aucune fuite de
  balisage constatée sur le jeu de notes réel.
- **Notation IA** (item 1) : bouton actif, ouvre la modale, appelle `/notation/grade`,
  affiche l'état de chargement puis l'état d'erreur correctement (timeout Axios 10s sur
  l'appel Gemini réel en repli synchrone sans worker Celery local — caractéristique
  d'infrastructure préexistante, identique pour Feynman/Blurting, hors périmètre de ce
  chantier).
- **Éditeur de notes** (item 6) : popovers Réglages et Insérer fonctionnels et lisibles à
  1440px ; vérification 375px non mécaniquement faite (limite outillage, documentée à la
  Task 8).

Les 6 demandes de l'utilisateur sont traitées (Notation IA, Blurting, Feynman, planning,
fuite HTML, éditeur), 9 tâches complètes. Chantier prêt à clôturer.

## 2026-09-03 (Task 10 — timeout Axios, demande utilisateur)

Timeout global `web/src/services/api.ts` porté de 10s à 60s — trop court pour un appel IA
(Notation/Feynman/Blurting) en repli synchrone sans worker Celery local (timeout constaté en
direct à la Task 9 sur `/notation/grade`). Test dédié (`api.spec.ts`, nouveau fichier).
Suite complète : 564/564 tests frontend verts.

## 2026-09-03 (Task 11 — timeout Axios 2 minutes, demande utilisateur)

60s encore trop court en pratique — porté à 120s (2 minutes). Même fichier, même test mis à
jour. Suite complète : 564/564 tests frontend verts.

## 2026-09-03 (clôture)

Toutes les tâches du plan sont cochées et vérifiées (tests + parcours réel). Chantier clos
(code). Prochaine action : demander à l'utilisateur de pousser
`feature/notes-ia-planning-corrections`, puis ouvrir la PR.
