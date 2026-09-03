# Plan — notes-ia-planning-corrections

Une case = une tâche atomique. TDD (skill `cycle-tdd`) : le test précède le code.
Détail de l'approche retenue et des arbitrages : `CONTEXT.md`.

- [x] Task 1 — Backend : planning de révision toujours vide. `PlanningService.get_calendar()`
  agrège aussi les `RevisionItem` dus (via `RevisionItemDAO`, groupés par `RevisionSet`, même
  principe que le groupement par `deck_id` existant) en plus des `Flashcard`/`Deck` — un jour du
  `breakdown` peut désormais mélanger deck et ensemble. `advance_review()` étendu pour accepter
  un `RevisionSet` en plus d'un `Deck`. Tests : jour avec seulement des `RevisionItem` dus
  (actuellement retournerait 0, doit retourner le bon total), jour mixte deck+ensemble, retard
  (item avant `date_from`) rattaché au premier jour comme les flashcards, non-régression sur les
  cas 100% deck existants.
- [x] Task 2 — Frontend : `PlanningPage.vue`/`WeekCalendar.vue`/`MonthCalendar.vue` distinguent
  le type d'item dans la modale de révision anticipée (`selectedDayForModal.breakdown`) et
  routent correctement au clic « Réviser » (`/decks/:id/study?advance=true` pour un deck,
  `/revision/sets/:id/study` pour un ensemble — vérifier si un paramètre d'anticipation existe
  déjà côté route ensemble, sinon révision normale suffit, le SM-2 s'appliquera avec la date du
  jour comme pour les decks). Tests composant sur le routage selon le type.
- [x] Task 3 — Fix ciblé : `<!--- sectionbody` (ou tout commentaire HTML) qui fuit dans l'aperçu
  bibliothèque. `noteExcerpt()` (`Binders.vue`) retire aussi les commentaires HTML
  (`<!--[\s\S]*?-->`) avant le nettoyage Markdown existant. Test : contenu avec un commentaire
  HTML au milieu, extrait ne doit contenir aucune trace de `<!--`/`-->`, non-régression sur les
  extraits déjà couverts (caractères Markdown, retours à la ligne).
- [x] Task 4 — Backend : Notation IA. Nouvelle méthode `AIService.grade_note(note_title,
  note_content) -> dict` (JSON structuré via `_generate_json_object`, même patron que
  `analyze_feynman`) : `score` (0-100), `verdict` (phrase courte), `points_forts` (liste),
  `ameliorations` (liste), `suggestions` (paragraphe). Nouveau service dédié + route
  (`POST /api/v1/notes/<id>/grade`, flux Celery + repli synchrone comme
  `evaluation_service.py`/feynman). Tests service (mock Gemini) + route (mock + isolation
  `user_id`).
- [x] Task 5 — Frontend : brancher le bouton « Notation » (`NoteEdit.vue:618-627`, actuellement
  `disabled`) sur la route de la Task 4. Résultat affiché en modale (cohérent avec le flux
  d'édition existant, ne casse pas la mise en page) conforme au canevas `Note — Notation (IA)` :
  score en cercle `/10` à une décimale (diviser le score 0-100 par 10, formatage décimal
  français), verdict, deux colonnes Points forts (vert) / Améliorations (orange), Suggestions.
  Tests composant (état loading/résultat/erreur).
- [x] Task 6 — Frontend + backend (si besoin) : refonte de `Blurting.vue` pour suivre la
  structure du canevas sans supprimer de fonctionnalité (cf. arbitrage `CONTEXT.md`) — carte
  d'analyse primaire unifiée (score `/10` à une décimale au lieu du % actuel, remplace la jauge
  circulaire + bloc « Bilan de votre tuteur » séparés), toutes les couleurs brutes remplacées
  par des tokens sémantiques (`text-emerald-500` → `text-success`, etc.), « Concepts clés » et
  « Flashcards suggérées + import » conservés en section secondaire sous la carte d'analyse.
  Aucun changement de schéma `AIService.analyze_blurting` attendu (juste un réaffichage divisé
  par 10) — vérifier en écrivant le test. Tests composant sur le nouvel affichage du score et la
  présence des sections conservées.
- [x] Task 7 — Frontend : harmonisation mineure `NoteFeynman.vue` — score affiché `/10` à une
  décimale au lieu de `%` (même formatage que Notation/Blurting), pas de changement structurel.
  Test composant sur le nouveau format d'affichage.
