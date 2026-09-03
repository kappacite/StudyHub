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
- [ ] Task 5 — Frontend : brancher le bouton « Notation » (`NoteEdit.vue:618-627`, actuellement
  `disabled`) sur la route de la Task 4. Résultat affiché en modale (cohérent avec le flux
  d'édition existant, ne casse pas la mise en page) conforme au canevas `Note — Notation (IA)` :
  score en cercle `/10` à une décimale (diviser le score 0-100 par 10, formatage décimal
  français), verdict, deux colonnes Points forts (vert) / Améliorations (orange), Suggestions.
  Tests composant (état loading/résultat/erreur).
- [ ] Task 6 — Frontend + backend (si besoin) : refonte de `Blurting.vue` pour suivre la
  structure du canevas sans supprimer de fonctionnalité (cf. arbitrage `CONTEXT.md`) — carte
  d'analyse primaire unifiée (score `/10` à une décimale au lieu du % actuel, remplace la jauge
  circulaire + bloc « Bilan de votre tuteur » séparés), toutes les couleurs brutes remplacées
  par des tokens sémantiques (`text-emerald-500` → `text-success`, etc.), « Concepts clés » et
  « Flashcards suggérées + import » conservés en section secondaire sous la carte d'analyse.
  Aucun changement de schéma `AIService.analyze_blurting` attendu (juste un réaffichage divisé
  par 10) — vérifier en écrivant le test. Tests composant sur le nouvel affichage du score et la
  présence des sections conservées.
- [ ] Task 7 — Frontend : harmonisation mineure `NoteFeynman.vue` — score affiché `/10` à une
  décimale au lieu de `%` (même formatage que Notation/Blurting), pas de changement structurel.
  Test composant sur le nouveau format d'affichage.
- [ ] Task 8 — Frontend : refonte de la densité de `NoteEdit.vue` (cf. arbitrage `CONTEXT.md`,
  pas de canevas cible strict pour ce point). Mode édition ligne 1 : regrouper
  Classeur/Tags/Contexte-Liens/Aperçu/Guide dans un menu « Réglages » (popover), garder
  Titre/Sauvegarde/Partage/Visualiser visibles. Ligne 2 : garder Format/LaTeX/Code visibles,
  regrouper Définition + Insertion diagramme dans un menu « Insérer ». Mode lecture : Guide
  rejoint le même menu « Réglages », garder Retour/bascule Lecture-Révision/Modifier/Export PDF
  visibles. Aucune fonctionnalité supprimée. Tests composant sur la présence de toutes les
  actions (déplacées, pas perdues) + vérification visuelle réelle (375px/1440px, clair/sombre)
  dans l'app locale avant de clore la tâche.
- [ ] Task 9 — Vérification finale : suite complète (backend + frontend) verte, `npm run build`
  propre, non-régression rapide sur les écrans touchés (Planning avec des decks existants,
  aperçu bibliothèque avec des notes sans commentaire HTML, Feynman/Blurting sur un vrai appel
  IA si clé Gemini disponible sinon revue de code seule), puis clôture du chantier.
