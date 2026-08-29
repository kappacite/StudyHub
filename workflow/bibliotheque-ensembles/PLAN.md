# Plan — bibliotheque-ensembles

- [x] Attendre que `backend-ensembles-heterogenes` soit livré — mergé (PR #126, `d2b6305`),
  CI verte (dont la garde migrations PostgreSQL)
- [x] Écrire la spec + plan détaillé (inventaire `Binders.vue`, maquette `Notes.dc.html`, états,
  contrat des 3 nouveaux composants) via `superpowers:brainstorming` puis
  `superpowers:writing-plans` —
  `docs/superpowers/specs/2026-08-28-bibliotheque-ensembles-design.md` +
  `docs/superpowers/plans/2026-08-28-bibliotheque-ensembles.md` (11 tâches TDD après 2 ajouts
  en cours d'exécution, cf. journal)
- [x] Migrer `Binders.vue` : bascule Notes/Révision/Autres + liste d'ensembles hétérogènes
  fusionnée visuellement avec les decks classiques (Task 9, 2 constats critiques trouvés en
  revue et corrigés — cf. journal)
- [x] Construire `RevisionSetDetail.vue` (Task 5)
- [x] Construire `RevisionSetModal.vue` (Task 4)
- [x] Construire `RevisionSetTypeItems.vue` (Task 6, pas prévu initialement dans cette liste —
  nécessaire pour éditer les items d'un seul type au sein d'un ensemble hétérogène)
- [x] Construire/adapter `RevisionItemModal.vue` (6 types, dont le type `flashcard` manquant
  trouvé et corrigé en Task 7)
- [x] Adapter `RevisionStudy.vue` au dispatch par type d'item (Task 8, dépendance dure non
  prévue initialement — nécessaire pour que « Réviser l'ensemble » fonctionne réellement)
- [x] Correctif backend `RevisionSetCreate.type` optionnel (Task 1, petit gap trouvé en écrivant
  le plan — sans lui la création d'un ensemble hétérogène était rejetée par l'API)
- [x] Correctif `TeacherDashboard.vue` (Task 10, risque de plantage réel trouvé en revue de la
  Task 2 — écran non lié à ce chantier mais cassé par la nullabilité de `RevisionSet.type`)
- [x] Vérification visuelle clair/sombre × desktop/mobile — **faite** (environnement natif
  hors Docker : venv local + SQLite pour le backend, Vite dev pour le frontend ; navigateur
  réel pour desktop/clair/sombre, Playwright 375×812 pour mobile). A trouvé et corrigé un bug
  bloquant réel (`module=rset.type` → `NOT NULL` sur `study_sessions` pour tout ensemble
  vraiment hétérogène) plus un défaut mineur (titres mobiles manquants) — détail complet dans
  le journal. `ETAT.md` §« Plan global par flux » précise explicitement ne plus être mis à jour
  au fil de l'exécution (suivi déplacé vers `workflow/`) — rien à y changer.
