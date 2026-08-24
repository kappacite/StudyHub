# Cartographie initiale du dépôt — StudyHub

> Phase 0 (reconnaissance, lecture seule). Inventaires bruts et chiffrés, sans jugement de
> valeur ni recommandation — la gravité et les pistes de correction relèvent de la phase 2.
> Généré le 2026-08-23.

---

## 1. Documentation existante

| Fichier | Dernière modif | Ce qu'il prescrit |
|---|---|---|
| `AGENTS.md` (35 Ko, 1106 lignes) | non horodaté par git log ciblé (présent dès l'historique lu) | Architecture de référence : stack, structure de dépôt (`mobile/` en dossier racine, Capacitor 6, pas de `desktop/`), couches DAO/Service/API/Middleware, modèle de données Auth/Binder/Note, spec API (endpoints Auth/Users/Binders/Decks/Flashcards/Notes/Packages/Blurting/Diagrams/PDFs/Stats/Health), conventions de nommage, `docker-compose.yml`+`docker-compose.prod.yml` (sans Redis ni Celery), checklist PR. |
| `README.md` | non horodaté par git log ciblé | Présentation produit, stack (mentionne Tiptap 2, Mermaid.js, PDF.js, KaTeX, Capacitor 6), instructions d'installation Docker et manuelle, structure de dépôt avec `mobile/` en dossier racine. |
| `CLAUDE.md` (racine, 5 Ko) | présent, contenu déjà fourni en contexte système | Renvoie vers les skills `.claude/skills/*` et `docs/*.md` par couche, résumé de stack (Capacitor **8**, Electron pour `desktop/`), architecture en couches, isolation `user_id`, conventions, codes HTTP, interdictions strictes, checklist PR. Se veut court (~150 lignes) et non duplicatif. |
| `docs/api_reference.md` (1376 lignes) | 2026-07-12 | Référence détaillée des endpoints v1, jusqu'à la section 12 « Révision Méthode Feynman (IA) » — couvre donc des blueprints absents d'AGENTS.md (`feynman`, etc.). |
| `docs/backend.md` (247 lignes) | 2026-06-13 | Détail architecture en couches backend, modèle de données, choix d'implémentation. |
| `docs/frontend.md` (146 lignes) | 2026-06-10 | SPA Vue 3 `<script setup lang="ts">`, TypeScript strict (pas de `any`), Tailwind + design system, Pinia, Vue Router avec guards. |
| `docs/design-system.md` (112 lignes) | 2026-06-21 | Système de design nommé **« White/Pink × Material épuré »** : primaire Pink 400 `#F06292`, tokens en custom properties CSS dans `web/src/style.css` exposés via `tailwind.config.js`, light + dark, motion ~200 ms ease-out, déploiement incrémental (tokens/primitives puis migration des vues par lots). |
| `docs/desktop.md` (89 lignes) | 2026-06-24 | Coque bureau Electron réutilisant le build `web/`, schéma « Bureau/Mobile wrap Web ↔ API ↔ PostgreSQL », renvoie au skill `desktop-build`. |
| `docs/mobile.md` (69 lignes) | 2026-06-24 | Coque mobile Capacitor réutilisant le build `web/` (projet natif dans `web/android`, pas de dossier `mobile/` racine), `usePlatform()` pour le conditionnel natif, renvoie au skill `mobile-build`. |
| `docs/migrations.md` (56 lignes) | 2026-06-12 | Le head Alembic fait foi ; auto-application des migrations versionnées au démarrage (`backend/wsgi.py`) ; interdiction explicite de générer une migration à la volée en production. |
| `docs/testing.md` (99 lignes) | 2026-06-13 | Stratégie de tests et gate anti-régression : `main` protégée, aucun push direct, flux `feature/* → develop → main` avec CI requise verte. |
| `docs/performance-audit.md` (169 lignes) | 2026-06-13 | Audit de performance déjà mené : statut **« plan implémenté (PR #10→#18) »**. 8 thématiques (instrumentation, index DB, over-fetch decks, N+1, cache Redis partiel, concurrence gthread, frontend partiel, full-text/LIKE), constats détaillés fichier:ligne (ex. `models/deck.py:32`, `dao/deck_dao.py:57-62`). Un reliquat signalé : CTE récursive de `class_service`, pagination frontend complète, caching des listes. |
| `docs/ui-redesign-plan.md` (208 lignes) | 2026-06-21 | Plan de suivi exécutable « S0 → S7 » de la refonte UI structurelle vers la direction « White/Pink × Material épuré ». Tableau d'avancement : Lot 0, Lot 1, Lot T, S0.1-S0.5, S0, S1, S5, S6 marqués **✅ fait** ; S2, S3, S4, S7 marqués **🔄 en cours**. Note explicite : le corps de l'éditeur `Diagrams.vue` (canevas SVG) est « laissé tel quel », à reprendre en S7. |
| `docs/revision-active-notes.md` (60 lignes) | 2026-06-15 | Guide utilisateur du balisage « Révision Active » dans les notes (auto-test inline, sans persistance). |
| `docs/REFACTO_FONCTIONNALITES.md` (375 lignes) | 2026-06-15 | Plan de suivi étape par étape « Révision / Professeur / UI », légende ✅/🟡/⬜/♻️, rappel des conventions AGENTS.md. |
| `docs/FEATURES.md` (1223 lignes) | 2026-06-15 | Roadmap fonctionnelle destinée à être lue/mise à jour par un agent IA, instructions : lire AGENTS.md, respecter les couches, TDD (« écrire les tests avant ou pendant le code, jamais après »), un commit par étape, journal en bas de fichier. |
| `docs/development_journal.md` (1520 lignes) | 2026-07-12 | Journal daté des développements (dernière entrée : 2026-07-12, génération IA de flashcards par taux de couverture des notions). |
| `.claude/skills/*/SKILL.md` (6 fichiers : `api-spec`, `backend-patterns`, `deployment`, `desktop-build`, `frontend-patterns`, `mobile-build`) | — | Chacun chargé à la demande selon la couche travaillée (référencés depuis `CLAUDE.md`). |
| `backend/CLAUDE.md`, `web/CLAUDE.md`, `web/src/components/CLAUDE.md` | absents | N'existent pas dans le dépôt actuel. |
| `.github/workflows/ci.yml` | présent | Gate anti-régression sur PR/push vers `main`/`develop` : 6 jobs (voir §4). |

**États manifestement antérieurs au code actuel, repérés dans `AGENTS.md` et `README.md`** (les deux seuls documents concernés — tous les autres fichiers `docs/*.md` sont cohérents avec le code observé) :

- Structure de dépôt : les deux décrivent un dossier `mobile/` à la racine (`mobile/android`, `mobile/ios`) ; le dépôt réel a `web/android` (Capacitor packagé depuis `web/`) et aucun dossier `mobile/` racine.
- Aucune mention de `desktop/` (Electron) dans AGENTS.md ni README.md, alors que le dossier existe et qu'un skill `desktop-build` + `docs/desktop.md` le documentent.
- Version Capacitor : « 6 » dans AGENTS.md/README.md vs `^8.4.1` dans `web/package.json`.
- Stack éditeur de notes : AGENTS.md/README.md mentionnent Tiptap 2 ; aucune dépendance Tiptap dans `web/package.json` (dépendances présentes : `marked`, `dompurify`, `highlight.js`, `katex`).
- PDF.js cité comme lecteur PDF ; aucune dépendance `pdfjs-dist` (ni équivalent) dans `web/package.json` ; `PdfReader.vue` n'importe que le store `pdf` et des icônes `lucide`.
- Mermaid.js cité comme moteur de diagrammes ; aucune dépendance `mermaid` dans `web/package.json` ; le mot « mermaid » n'apparaît que dans `Diagrams.vue`, `NoteEdit.vue`, `models/diagram.py` et `app/__init__.py` (nature de ces références — commentaire, CSP, identifiant de bloc de code — non déterminée à ce stade).
- Docker : AGENTS.md décrit deux fichiers (`docker-compose.yml` dev + `docker-compose.prod.yml`) sans Redis ni worker Celery. Le dépôt n'a qu'un seul `docker-compose.yml`, déjà « façon prod » (`restart: always`, pas de bind-mount de code), avec 5 services : `db`, `redis`, `backend`, `worker` (Celery), `frontend`. Variables `GEMINI_API_KEY`/`GEMINI_MODEL` injectées côté conteneur `backend`/`worker` uniquement.
- Aucun `.env.example` trouvé à la racine ni dans `backend/`/`web/`, alors qu'AGENTS.md et la checklist PR (AGENTS.md §13, CLAUDE.md) y font référence.
- Portée fonctionnelle : AGENTS.md décrit 7 modèles/DAO/services (`user`, `deck`, `flashcard`, `note`, `diagram`, `pdf_document`, `binder`) et ~10 blueprints. Le code réel compte 21 modèles, 17 DAO, 29 services et 27 blueprints (détail §2) — domaines absents d'AGENTS.md : classes/enseignant (`class_*`), groupes, examens, quiz, évaluations IA, méthode Feynman, focus/pomodoro, planning, notifications, tags, recherche, imports (Anki), analytics/engagement.
- Design/UI : AGENTS.md §6 documente des tokens Tailwind théoriques (`primary #4F46E5`, police `Inter Variable`) différents de la direction réellement en place et documentée dans `docs/design-system.md` (« White/Pink × Material », primaire `#F06292`).

---

## 2. Backend

### 2.1 Modèles (`backend/app/models/`, 21 fichiers)
`assignment`, `binder`, `class_insight`, `class_question`, `deck`, `diagram`, `evaluation`, `exam`, `flashcard`, `group`, `hidden_binder`, `hidden_note`, `note`, `notification`, `pdf_document`, `quiz`, `revision`, `search_type`, `study_session`, `tag`, `user`.

### 2.2 DAO (`backend/app/dao/`, 17 fichiers dont `base_dao.py`)
`assignment_dao`, `base_dao`, `binder_dao`, `deck_dao`, `diagram_dao`, `evaluation_dao`, `exam_dao`, `flashcard_dao`, `group_dao`, `note_dao`, `pdf_dao`, `quiz_dao`, `revision_dao`, `search_dao`, `study_session_dao`, `tag_dao`, `user_dao`.

### 2.3 Services (`backend/app/services/`, 29 fichiers)
`ai_service`, `analytics_service`, `auth_service`, `binder_items_service`, `binder_service`, `class_management_service`, `class_qa_service`, `class_service`, `community_service`, `deck_service`, `diagram_service`, `engagement_service`, `evaluation_service`, `exam_service`, `flashcard_generation_service`, `flashcard_service`, `focus_service`, `group_service`, `import_service`, `note_service`, `pdf_service`, `planning_service`, `quiz_service`, `revision_service`, `revision_stats_service`, `search_service`, `spaced_repetition`, `stats_service`, `tag_service`, `user_service`.

### 2.4 Schémas Pydantic (`backend/app/schemas/`, 21 fichiers)
`analytics_schema`, `auth_schema`, `binder_schema`, `class_schema`, `deck_schema`, `diagram_schema`, `engagement_schema`, `evaluation_schema`, `exam_schema`, `flashcard_schema`, `focus_schema`, `group_schema`, `management_schema`, `note_schema`, `pdf_schema`, `planning_schema`, `quiz_schema`, `revision_schema`, `stats_schema`, `tag_schema`, `user_schema`.

### 2.5 Routes par blueprint (`backend/app/api/v1/`, 26 fichiers, 27 blueprints enregistrés)

Préfixes tels que déclarés dans `backend/app/__init__.py` :

| Blueprint | Préfixe | Nb routes | Endpoints (méthode + chemin relatif) |
|---|---|---|---|
| `auth_bp` | `/api/v1/auth` | 5 | POST `/register`, POST `/login`, POST `/refresh`, POST `/logout`, DELETE `/account` |
| `users_bp` | `/api/v1/users` | 3 | GET `/me`, PUT `/me`, DELETE `/me` |
| `binders_bp` | `/api/v1/binders` | 11 | GET ``, POST ``, GET `/<binder_id>`, PUT `/<binder_id>`, DELETE `/<binder_id>`, POST `/<binder_id>/items`, POST `/<binder_id>/items/detach`, GET `/<binder_id>/study`, POST `/<binder_id>/tags`, DELETE `/<binder_id>/tags/<tag_id>`, GET `/public/<binder_id>`, PATCH `/<binder_id>/visibility` |
| `decks_bp` | `/api/v1/decks` | 9 | GET ``, POST ``, GET `/<deck_id>`, PUT `/<deck_id>`, DELETE `/<deck_id>`, POST `/<deck_id>/tags`, DELETE `/<deck_id>/tags/<tag_id>`, GET `/<deck_id>/study`, POST `/<deck_id>/study/answer/<card_id>` |
| `flashcards_bp` | `/api/v1/decks/<deck_id>/cards` | 6 | GET ``, POST ``, GET `/<card_id>`, PUT `/<card_id>`, DELETE `/<card_id>`, GET `/<card_id>/history` |
| `flashcards_global_bp` | `/api/v1/flashcards` | 2 | POST `/generate`, PATCH `/<card_id>/review` |
| `revision_bp` | `/api/v1/revision` | 12 | GET `/sets`, POST `/sets`, GET `/sets/<id>`, PUT `/sets/<id>`, DELETE `/sets/<id>`, GET `/sets/<id>/items`, POST `/sets/<id>/items`, PUT `/sets/<id>/items/<item_id>`, DELETE `/sets/<id>/items/<item_id>`, GET `/sets/<id>/study`, POST `/sets/<id>/study/answer/<item_id>`, POST `/sets/<id>/run`, POST `/sets/<id>/study/grade/<item_id>` (13 routes listées) |
| `notes_bp` | `/api/v1/notes` | 11 | GET ``, POST ``, GET `/<note_id>`, PUT `/<note_id>`, DELETE `/<note_id>`, POST `/<note_id>/copy`, POST `/<note_id>/hide`, DELETE `/<note_id>/hide`, POST `/<note_id>/tags`, DELETE `/<note_id>/tags/<tag_id>`, GET `/public/<token>`, PATCH `/<note_id>/visibility` (12 routes listées) |
| `diagrams_bp` | `/api/v1/diagrams` | 7 | GET ``, POST ``, GET `/<id>`, PUT `/<id>`, DELETE `/<id>`, POST `/<id>/tags`, DELETE `/<id>/tags/<tag_id>` |
| `pdfs_bp` | `/api/v1/pdfs` | 8 | GET ``, POST ``, GET `/<pdf_id>`, GET `/<pdf_id>/file`, PUT `/<pdf_id>`, DELETE `/<pdf_id>`, POST `/<pdf_id>/tags`, DELETE `/<pdf_id>/tags/<tag_id>` |
| `stats_bp` | `/api/v1/stats` | 9 | GET `/overview`, GET `/sessions`, POST `/sessions`, GET `/heatmap`, GET `/decks/<deck_id>`, GET `/dashboard`, GET `/sets/<set_id>`, GET `/items/<item_id>`, GET `/binders/<binder_id>` |
| `health_bp` | `/api/v1/health` | 1 | GET `` |
| `blurting_bp` | `/api/v1/blurting` | 3 | POST `/analyze`, GET `/tasks/<task_id>`, POST `/create-flashcards` |
| `feynman_bp` | `/api/v1/feynman` | 2 | POST `/analyze`, GET `/tasks/<task_id>` |
| `packages_bp` | `/api/v1/packages` | 3 | GET ``, GET `/<binder_id>`, POST `/<binder_id>/clone` |
| `tags_bp` | `/api/v1/tags` | 4 | GET ``, POST ``, PUT `/<tag_id>`, DELETE `/<tag_id>` |
| `focus_bp` | `/api/v1/focus` | 3 | GET `/today`, GET `/forecast`, GET `/retention` |
| `planning_bp` | `/api/v1/planning` | 2 | GET `/calendar`, POST `/advance` |
| `search_bp` | `/api/v1/search` | 1 | GET `` |
| `imports_bp` | `/api/v1/import` | 1 | POST `/anki` |
| `quizzes_bp` | `/api/v1/quizzes` | 6 | POST `/generate`, GET `/note/<note_id>`, GET `/<quiz_id>`, POST `/<quiz_id>/questions/<question_id>/answer`, POST `/<quiz_id>/complete`, POST `/<quiz_id>/create-flashcards` |
| `evaluations_bp` | `/api/v1/evaluations` | 6 | POST `/generate`, GET `/tasks/<task_id>`, GET `/<evaluation_id>`, POST `/<evaluation_id>/items/<item_id>/answer`, POST `/<evaluation_id>/complete`, POST `/<evaluation_id>/flashcards` |
| `exam_bp` | `/api/v1/exam` | 4 | POST `/start`, GET `/<session_id>`, POST `/<session_id>/questions/<item_id>/answer`, POST `/<session_id>/complete` |
| `groups_bp` | `/api/v1/groups` | 10 | POST ``, GET ``, GET `/<group_id>`, POST `/join`, DELETE `/<group_id>/members/<user_id>`, PATCH `/<group_id>/members/<user_id>`, POST `/<group_id>/binders`, GET `/binders/<binder_id>/classes`, DELETE `/<group_id>/binders/<binder_id>`, GET `/<group_id>/activity`, GET `/<group_id>/members/progress` (11 routes listées) |
| `classes_bp` | `/api/v1/classes` | 24 | GET ``, POST ``, GET `/<class_id>/assignments`, POST `/<class_id>/assignments`, GET `/<class_id>/assignments/<asgn_id>`, DELETE `/<class_id>/assignments/<asgn_id>`, PATCH/PUT (2 routes multi-lignes), GET `/<class_id>/analytics`, GET `/<class_id>/insights`, POST `/<class_id>/insights`, POST `/<class_id>/announcements`, GET `/<class_id>/feed`, GET `/<class_id>/leaderboard`, GET `/<class_id>/questions`, POST `/<class_id>/questions`, POST `/<class_id>/questions/<question_id>/answer`, GET `/<class_id>/members`, POST `/<class_id>/invite/regenerate`, POST `/<class_id>/distribute`, POST `/<class_id>/course-binder`, GET `/<class_id>/students/<student_id>/progress`, GET `/<class_id>/materials/progress`, GET `/public`, POST `/<class_id>/follow` |
| `assignments_mine_bp` | `/api/v1/assignments` | 1 | GET `/mine` |
| `notifications_bp` | `/api/v1/notifications` | 4 | GET ``, GET `/unread-count`, PATCH `/<notif_id>/read`, POST `/read-all` |

Non répertorié dans le router ou les blueprints ci-dessus : aucun écart détecté entre blueprints déclarés et blueprints enregistrés dans `backend/app/__init__.py`.

### 2.6 Endroits où le patron DAO semble court-circuité

- `db.session` référencé en dehors de `backend/app/dao/` dans **23 fichiers de routes** (`backend/app/api/v1/*.py` — pratiquement tous sauf `focus.py`, `search.py`, `stats.py`, `tags.py` sans certitude exhaustive) et **6 fichiers de services** (`class_service.py`, `community_service.py`, `focus_service.py`, `import_service.py`, `stats_service.py`, `backend/app/tasks.py`).
- Requêtes ORM directes (`.query(`) détectées dans **13 fichiers de services** : `analytics_service.py`, `class_management_service.py`, `class_qa_service.py`, `class_service.py`, `community_service.py`, `engagement_service.py`, `evaluation_service.py`, `exam_service.py`, `focus_service.py`, `group_service.py`, `note_service.py`, `planning_service.py`, `stats_service.py`.

### 2.7 Dépendances backend (`backend/requirements.txt` + `requirements-dev.txt`)
Flask 3.0.3, Flask-SQLAlchemy 3.1.1, SQLAlchemy ≥2.0.35, Flask-Migrate 4.0.7, Flask-JWT-Extended 4.6.0, Pydantic ≥2.7.2, Werkzeug 3.0.3, PyJWT 2.8.0, psycopg2-binary, gunicorn 22.0.0, Flask-Limiter 3.7.0, cryptography 42.0.7, flask-cors, python-magic, redis, gevent, flask-talisman, bleach, tinycss2, celery. Dev : pytest-cov, factory-boy, Faker, freezegun (commentaire : « utilisés à partir de la phase 4 »).

---

## 3. Frontend

### 3.1 Routes déclarées (`web/src/router/index.ts`)

35 entrées `path:` dénombrées, dont 7 redirects explicites (`dashboard`, `focus`, `binders/:id?`, `reviews`, `classes/teacher`, `classes/student`, `groups`) vers les 5 sections canoniques mentionnées dans `docs/ui-redesign-plan.md`. Routes réelles (hors redirects et catch-all) :

`/login`, `/register`, `/` (public : `explore`, `package/:id`, `notes/public/:token`), puis sous le layout applicatif : `accueil`, `bibliotheque/:id?`, `bibliotheque/:id/reviser`, `reviser`, `classes`, `decks`, `decks/:id/study`, `revision/sets/:id/run`, `revision/sets/:id/study`, `revision/sets/:id/manage`, `revision/sets/:id/stats`, `revision/binders/:id/stats`, `planning`, `notes`, `notes/:id`, `notes/:id/blurting`, `notes/:id/quiz`, `notes/:id/evaluation`, `exam/setup`, `exam/:id`, `exam/:id/results`, `diagrams`, `pdfs`, `groups/:id`, `classes/:classId/assignments/:asgnId`, plus `/:pathMatch(.*)*` (404).

Chaque route recensée dispose d'une vue correspondante dans `web/src/views/` (voir §3.2) ; aucune route sans vue identifiée.

### 3.2 Vues (`web/src/views/`, 35 fichiers `.vue`) — lignes de code

| Vue | Lignes |
|---|---|
| `Notes/NoteEdit.vue` | 3024 |
| `Reviews/Reviews.vue` | 1878 |
| `Diagrams/Diagrams.vue` | 1789 |
| `Classes/TeacherDashboard.vue` | 1064 |
| `Binders/Binders.vue` | 780 |
| `Notes/Blurting.vue` | 631 |
| `Notes/NoteQuiz.vue` | 566 |
| `Dashboard/Dashboard.vue` | 533 |
| `Decks/Decks.vue` | 518 |
| `Groups/GroupDetail.vue` | 498 |
| `Notes/NoteEvaluation.vue` | 467 |
| `Home/Accueil.vue` | 451 |
| `Exam/ExamSession.vue` | 437 |
| `Classes/StudentClassView.vue` | 387 |
| `Notes/PublicNote.vue` | 361 |
| `Classes/AssignmentDetail.vue` | 356 |
| `Marketplace/Explore.vue` | 329 |
| `Decks/StudyDeck.vue` | 323 |
| `Focus/FocusPage.vue` | 309 |
| `Planning/PlanningPage.vue` | 289 |
| `Marketplace/PackagePreview.vue` | 263 |
| `Reviews/RevisionStudy.vue` | 241 |
| `Groups/GroupsList.vue` | 241 |
| `Reviews/RevisionSetStats.vue` | 239 |
| `Exam/ExamResults.vue` | 233 |
| `PDFs/PDFs.vue` | 232 |
| `Notes/Notes.vue` | 208 |
| `Exam/ExamSetup.vue` | 190 |
| `Reviews/RevisionBinderStats.vue` | 162 |
| `Reviews/RevisionSetManage.vue` | 160 |
| `Reviews/QcmRun.vue` | 138 |
| `Marketplace/Home.vue` | 122 |
| `Auth/Register.vue` | 115 |
| `Auth/Login.vue` | 107 |
| `Classes/ClassesLanding.vue` | 73 |

Répartition par dossier : Auth (2), Binders (1), Classes (4), Dashboard (1), Decks (2), Diagrams (1), Exam (3), Focus (1), Groups (2), Home (1), Marketplace (3), Notes (6), PDFs (1), Planning (1), Reviews (6) — total 35, cohérent avec le décompte fichier par fichier ci-dessus (note : `Dashboard/` contient 1 fichier alors que `ui-redesign-plan.md` indique une fusion Dashboard+Focus vers `Home/Accueil.vue` — les deux vues `Dashboard.vue` et `FocusPage.vue` existent toujours sur le disque).

### 3.3 Composants réutilisables (`web/src/components/`, 32 fichiers `.vue`)

Sous-dossiers : `classes`, `dashboard`, `decks`, `layout`, `notes`, `pdf`, `planning`, `ui`. Composants dépassant 300 lignes :

| Composant | Lignes |
|---|---|
| `notes/NotePdfExportModal.vue` | 406 |
| `ui/SearchModal.vue` | 376 |
| `layout/AppLayout.vue` | 355 |
| `decks/RevisionItemModal.vue` | 345 |
| `ui/PomodoroTimer.vue` | 332 |

### 3.4 Stores Pinia (`web/src/stores/`, 12 fichiers)

| Store | Lignes |
|---|---|
| `revision.ts` | 323 |
| `decks.ts` | 294 |
| `pomodoro.ts` | 225 |
| `notes.ts` | 141 |
| `binders.ts` | 123 |
| `auth.ts` | 117 |
| `groups.ts` | 116 |
| `pdf.ts` | 105 |
| `focus.ts` | 103 |
| `tags.ts` | 65 |
| `planning.ts` | 61 |
| `notifications.ts` | 46 |

### 3.5 Dépendances frontend clés (`web/package.json`)

Runtime : Vue `^3.5.34`, Vue Router `^4.6.4`, Pinia `^3.0.4`, Vite `^8.0.12`, TailwindCSS `^3.4.19`, `@headlessui/vue` `^1.7.23`, `@vueuse/motion` `^3.0.3`, Axios `^1.16.1`, `dompurify` `^3.4.10`, `highlight.js` `^11.11.1`, `katex` `^0.17.0`, `marked` `^18.0.4`, `lucide-vue-next` / `@lucide/vue`, plugins Capacitor `^8.x` (`core`, `filesystem`, `haptics`, `local-notifications`, `preferences`).
Absents des dépendances : `tiptap`/`@tiptap/*`, `mermaid`, `pdfjs-dist` (ou équivalent).
Dev : TypeScript `~6.0.2`, `vue-tsc` `^3.2.8`, Vitest `^4.1.8` + `@vitest/coverage-v8`, `@vue/test-utils`, `happy-dom`, `@playwright/test` `^1.60.0`, `cross-env`.

---

## 4. Tests & CI

### 4.1 Backend
- 58 fichiers `test_*.py` sous `backend/tests/`.
- 288 fonctions `def test_*` dénombrées (grep, y compris méthodes de classes de test).
- Config dev : `backend/requirements-dev.txt` inclut `pytest-cov`, `factory-boy`, `Faker`, `freezegun`.
- Config coverage/pytest : `backend/pyproject.toml` présent (contenu non détaillé ici).

### 4.2 Frontend
- 17 fichiers de tests unitaires/composants sous `web/tests/` (`components/`, `composables/`, `services/`, `stores/`, `ui/`).
- 69 occurrences `it(`/`test(` dénombrées dans `web/src` + `web/tests`.
- 5 fichiers de tests E2E Playwright sous `web/tests-e2e/` : `diagrams-editor.spec.ts`, `guards.spec.ts`, `note-navigation.spec.ts`, `render-check.spec.ts`, `reviews-ai-flashcards.spec.ts`.
- Aucun fichier `.eslintrc*` ni `eslint.config.*` trouvé sous `web/` (recherche à la racine du dossier).

### 4.3 CI (`.github/workflows/ci.yml`)
Déclenchement : `pull_request` et `push` sur `main`/`develop`, `concurrency` avec annulation des runs redondants. 6 jobs :
1. **backend-tests** — pytest + coverage sur SQLite, `--cov-fail-under=80` (gate bloquant).
2. **backend-tests-postgres** — même suite rejouée sur PostgreSQL 16 (service conteneurisé).
3. **migrations** — applique toutes les migrations sur PostgreSQL vierge, puis lance `flask db migrate` et échoue si une migration est auto-générée (garde anti-drift modèle/migration).
4. **frontend-build** — `vue-tsc` (typecheck) + build Vite production.
5. **frontend-tests** — `vitest run` (`test:run`).
6. **e2e** — Playwright Chromium (`test:e2e`), Vite lancé par Playwright, API mockée.

`docs/testing.md` documente en complément : `main` protégée (pas de push direct), flux `feature/* → develop → main` avec CI verte requise.

### 4.4 Hooks agentiques déjà en place (`.claude/`)
- `settings.json` : 3 hooks seulement — `PostToolUse` (Write/Edit/MultiEdit) → `no_debug.py` puis `no_secrets.py` ; `Stop` → `commit_reminder.py`.
- Aucun hook `PreToolUse` bloquant (`git push`, `rm -rf`, clés API), aucune garde TDD, aucune mécanique `PreCompact`/`SessionStart` de passation de contexte.
- Pas de `.claude/agents/` (aucun subagent défini).
- `.claude/skills/` : 6 skills (`api-spec`, `backend-patterns`, `deployment`, `desktop-build`, `frontend-patterns`, `mobile-build`), chacun avec un `SKILL.md`, référencés depuis `CLAUDE.md` par couche.

---

## 5. Déploiement & environnement

- Un seul `docker-compose.yml` (racine), pas de `docker-compose.prod.yml`, pas de variantes `amd64`/`arm64`, pas de `docker-compose.override.yml`.
- Services déclarés : `db` (postgres:16-alpine), `redis` (redis:7-alpine), `backend` (Flask + gunicorn), `worker` (Celery, `celery_worker:celery_app`, concurrency 2 — tâches async blurting/évaluations IA), `frontend` (build Vite servi, port 80 exposé).
- Variables d'environnement backend/worker : `FLASK_ENV`, `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `JWT_SECRET_KEY`, `JWT_ACCESS_TOKEN_EXPIRES`, `JWT_REFRESH_TOKEN_EXPIRES`, `UPLOAD_FOLDER`, `MAX_CONTENT_LENGTH`, `GEMINI_API_KEY`, `GEMINI_MODEL` — aucune n'est exposée côté `frontend` dans ce fichier.
- Pas de `.env.example` trouvé dans le dépôt (racine, `backend/`, `web/`).
- `desktop/` (Electron) : présent avec sous-dossiers `build/` et `src/`, documenté par `docs/desktop.md` et le skill `desktop-build` — absent de toute mention dans AGENTS.md/README.md.
- `web/android` : projet natif Capacitor déjà généré (`app/`, `build.gradle`, `capacitor.settings.gradle`) — pas de dossier `mobile/` racine.