- [x] Task 8 — Frontend : refonte de la densité de `NoteEdit.vue` (cf. arbitrage `CONTEXT.md`,
  pas de canevas cible strict pour ce point). Mode édition ligne 1 : regrouper
  Classeur/Tags/Contexte-Liens/Aperçu/Guide dans un menu « Réglages » (popover), garder
  Titre/Sauvegarde/Partage/Visualiser visibles. Ligne 2 : garder Format/LaTeX/Code visibles,
  regrouper Définition + Insertion diagramme dans un menu « Insérer ». Mode lecture : Guide
  rejoint le même menu « Réglages », garder Retour/bascule Lecture-Révision/Modifier/Export PDF
  visibles. Aucune fonctionnalité supprimée. Tests composant sur la présence de toutes les
  actions (déplacées, pas perdues) + vérification visuelle réelle (375px/1440px, clair/sombre)
  dans l'app locale avant de clore la tâche.
- [x] Task 10 — Frontend : le timeout Axios global (10s, `web/src/services/api.ts`) est trop
  court pour un appel IA synchrone sans worker Celery local (repli inline observé en Task 9,
  timeout constaté sur `/notation/grade`) — porté à 60s (1 minute), demande explicite de
  l'utilisateur.
- [x] Task 11 — Frontend : 60s encore insuffisant en pratique (demande explicite de
  l'utilisateur) — timeout Axios porté à 120s (2 minutes).
- [x] Task 12 — Persistance de la Notation IA (demande explicite de l'utilisateur) : la
  notation n'était jusque-là jamais enregistrée (résultat éphémère, reperdu à chaque clic).
  Backend : nouveau modèle `NoteGrade` (une par note, écrasée à la réévaluation — pas
  d'historique, même patron que `Evaluation`), migration Alembic, `NoteGradeDAO`
  (`get_by_note`/`upsert`), `run_note_grading` persiste désormais le résultat, nouvelle route
  `GET /api/v1/notation/<note_id>` (404 si pas encore noté). Frontend : au clic sur
  « Notation », si aucune notation existante → lance l'évaluation comme avant ; si une
  notation existe déjà → propose un choix (« Voir la notation existante » / « Réévaluer »)
  dans `NoteGradeModal.vue` avant de rappeler l'IA.
- [x] Task 13 — Refonte de l'écran Notation (demande explicite de l'utilisateur) : le canevas
  `Note — Notation (IA)` montre un **écran dédié** (comme `NoteFeynman.vue`/`Blurting.vue`),
  pas une modale — écart trouvé en re-consultant le canevas. Conversion de `NoteGradeModal.vue`
  en route `/notes/:id/notation` (nouveau `NoteNotation.vue`), même patron de header que
  Feynman (breadcrumb, retour, titre), conserve le mode `choice` (voir/réévaluer) et la
  persistance (Task 12) sans changement côté backend.
- [x] Task 14 — Upload de PDF dans la Bibliothèque (demande explicite de l'utilisateur) : le
  backend accepte déjà `binder_id` à l'upload (`POST /api/v1/pdfs`, inchangé) mais aucune UI
  ne permet d'uploader un PDF depuis `Binders.vue` (seul « Élément existant » attache un PDF
  déjà présent). Ajout d'une entrée « PDF » dans le menu « Ajouter », `pdfStore.uploadPdf`
  étendu d'un `binderId` optionnel.
- [x] Task 15 — Backend : `FocusService.get_forecast()` (Charge à venir 14j, écran Accueil)
  n'interroge que `Flashcard`/`Deck`, jamais `RevisionItem`/`RevisionSet` — même classe de bug
  que le planning (Task 1), demande explicite de l'utilisateur après avoir constaté que la
  charge à venir affiche 0 alors qu'il étudie via des ensembles de révision. Étendre
  `get_forecast()` pour additionner aussi les `RevisionItem` dus par jour dans `forecast_dict`
  (même fenêtre de `days` jours, pas de filtrage de type nécessaire contrairement aux
  `Flashcard` — un `RevisionItem` est déjà un type de révision valide par construction).
  `get_today_items()` (compteurs "Aujourd'hui") et le planning sont déjà corrects (vérifiés en
  lisant le code) — seul `get_forecast()` a cette lacune. Test : ensemble de révision avec un
  item dû aujourd'hui compte dans le bucket du jour du forecast.
- [x] Task 9 — Vérification finale : suite complète (backend + frontend) verte, `npm run build`
  propre, non-régression rapide sur les écrans touchés (Planning avec des decks existants,
  aperçu bibliothèque avec des notes sans commentaire HTML, Feynman/Blurting sur un vrai appel
  IA si clé Gemini disponible sinon revue de code seule), puis clôture du chantier.
