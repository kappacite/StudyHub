# StudyHub — Roadmap Fonctionnelle & Guide de Développement Agent

> Ce fichier est destiné à être lu, exécuté et mis à jour par un agent IA au fil du développement.
> Chaque fonctionnalité est autonome et peut être développée indépendamment.
> L'agent doit mettre à jour le statut de chaque étape (`[ ]` → `[x]`) au fur et à mesure.

---

## Instructions pour l'agent

- Lire l'intégralité de `AGENTS.md` avant toute intervention.
- Respecter strictement la séparation en couches : Model → DAO → Service → API → Frontend.
- Aucune logique métier dans les routes Flask. Aucune requête SQL directe dans les services.
- Chaque étape de développement = un commit atomique (Conventional Commits).
- Écrire les tests **avant ou pendant** le code, jamais après.
- Après chaque fonctionnalité complétée, mettre à jour la section `## Journal` en bas de ce fichier.
- Ne jamais modifier ce fichier sans avoir exécuté les tests de régression globaux.

### Commandes de référence

```bash
# Tests backend
cd backend && python -m pytest --cov=app --cov-report=term-missing

# Tests frontend
cd web && npm run test

# Régression complète avant merge
cd backend && python -m pytest && cd ../web && npm run test && npm run build
```

### Ordre de priorité recommandé

1. Tags transversaux (fondation pour Recherche et QCM)
2. Espace Focus — widget + page
3. Planning des révisions
4. Recherche globale
5. Minuteur Pomodoro
6. Import Anki
7. Génération de QCM
8. Mode examen
9. Groupes asynchrones
10. Système professeur

---

## Table des matières

1. [Tags transversaux](#1-tags-transversaux)
2. [Espace Focus](#2-espace-focus)
3. [Planning des révisions](#3-planning-des-révisions)
4. [Recherche globale full-text](#4-recherche-globale-full-text)
5. [Minuteur Pomodoro](#5-minuteur-pomodoro)
6. [Import depuis Anki](#6-import-depuis-anki)
7. [Génération de QCM depuis une note](#7-génération-de-qcm-depuis-une-note)
8. [Mode examen](#8-mode-examen)
9. [Groupes asynchrones](#9-groupes-asynchrones)
10. [Système professeur](#10-système-professeur)
11. [Journal de développement](#11-journal-de-développement)
12. [Tests de régression — projet existant](#12-tests-de-régression--projet-existant)

---

## 1. Tags transversaux

**Statut :** `[x] Terminé`

**Description :** Système de tags utilisables sur toutes les entités (Notes, Decks, Diagrammes, PDFs, Classeurs). Permet de filtrer et regrouper le contenu par thème indépendamment de l'arborescence de classeurs. Socle requis pour la Recherche globale et le Mode examen.

**Priorité :** Haute — plusieurs fonctionnalités en dépendent.

---

### 1.1 Impact architectural

#### Nouveau modèle

```python
# backend/app/models/tag.py
class Tag(Base):
    __tablename__ = "tags"
    id         = Column(Integer, primary_key=True)
    name       = Column(String(50), nullable=False)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    color      = Column(String(7), nullable=True)  # hex couleur ex: "#4F46E5"
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (UniqueConstraint("name", "user_id"),)
```

#### Tables de liaison (many-to-many)

```sql
CREATE TABLE note_tags     (note_id    INTEGER REFERENCES notes(id)    ON DELETE CASCADE,
                            tag_id     INTEGER REFERENCES tags(id)     ON DELETE CASCADE,
                            PRIMARY KEY (note_id, tag_id));

CREATE TABLE deck_tags     (deck_id    INTEGER REFERENCES decks(id)    ON DELETE CASCADE,
                            tag_id     INTEGER REFERENCES tags(id)     ON DELETE CASCADE,
                            PRIMARY KEY (deck_id, tag_id));

CREATE TABLE diagram_tags  (diagram_id INTEGER REFERENCES diagrams(id) ON DELETE CASCADE,
                            tag_id     INTEGER REFERENCES tags(id)     ON DELETE CASCADE,
                            PRIMARY KEY (diagram_id, tag_id));

CREATE TABLE pdf_tags      (pdf_id     INTEGER REFERENCES pdf_documents(id) ON DELETE CASCADE,
                            tag_id     INTEGER REFERENCES tags(id)     ON DELETE CASCADE,
                            PRIMARY KEY (pdf_id, tag_id));

CREATE TABLE binder_tags   (binder_id  INTEGER REFERENCES binders(id) ON DELETE CASCADE,
                            tag_id     INTEGER REFERENCES tags(id)     ON DELETE CASCADE,
                            PRIMARY KEY (binder_id, tag_id));
```

> **Note :** Les colonnes `tags JSON` existantes sur `Binder` doivent être migrées vers ce système puis supprimées.

#### Nouveaux endpoints

```
GET    /api/v1/tags                   → liste des tags de l'utilisateur
POST   /api/v1/tags                   → créer un tag
PUT    /api/v1/tags/:id               → renommer / changer couleur
DELETE /api/v1/tags/:id               → supprimer (retire les liaisons)

POST   /api/v1/notes/:id/tags         → { tag_ids: [1,2,3] } — associer des tags
DELETE /api/v1/notes/:id/tags/:tag_id → retirer un tag d'une note
# Même pattern pour /decks, /diagrams, /pdfs, /binders
```

#### Frontend

- Nouveau composant `TagBadge.vue` dans `components/ui/`
- Nouveau composant `TagSelector.vue` (dropdown multi-select avec création inline)
- Intégrer `TagSelector` dans `NoteEdit.vue`, `Decks/DeckDetail.vue`, `Diagrams.vue`, `PDFs.vue`
- Nouveau store `tags.ts` dans `stores/`
- Ajouter filtre par tag dans toutes les vues liste (Notes, Decks, Diagrams, PDFs)

---

### 1.2 Étapes de développement

#### Backend

- [x] **1.2.1** Créer `backend/app/models/tag.py` avec le modèle `Tag` et les tables de liaison.
  `commit: feat(tags): add Tag model and association tables`

- [x] **1.2.2** Générer la migration Alembic.
  ```bash
  cd backend && flask db migrate -m "add tags system"
  ```
  `commit: chore(db): migration add tags system`

- [x] **1.2.3** Créer `backend/app/dao/tag_dao.py` héritant de `BaseDAO`.
  Méthodes supplémentaires : `get_by_user(user_id)`, `get_tags_for_entity(entity_type, entity_id)`, `set_tags_for_entity(entity_type, entity_id, tag_ids)`.
  `commit: feat(tags): add TagDAO`

- [x] **1.2.4** Créer `backend/app/services/tag_service.py`.
  Règles métier : un tag appartient à un user, max 50 tags par utilisateur, nom max 30 caractères, couleur validée comme hex valide.
  `commit: feat(tags): add TagService with business rules`

- [x] **1.2.5** Créer `backend/app/schemas/tag_schema.py` (Pydantic).
  `TagCreateSchema`, `TagUpdateSchema`, `TagResponseSchema`, `TagListResponseSchema`.
  `commit: feat(tags): add Pydantic schemas`

- [x] **1.2.6** Créer `backend/app/api/v1/tags.py` avec tous les endpoints CRUD.
  Enregistrer le blueprint dans `app/api/v1/__init__.py`.
  `commit: feat(tags): add REST endpoints`

- [x] **1.2.7** Modifier les endpoints existants (`/notes`, `/decks`, `/diagrams`, `/pdfs`, `/binders`) pour accepter le paramètre de filtre `?tag_id=` et inclure les tags dans les réponses.
  `commit: feat(tags): integrate tag filtering in existing endpoints`

- [x] **1.2.8** Migrer les données existantes : lire la colonne `tags JSON` de `Binder`, créer les entrées `Tag` correspondantes, créer les liaisons `binder_tags`, puis supprimer la colonne `tags` de `Binder`.
  Script de migration : `backend/scripts/migrate_binder_tags.py`.
  `commit: chore(db): migrate binder JSON tags to relational tags`

#### Frontend

- [x] **1.2.9** Créer `web/src/stores/tags.ts` (Pinia) avec actions : `fetchTags`, `createTag`, `updateTag`, `deleteTag`, `setTagsForEntity`.
  `commit: feat(tags): add tags Pinia store`

- [x] **1.2.10** Créer `web/src/components/ui/TagBadge.vue` — affiche un badge coloré avec le nom du tag. Props : `tag: Tag`, `removable: boolean`.
  `commit: feat(tags): add TagBadge component`

- [x] **1.2.11** Créer `web/src/components/ui/TagSelector.vue` — dropdown multi-select avec recherche, création inline d'un nouveau tag avec color picker.
  `commit: feat(tags): add TagSelector component`

- [x] **1.2.12** Intégrer `TagSelector` dans `NoteEdit.vue`, `DeckDetail.vue`, `Diagrams.vue`, `PDFs.vue`, `Binders.vue`.
  `commit: feat(tags): integrate TagSelector in all entity views`

- [x] **1.2.13** Ajouter une barre de filtre par tag dans les vues liste de chaque module.
  `commit: feat(tags): add tag filter bar in list views`

---

### 1.3 Tests

```python
# backend/tests/test_tags.py

# Unitaires (TagService)
def test_create_tag_success()
def test_create_tag_duplicate_name_raises_conflict()
def test_create_tag_invalid_color_raises_validation()
def test_max_tags_per_user_raises_limit_error()
def test_delete_tag_removes_all_associations()
def test_set_tags_for_note_replaces_existing()

# Intégration (endpoints)
def test_get_tags_requires_auth()
def test_post_tag_creates_and_returns_201()
def test_filter_notes_by_tag_id()
def test_filter_decks_by_tag_id()
def test_tag_belongs_to_user_isolation()  # user A ne voit pas les tags de user B
```

```typescript
// web/src/components/ui/__tests__/TagBadge.test.ts
// web/src/components/ui/__tests__/TagSelector.test.ts
// Test : affichage, sélection, création inline, suppression
```

### 1.4 Tests de régression obligatoires

Après cette fonctionnalité, vérifier :
- `GET /api/v1/notes` retourne toujours les notes sans tag (pas de régression filtre)
- `GET /api/v1/binders` — la colonne `tags` JSON n'est plus présente dans les réponses
- Les tests existants `test_notes.py`, `test_decks.py`, `test_binders.py` passent sans modification

---

## 2. Espace Focus

**Statut :** `[x] Terminé`

**Dépendances :** Aucune (peut être développé en parallèle de la feature 1)

**Description :** Deux surfaces complémentaires. Un widget compact sur le dashboard existant ("coup d'œil + action rapide") et une page dédiée `/focus` avec trois zones : file du jour, graphique de charge 14 jours, rétention par matière.

---

### 2.1 Impact architectural

#### Nouveaux endpoints backend

```
GET /api/v1/focus/today
  → {
      total_due: int,
      late_count: int,
      flashcard_count: int,
      blurting_count: int,
      items: [{ type: "deck"|"note", id, title, count, is_late, last_session_ago_days }]
    }

GET /api/v1/focus/forecast?days=14
  → { forecast: [{ date: "YYYY-MM-DD", count: int, load_level: "low"|"medium"|"high" }] }

GET /api/v1/focus/retention
  → { by_subject: [{ binder_id, binder_name, retention_pct, overdue_count, trend_7d }] }
```

> **Règle de calcul `forecast`** : pour chaque deck, compter les flashcards dont `next_review` tombe entre `today` et `today + N days`. Grouper par date.

> **Règle `retention`** : `retention_pct` = `cards_correct / cards_reviewed` sur les 30 derniers jours pour les sessions liées aux decks d'un classeur. `trend_7d` = différence entre la moyenne des 7 derniers jours et la moyenne des 7 jours précédents.

#### Nouveau service backend

`backend/app/services/focus_service.py`
- `get_today_items(user_id)` — interroge `FlashcardDAO` (filtre `next_review <= today`) et `NoteDAO` (filtre `last_blurting_session > X jours`)
- `get_forecast(user_id, days)` — requête agrégée sur `flashcards.next_review`
- `get_retention_by_subject(user_id)` — requête agrégée sur `study_sessions`

#### Frontend

- `web/src/views/Focus/FocusPage.vue` — nouvelle vue complète
- `web/src/components/dashboard/FocusWidget.vue` — widget compact intégré dans `Dashboard.vue`
- `web/src/stores/focus.ts` — store Pinia dédié
- Nouveau service `web/src/services/focusService.ts`
- Ajouter la route `/focus` dans `router/index.ts` (protégée, auth requise)

---

### 2.2 Étapes de développement

#### Backend

- [x] **2.2.1** Créer `backend/app/services/focus_service.py` avec les trois méthodes de calcul.
  `commit: feat(focus): add FocusService with today/forecast/retention logic`

- [x] **2.2.2** Créer `backend/app/schemas/focus_schema.py` (Pydantic) pour les trois réponses.
  `commit: feat(focus): add Pydantic response schemas`

- [x] **2.2.3** Créer `backend/app/api/v1/focus.py` avec les trois endpoints GET.
  Enregistrer le blueprint.
  `commit: feat(focus): add /focus REST endpoints`

#### Frontend

- [x] **2.2.4** Créer `web/src/services/focusService.ts` avec trois fonctions wrappant les appels Axios.
  `commit: feat(focus): add focusService`

- [x] **2.2.5** Créer `web/src/stores/focus.ts` avec state : `todayItems`, `forecast`, `retention`. Actions : `loadFocusData()` (appelle les trois endpoints en parallèle avec `Promise.all`).
  `commit: feat(focus): add focus Pinia store`

- [x] **2.2.6** Créer `web/src/components/dashboard/FocusWidget.vue`.
  Affiche : total du jour, badges (retard / cartes / blurting), mini-sparkline 7 jours (SVG inline), streak, bouton "Lancer la révision", lien "Voir le détail".
  `commit: feat(focus): add FocusWidget component`

- [x] **2.2.7** Intégrer `FocusWidget` dans `web/src/views/Dashboard/Dashboard.vue` en position haute.
  `commit: feat(focus): integrate FocusWidget in Dashboard`

- [x] **2.2.8** Créer `web/src/views/Focus/FocusPage.vue` avec les trois zones :
  - **Zone Maintenant** : liste des items du jour avec code couleur (rouge = retard, neutre = normal, violet = blurting). Bouton "Réviser" par item + bouton "Tout réviser".
  - **Zone Forecast** : graphique en barres 14 jours avec légende de charge (bas/moyen/haut).
  - **Zone Rétention** : tableau par matière avec barre de progression, tendance, count retard.
  `commit: feat(focus): add FocusPage view`

- [x] **2.2.9** Ajouter la route `/focus` dans `router/index.ts`.
  Ajouter l'entrée dans la sidebar (`AppLayout.vue`).
  `commit: feat(focus): add /focus route and sidebar entry`

- [x] **2.2.10** Implémenter le bouton "Tout réviser" : construit une file d'items ordonnée (retards d'abord, puis SM-2 du jour, puis blurting) et navigue vers le premier item. État de la file géré dans le store.
  `commit: feat(focus): implement unified review queue`

---

### 2.3 Tests

```python
# backend/tests/test_focus.py
def test_today_items_returns_only_due_cards()
def test_today_items_marks_late_correctly()        # next_review < today-1
def test_forecast_counts_correct_for_known_deck()
def test_retention_calculation_30_days()
def test_retention_trend_positive_negative()
def test_focus_endpoints_require_auth()
def test_user_isolation_focus_data()
```

```typescript
// web/src/stores/__tests__/focus.test.ts
// Test : loadFocusData appelle les 3 endpoints, gère les erreurs, state correct
// web/src/components/dashboard/__tests__/FocusWidget.test.ts
// Test : affiche le bon total, badge retard visible si late_count > 0
```

### 2.4 Tests de régression obligatoires

- `GET /api/v1/stats/overview` — toujours fonctionnel (partage la logique sessions)
- `GET /api/v1/decks/:id/study` — toujours fonctionnel (même source de données)
- Dashboard existant s'affiche sans erreur avec le widget ajouté

---

## 3. Planning des révisions

**Statut :** `[x] Terminé`

**Dépendances :** Feature 2 (Espace Focus) pour cohérence des données

**Description :** Vue calendaire hebdomadaire (et mensuelle) qui affiche la charge SM-2 prévue par jour. L'étudiant peut voir les pics à venir et lancer des "révisions anticipées" pour lisser sa charge.

---

### 3.1 Impact architectural

#### Nouveaux endpoints

```
GET /api/v1/planning/calendar?from=YYYY-MM-DD&to=YYYY-MM-DD
  → { days: [{ date, total_due, breakdown: [{ deck_id, deck_name, count }] }] }

POST /api/v1/planning/advance
  Body: { deck_id: int, card_ids: [int] }
  → 200 OK — déclenche une révision anticipée (ne modifie pas next_review avant que l'utilisateur ait répondu)
```

> **Règle métier révision anticipée** : quand un étudiant révise une carte avant sa `next_review`, l'algorithme SM-2 s'applique normalement mais l'intervalle calculé repart de `today` (et non de `next_review`), ce qui revient à légèrement réduire le bénéfice de la révision anticipée. Documenter ce comportement dans le code.

#### Frontend

- `web/src/views/Planning/PlanningPage.vue`
- `web/src/components/planning/WeekCalendar.vue` — grille 7 colonnes, barres de charge par jour
- `web/src/components/planning/MonthCalendar.vue` — vue mensuelle avec heatmap de charge
- `web/src/stores/planning.ts`

---

### 3.2 Étapes de développement

#### Backend

- [x] **3.2.1** Ajouter `get_cards_due_between(user_id, date_from, date_to)` dans `FlashcardDAO`.
  Retourne les cartes groupées par `next_review` et par `deck_id`.
  `commit: feat(planning): add date-range query in FlashcardDAO`

- [x] **3.2.2** Créer `backend/app/services/planning_service.py`.
  - `get_calendar(user_id, date_from, date_to)` — agrège par jour
  - `advance_review(user_id, deck_id, card_ids)` — valide l'appartenance, délègue à `SpacedRepetitionService`
  `commit: feat(planning): add PlanningService`

- [x] **3.2.3** Créer `backend/app/api/v1/planning.py` avec les deux endpoints.
  `commit: feat(planning): add /planning REST endpoints`

#### Frontend

- [x] **3.2.4** Créer `web/src/stores/planning.ts`.
  `commit: feat(planning): add planning Pinia store`

- [x] **3.2.5** Créer `web/src/components/planning/WeekCalendar.vue`.
  Chaque colonne = un jour. Barre de charge colorée (vert < 10, orange 10-25, rouge > 25). Clic sur une barre = popover avec le détail par deck.
  `commit: feat(planning): add WeekCalendar component`

- [x] **3.2.6** Créer `web/src/components/planning/MonthCalendar.vue`.
  Grille mensuelle, chaque cellule colorée selon la charge. Style heatmap similaire au dashboard GitHub-style existant.
  `commit: feat(planning): add MonthCalendar component`

- [x] **3.2.7** Créer `web/src/views/Planning/PlanningPage.vue`.
  Toggle semaine / mois. Bouton "Révisions anticipées" sur les jours à forte charge — ouvre une modale listant les decks concernés avec case à cocher.
  `commit: feat(planning): add PlanningPage view`

- [x] **3.2.8** Ajouter la route `/planning` dans le router et la sidebar.
  `commit: feat(planning): add /planning route and sidebar entry`

---

### 3.3 Tests

```python
def test_calendar_returns_correct_counts()
def test_calendar_empty_range_returns_empty_days()
def test_advance_review_forbidden_for_other_user_card()
def test_advance_review_applies_sm2_from_today()
def test_sm2_interval_not_inflated_by_advance()
```

---

## 4. Recherche globale full-text

**Statut :** `[x] Terminé`

**Dépendances :** Feature 1 (Tags transversaux) pour inclure les tags dans les résultats

**Description :** Barre de recherche universelle (`Ctrl+K` / `Cmd+K`) qui cherche dans toutes les entités de l'utilisateur (Notes, Decks, Flashcards, Diagrammes, PDFs, Classeurs) et retourne des résultats groupés par type avec extrait contextuel.

---

### 4.1 Impact architectural

#### Stratégie technique

Utiliser **PostgreSQL Full-Text Search** (`tsvector` / `tsquery`). En mode développement SQLite, fallback sur `LIKE` insensible à la casse. La différence est encapsulée dans le `SearchDAO`.

#### Modifications modèles

Ajouter des colonnes `search_vector` (type `TSVECTOR`) sur `Note`, `Deck`, `Flashcard`, `Diagram` pour PostgreSQL. Maintenues automatiquement via trigger SQL ou update explicite à chaque save.

```sql
-- Exemple sur notes
ALTER TABLE notes ADD COLUMN search_vector TSVECTOR;
CREATE INDEX notes_search_idx ON notes USING GIN(search_vector);
CREATE TRIGGER notes_search_update BEFORE INSERT OR UPDATE ON notes
  FOR EACH ROW EXECUTE FUNCTION tsvector_update_trigger(search_vector, 'pg_catalog.french', 'title', 'content');
```

#### Nouveau endpoint

```
GET /api/v1/search?q=<query>&types=note,deck,flashcard,diagram&limit=20
  → {
      query: str,
      results: {
        notes:      [{ id, title, excerpt, binder_id, tags, score }],
        decks:      [{ id, name, excerpt, binder_id, tags, score }],
        flashcards: [{ id, front, deck_id, deck_name, score }],
        diagrams:   [{ id, title, binder_id, score }]
      },
      total: int
    }
```

> **Règle** : les PDFs ne sont pas indexés full-text (contenu binaire). Seul le `name` du document est cherché.

#### Frontend

- `web/src/components/ui/SearchModal.vue` — modale de recherche universelle (overlay plein écran)
- `web/src/composables/useSearch.ts` — debounce 300ms, annulation de requête en vol (AbortController)
- Raccourci clavier `Ctrl+K` / `Cmd+K` enregistré dans `AppLayout.vue`

---

### 4.2 Étapes de développement

#### Backend

- [x] **4.2.1** Créer `backend/app/dao/search_dao.py`.
  - `search_all(user_id, query, types, limit)` — détecte le moteur DB (PostgreSQL vs SQLite) et utilise la stratégie appropriée.
  - Méthode privée `_pg_search` (tsvector) et `_sqlite_search` (LIKE).
  `commit: feat(search): add SearchDAO with dual-engine strategy`

- [x] **4.2.2** Générer la migration pour les colonnes `search_vector` et les triggers PostgreSQL.
  La migration doit être no-op sur SQLite (vérifier le dialecte dans la migration Alembic).
  `commit: chore(db): migration add full-text search vectors`

- [x] **4.2.3** Créer `backend/app/services/search_service.py`.
  - Sanitise la query (longueur min 2 chars, max 100 chars, strip caractères spéciaux)
  - Formate les extraits (`excerpt`) : 150 chars autour du premier match, avec `<mark>` autour du terme trouvé
  `commit: feat(search): add SearchService with excerpt formatting`

- [x] **4.2.4** Créer `backend/app/api/v1/search.py` avec l'endpoint GET.
  `commit: feat(search): add /search REST endpoint`

#### Frontend

- [x] **4.2.5** Créer `web/src/composables/useSearch.ts`.
  Gère : debounce 300ms, AbortController pour annuler les requêtes en vol, état `isLoading`, `results`, `error`.
  `commit: feat(search): add useSearch composable`

- [x] **4.2.6** Créer `web/src/components/ui/SearchModal.vue`.
  - Overlay avec fond semi-transparent, animation d'apparition
  - Input avec focus automatique à l'ouverture
  - Résultats groupés par type avec icônes
  - Mise en évidence du terme recherché (rendu du `<mark>`)
  - Navigation clavier (flèches + Entrée pour ouvrir, Échap pour fermer)
  - État vide, état chargement, état erreur
  `commit: feat(search): add SearchModal component`

- [x] **4.2.7** Enregistrer le raccourci `Ctrl+K` / `Cmd+K` dans `AppLayout.vue` pour ouvrir `SearchModal`.
  `commit: feat(search): register global keyboard shortcut`

---

### 4.3 Tests

```python
def test_search_returns_notes_matching_query()
def test_search_filters_by_type()
def test_search_user_isolation()        # résultats d'un autre user jamais retournés
def test_search_query_too_short_returns_400()
def test_search_excerpt_contains_mark_tag()
def test_search_sqlite_fallback_works()
```

```typescript
// Test useSearch : debounce, annulation en vol, résultats vides
// Test SearchModal : navigation clavier, affichage résultats, fermeture Échap
```

---

## 5. Minuteur Pomodoro

**Statut :** `[x] Terminé`

**Dépendances :** Aucune

**Description :** Minuteur configurable intégré à l'interface. Lance une session d'étude chronométrée (par défaut 25 min travail / 5 min pause). À la fin d'une session, enregistre automatiquement une `StudySession` dans la base. Notifications locales via Capacitor sur mobile.

---

### 5.1 Impact architectural

Purement frontend + appel à l'endpoint `POST /api/v1/stats/sessions` déjà existant. Aucun nouveau endpoint nécessaire.

#### Frontend

- `web/src/composables/usePomodoro.ts` — logique du timer (état, countdown, transitions travail/pause)
- `web/src/components/ui/PomodoroTimer.vue` — widget flottant persistant (bas de l'écran)
- Intégration de `@capacitor/local-notifications` pour la notification de fin de session

---

### 5.2 Étapes de développement

- [x] **5.2.1** Créer `web/src/composables/usePomodoro.ts`.
  État : `phase` ("work" | "break" | "idle"), `remaining_seconds`, `session_count`, `is_running`.
  Actions : `start()`, `pause()`, `reset()`, `skip()`.
  Configuration : `work_minutes` (défaut 25), `break_minutes` (défaut 5), `long_break_minutes` (défaut 15, toutes les 4 sessions).
  À la fin d'une phase "work" : appeler `POST /api/v1/stats/sessions` avec `module: "pomodoro"`, `duration_seconds`.
  `commit: feat(pomodoro): add usePomodoro composable`

- [x] **5.2.2** Créer `web/src/components/ui/PomodoroTimer.vue`.
  Widget compact (coin bas-droite), toujours visible quand actif. Affiche le countdown, la phase, le compte de sessions. Boutons play/pause/reset. Cercle SVG animé comme indicateur de progression.
  `commit: feat(pomodoro): add PomodoroTimer widget component`

- [x] **5.2.3** Intégrer `PomodoroTimer` dans `AppLayout.vue` (visible sur toutes les pages).
  `commit: feat(pomodoro): integrate PomodoroTimer in global layout`

- [x] **5.2.4** Ajouter un écran de configuration dans les Settings (durées personnalisables, activer/désactiver les sons).
  `commit: feat(pomodoro): add pomodoro settings`

- [x] **5.2.5** Intégrer `@capacitor/local-notifications` : déclencher une notification à la fin de chaque phase. Conditionner à `usePlatform().isNative`.
  `commit: feat(pomodoro): add native notifications via Capacitor`

---

### 5.3 Tests

```typescript
// Test usePomodoro :
// - countdown décrémente correctement
// - transition work → break après expiration
// - appel POST /stats/sessions en fin de phase work
// - long break après 4 sessions
// - reset remet à l'état initial
```

---

## 6. Import depuis Anki

**Statut :** `[x] Terminé`

**Dépendances :** Aucune

**Description :** Importer des decks Anki (format `.apkg`) dans StudyHub. Le format `.apkg` est une archive ZIP contenant une base SQLite (`collection.anki2`). L'import crée un `Deck` et ses `Flashcard` dans StudyHub, en mappant les champs Anki vers `front` / `back`.

---

### 6.1 Impact architectural

#### Dépendance Python à ajouter

```
# backend/requirements.txt
zipfile   # stdlib, déjà disponible
sqlite3   # stdlib, déjà disponible
```

Aucune dépendance externe requise.

#### Nouveau endpoint

```
POST /api/v1/import/anki
  Content-Type: multipart/form-data
  Body: file (.apkg), binder_id (optionnel)
  → 201 Created { deck_id, deck_name, cards_imported, cards_skipped, warnings: [] }
```

> **Contrainte taille** : le fichier `.apkg` est soumis au `MAX_CONTENT_LENGTH` global (50 MB). Ajouter une validation explicite du MIME type et de l'extension.

#### Logique de mapping Anki → StudyHub

Le format Anki stocke les cartes dans la table `notes` (≠ nos notes) avec un champ `flds` contenant les champs séparés par `\x1f`. Le premier champ = recto, le second = verso. Les modèles complexes (3 champs+) : seuls les deux premiers sont importés, un warning est ajouté.

---

### 6.2 Étapes de développement

#### Backend

- [x] **6.2.1** Créer `backend/app/utils/anki_parser.py`.
  - `parse_apkg(file_bytes)` → `AnkiDeck(name, cards: List[AnkiCard])`
  - Décompresse le ZIP, ouvre le SQLite en mémoire, lit `notes.flds` et `col.decks`
  - Gère les erreurs : fichier corrompu, ZIP invalide, SQLite illisible
  `commit: feat(import): add Anki .apkg parser utility`

- [x] **6.2.2** Créer `backend/app/services/import_service.py`.
  - `import_anki(user_id, file_bytes, binder_id)` → résultat d'import
  - Valide le fichier, parse, crée le `Deck` via `DeckDAO`, crée les `Flashcard` via `FlashcardDAO`
  - Initialise les paramètres SM-2 par défaut pour chaque carte (`ease_factor=2.5`, `interval=0`, `repetitions=0`, `next_review=today`)
  - Les cartes HTML Anki (contenu avec balises) sont importées telles quelles ; ajouter un warning si détecté
  `commit: feat(import): add ImportService for Anki decks`

- [x] **6.2.3** Créer `backend/app/api/v1/imports.py` avec l'endpoint POST.
  `commit: feat(import): add /import/anki REST endpoint`

#### Frontend

- [x] **6.2.4** Créer `web/src/components/decks/AnkiImportModal.vue`.
  - Zone de drop de fichier (drag & drop + input classique)
  - Validation côté client : extension `.apkg`, taille < 50 MB
  - Sélecteur de classeur de destination (optionnel)
  - Affichage du résultat : X cartes importées, warnings éventuels
  `commit: feat(import): add AnkiImportModal component`

- [x] **6.2.5** Ajouter un bouton "Importer depuis Anki" dans la vue `Decks.vue`.
  `commit: feat(import): add import button in Decks view`

---

### 6.3 Tests

```python
def test_parse_valid_apkg_returns_cards()
def test_parse_corrupted_file_raises_error()
def test_parse_multi_field_card_uses_first_two_fields()
def test_import_creates_deck_and_cards_in_db()
def test_import_sets_default_sm2_parameters()
def test_import_wrong_mimetype_returns_400()
def test_import_file_too_large_returns_413()
def test_import_user_isolation()
```

---

## 7. Génération de QCM depuis une note

**Statut :** `[x] Terminé`

**Dépendances :** Aucune (mais cohérent à développer après le blurting existant)

**Description :** À partir du contenu d'une note, l'IA (Gemini) génère 5 à 10 questions à choix multiples (4 options, 1 seule correcte). L'étudiant répond aux questions dans une interface dédiée et obtient un score. Les questions incorrectes peuvent être converties en flashcards.

---

### 7.1 Impact architectural

#### Nouveaux modèles

```python
# backend/app/models/quiz.py
class Quiz(Base):
    __tablename__ = "quizzes"
    id         = Column(Integer, primary_key=True)
    note_id    = Column(Integer, ForeignKey("notes.id"), nullable=False)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    score_pct  = Column(Float, nullable=True)   # null = non complété
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    id             = Column(Integer, primary_key=True)
    quiz_id        = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question_text  = Column(Text, nullable=False)
    options        = Column(JSON, nullable=False)  # [{"id": "a", "text": "...", "correct": bool}]
    user_answer_id = Column(String(1), nullable=True)  # "a", "b", "c", "d"
```

#### Nouveaux endpoints

```
POST /api/v1/notes/:id/quiz/generate
  Body: { question_count: int (5-10, défaut 7) }
  → 201 Created { quiz_id, questions: [...] }

POST /api/v1/quizzes/:quiz_id/answer
  Body: { question_id: int, answer_id: str }
  → 200 OK { is_correct: bool, correct_answer_id: str }

POST /api/v1/quizzes/:quiz_id/complete
  → 200 OK { score_pct: float, wrong_questions: [...] }

POST /api/v1/quizzes/:quiz_id/create-flashcards
  Body: { question_ids: [int], deck_id: int }
  → 201 Created { created: int }
```

> **Rate limiting** : l'endpoint `generate` appelle Gemini. Appliquer `flask-limiter` : max 10 générations par heure par utilisateur.

#### Prompt Gemini pour la génération

```python
QUIZ_GENERATION_PROMPT = """
Tu es un assistant pédagogique. À partir du texte suivant, génère exactement {count} questions à choix multiples.

Règles strictes :
- Chaque question a exactement 4 options (a, b, c, d)
- Une seule option est correcte
- Les mauvaises réponses doivent être plausibles (pas triviales)
- Couvre les concepts les plus importants du texte
- Les questions doivent être en français

Réponds UNIQUEMENT en JSON valide, sans markdown, sans commentaires :
[
  {{
    "question": "...",
    "options": [
      {{"id": "a", "text": "...", "correct": false}},
      {{"id": "b", "text": "...", "correct": true}},
      {{"id": "c", "text": "...", "correct": false}},
      {{"id": "d", "text": "...", "correct": false}}
    ]
  }}
]

Texte source :
{content}
"""
```

---

### 7.2 Étapes de développement

#### Backend

- [x] **7.2.1** Créer `backend/app/models/quiz.py` avec `Quiz` et `QuizQuestion`.
  `commit: feat(quiz): add Quiz and QuizQuestion models`

- [x] **7.2.2** Générer la migration Alembic.
  `commit: chore(db): migration add quizzes tables`

- [x] **7.2.3** Créer `backend/app/dao/quiz_dao.py`.
  `commit: feat(quiz): add QuizDAO`

- [x] **7.2.4** Étendre `backend/app/services/ai_service.py` avec la méthode `generate_quiz(note_content, count)`.
  Gérer les erreurs Gemini (timeout, réponse JSON invalide, quota dépassé).
  `commit: feat(quiz): add generate_quiz in AIService`

- [x] **7.2.5** Créer `backend/app/services/quiz_service.py`.
  `commit: feat(quiz): add QuizService`

- [x] **7.2.6** Créer `backend/app/api/v1/quiz.py` avec les 4 endpoints.
  Appliquer `flask-limiter` sur `/generate` : `@limiter.limit("10 per hour")`.
  `commit: feat(quiz): add quiz REST endpoints with rate limiting`

#### Frontend

- [x] **7.2.7** Créer `web/src/views/Notes/NoteQuiz.vue`.
  - État "génération" : spinner + message d'attente
  - État "en cours" : une question à la fois, 4 boutons options, pas de retour arrière
  - État "résultat" : score, liste des questions ratées avec la bonne réponse, bouton "Créer des flashcards"
  `commit: feat(quiz): add NoteQuiz view`

- [x] **7.2.8** Ajouter un bouton "Générer un QCM" dans `NoteEdit.vue`.
  `commit: feat(quiz): add quiz generation button in NoteEdit`

---

### 7.3 Tests

```python
def test_generate_quiz_creates_quiz_and_questions()
def test_generate_quiz_rate_limit_enforced()
def test_answer_question_returns_correct_flag()
def test_complete_quiz_calculates_score()
def test_create_flashcards_from_wrong_answers()
def test_quiz_belongs_to_note_user_only()
def test_ai_service_handles_gemini_invalid_json()
```

---

## 8. Mode examen

**Statut :** `[x] Terminé`

**Dépendances :** Feature 7 (QCM) recommandée, Feature 1 (Tags) pour filtrer par matière

**Description :** Session d'évaluation chronométrée qui simule les conditions d'examen. Mélange des flashcards SM-2 dues et des QCM générés depuis les notes d'un classeur donné. Interface épurée sans accès aux cours. Score final avec bilan détaillé.

---

### 8.1 Impact architectural

#### Nouveaux endpoints

```
POST /api/v1/exam/start
  Body: { binder_id: int, duration_minutes: int (15-120), include_flashcards: bool, include_qcm: bool, question_limit: int (10-50) }
  → 201 Created { session_id, items: [...], total_items: int, duration_seconds: int }

POST /api/v1/exam/:session_id/answer
  Body: { item_type: "flashcard"|"qcm", item_id: int, answer: str|int }
  → 200 OK { is_correct: bool }

POST /api/v1/exam/:session_id/complete
  → 200 OK { score_pct, flashcard_score, qcm_score, time_taken_seconds, breakdown: [...] }
```

#### Nouveau modèle

```python
class ExamSession(Base):
    __tablename__ = "exam_sessions"
    id              = Column(Integer, primary_key=True)
    user_id         = Column(Integer, ForeignKey("users.id"))
    binder_id       = Column(Integer, ForeignKey("binders.id"))
    duration_seconds = Column(Integer, nullable=False)
    started_at      = Column(DateTime, server_default=func.now())
    completed_at    = Column(DateTime, nullable=True)
    score_pct       = Column(Float, nullable=True)
    items_snapshot  = Column(JSON, nullable=False)  # snapshot des questions au moment du lancement
```

---

### 8.2 Étapes de développement

#### Backend

- [x] **8.2.1** Créer le modèle `ExamSession` et la migration.
  `commit: feat(exam): add ExamSession model and migration`

- [x] **8.2.2** Créer `backend/app/services/exam_service.py`.
  - `start_exam(user_id, binder_id, config)` : récupère les flashcards dues du classeur + génère ou récupère des QCM depuis les notes du classeur. Mélange et sérialise le snapshot.
  - `submit_answer(session_id, item)` : évalue la réponse selon le type.
  - `complete_exam(session_id)` : calcule les scores, enregistre une `StudySession`.
  `commit: feat(exam): add ExamService`

- [x] **8.2.3** Créer `backend/app/api/v1/exam.py`.
  `commit: feat(exam): add exam REST endpoints`

#### Frontend

- [x] **8.2.4** Créer `web/src/views/Exam/ExamSetup.vue` — formulaire de configuration (classeur, durée, types de questions).
  `commit: feat(exam): add ExamSetup view`

- [x] **8.2.5** Créer `web/src/views/Exam/ExamSession.vue` — interface épurée : une question à la fois, chronomètre décompte, barre de progression, pas de navigation, pas de sidebar.
  `commit: feat(exam): add ExamSession view (distraction-free)`

- [x] **8.2.6** Créer `web/src/views/Exam/ExamResults.vue` — score global, score par type, liste des erreurs avec corrections.
  `commit: feat(exam): add ExamResults view`

- [x] **8.2.7** Configurer le router pour que les routes `/exam/session` masquent la sidebar (`AppLayout` sans navigation).
  `commit: feat(exam): configure distraction-free layout for exam`

---

### 8.3 Tests

```python
def test_start_exam_creates_session_with_snapshot()
def test_exam_snapshot_immutable_after_start()  # les questions ne changent pas si le deck change
def test_complete_exam_calculates_composite_score()
def test_exam_expired_session_rejected()
def test_exam_user_isolation()
```

---

## 9. Groupes asynchrones

**Statut :** `[x] Terminé`

**Dépendances :** Feature 1 (Tags) recommandée

**Description :** Des étudiants se regroupent autour d'une matière. Un groupe possède des classeurs partagés (lecture seule ou lecture/écriture selon le rôle), un fil d'activité asynchrone, et une vue de progression des membres. Pas de temps réel — tout est asynchrone.

---

### 9.1 Impact architectural

#### Nouveaux modèles

```python
class Group(Base):
    __tablename__ = "groups"
    id          = Column(Integer, primary_key=True)
    name        = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    invite_code = Column(String(8), unique=True, nullable=False)  # code court pour rejoindre
    created_by  = Column(Integer, ForeignKey("users.id"))
    created_at  = Column(DateTime, server_default=func.now())

class GroupMember(Base):
    __tablename__ = "group_members"
    group_id   = Column(Integer, ForeignKey("groups.id"), primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role       = Column(String(10), nullable=False)  # "owner" | "admin" | "member"
    joined_at  = Column(DateTime, server_default=func.now())

class GroupBinder(Base):
    __tablename__ = "group_binders"
    group_id    = Column(Integer, ForeignKey("groups.id"), primary_key=True)
    binder_id   = Column(Integer, ForeignKey("binders.id"), primary_key=True)
    permission  = Column(String(10), nullable=False)  # "read" | "write"
    pinned      = Column(Boolean, default=False)
    added_by    = Column(Integer, ForeignKey("users.id"))
    added_at    = Column(DateTime, server_default=func.now())

class GroupActivity(Base):
    __tablename__ = "group_activities"
    id          = Column(Integer, primary_key=True)
    group_id    = Column(Integer, ForeignKey("groups.id"))
    user_id     = Column(Integer, ForeignKey("users.id"))
    type        = Column(String(30))  # "joined" | "shared_binder" | "completed_session" | "posted_note"
    payload     = Column(JSON, nullable=True)
    created_at  = Column(DateTime, server_default=func.now())
```

#### Endpoints principaux

```
POST   /api/v1/groups                          → créer un groupe
GET    /api/v1/groups                          → mes groupes
GET    /api/v1/groups/:id                      → détails + membres + classeurs partagés
POST   /api/v1/groups/join                     Body: { invite_code }
DELETE /api/v1/groups/:id/members/:user_id     → quitter ou exclure
PATCH  /api/v1/groups/:id/members/:user_id     Body: { role }
POST   /api/v1/groups/:id/binders             Body: { binder_id, permission }
DELETE /api/v1/groups/:id/binders/:binder_id
GET    /api/v1/groups/:id/activity             → fil d'activité paginé
GET    /api/v1/groups/:id/members/progress     → stats de révision par membre (7j)
```

> **Règle de confidentialité** : `GET /groups/:id/members/progress` retourne uniquement les données agrégées (temps total, cartes révisées). Jamais le contenu des notes ou flashcards d'un autre membre.

---

### 9.2 Étapes de développement

#### Backend

- [x] **9.2.1** Créer les 4 modèles et la migration.
  `commit: feat(groups): add Group, GroupMember, GroupBinder, GroupActivity models`

- [x] **9.2.2** Créer `backend/app/dao/group_dao.py`.
  `commit: feat(groups): add GroupDAO`

- [x] **9.2.3** Créer `backend/app/services/group_service.py`.
  Règles : un utilisateur peut créer max 5 groupes, appartenir à max 20 groupes. Le code d'invitation est un string aléatoire 8 chars alphanumériques.
  `commit: feat(groups): add GroupService with business rules`

- [x] **9.2.4** Créer `backend/app/api/v1/groups.py` avec tous les endpoints.
  `commit: feat(groups): add groups REST endpoints`

- [x] **9.2.5** Enregistrer automatiquement une `GroupActivity` lors des événements : join, share binder, complete study session (via `StatsService`).
  `commit: feat(groups): add activity tracking hooks`

#### Frontend

- [x] **9.2.6** Créer `web/src/views/Groups/GroupsList.vue` — liste des groupes rejoints + bouton créer + champ "rejoindre avec un code".
  `commit: feat(groups): add GroupsList view`

- [x] **9.2.7** Créer `web/src/views/Groups/GroupDetail.vue` — onglets : Classeurs partagés / Activité / Membres / Progression.
  `commit: feat(groups): add GroupDetail view`

- [x] **9.2.8** Créer `web/src/stores/groups.ts`.
  `commit: feat(groups): add groups Pinia store`

- [x] **9.2.9** Ajouter l'entrée "Groupes" dans la sidebar.
  `commit: feat(groups): add groups entry in sidebar`

---

### 9.3 Tests

```python
def test_create_group_generates_unique_invite_code()
def test_join_group_by_invite_code()
def test_join_invalid_code_returns_404()
def test_max_groups_per_user_enforced()
def test_share_binder_requires_owner_role()
def test_member_cannot_access_other_member_flashcards()
def test_progress_endpoint_returns_only_aggregated_data()
def test_activity_recorded_on_join()
```

---

## 10. Système professeur

**Statut :** `[x] Terminé`

**Dépendances :** Feature 9 (Groupes asynchrones) — le système professeur est une extension des groupes avec des rôles et fonctionnalités supplémentaires.

**Description :** Un utilisateur peut créer un "Espace de cours" (groupe de type "classe"). En tant que professeur, il peut publier des classeurs officiels, assigner des révisions avec deadline, et consulter la progression individuelle de chaque élève. Les élèves voient les devoirs assignés dans leur Espace Focus.

---

### 10.1 Impact architectural

> Ce système étend les Groupes (Feature 9). Il faut avoir complété la Feature 9 avant de démarrer celle-ci.

#### Modifications modèles

```python
# Étendre Group
class Group(Base):
    # ... colonnes existantes ...
    type      = Column(String(10), default="study")  # "study" | "class"
    is_class  = Column(Boolean, default=False)        # shortcut

# Nouveau modèle
class Assignment(Base):
    __tablename__ = "assignments"
    id          = Column(Integer, primary_key=True)
    group_id    = Column(Integer, ForeignKey("groups.id"), nullable=False)
    binder_id   = Column(Integer, ForeignKey("binders.id"), nullable=False)
    title       = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    due_date    = Column(DateTime, nullable=True)
    created_by  = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at  = Column(DateTime, server_default=func.now())

class AssignmentProgress(Base):
    __tablename__ = "assignment_progress"
    assignment_id  = Column(Integer, ForeignKey("assignments.id"), primary_key=True)
    user_id        = Column(Integer, ForeignKey("users.id"), primary_key=True)
    cards_reviewed = Column(Integer, default=0)
    score_pct      = Column(Float, nullable=True)
    completed_at   = Column(DateTime, nullable=True)
```

#### Nouveaux endpoints

```
POST   /api/v1/classes                                → créer une classe (type "class")
GET    /api/v1/classes/:id/assignments                → liste des devoirs
POST   /api/v1/classes/:id/assignments                → créer un devoir (rôle teacher requis)
GET    /api/v1/classes/:id/assignments/:asgn_id       → détails + progression par élève
DELETE /api/v1/classes/:id/assignments/:asgn_id

GET    /api/v1/classes/:id/students/:user_id/progress → progression individuelle (teacher only)
GET    /api/v1/assignments/mine                        → devoirs assignés à moi (vue élève)
```

> **Règle de confidentialité renforcée** : `GET /classes/:id/students/:user_id/progress` est réservé aux membres avec le rôle `owner` ou `admin`. Le contenu textuel des flashcards d'un élève n'est jamais exposé — uniquement les métriques.

---

### 10.2 Étapes de développement

#### Backend

- [x] **10.2.1** Ajouter les colonnes `type` et `is_class` au modèle `Group`. Générer la migration.
  `commit: feat(classes): extend Group model with class type`

- [x] **10.2.2** Créer `backend/app/models/assignment.py` avec `Assignment` et `AssignmentProgress`. Migration.
  `commit: feat(classes): add Assignment and AssignmentProgress models`

- [x] **10.2.3** Créer `backend/app/services/class_service.py`.
  Hérite/compose avec `GroupService`. Ajoute : vérification du rôle `teacher` pour les opérations d'assignation, calcul de progression agrégée par classe.
  `commit: feat(classes): add ClassService`

- [x] **10.2.4** Créer `backend/app/api/v1/classes.py`.
  `commit: feat(classes): add classes REST endpoints`

- [x] **10.2.5** Modifier `FocusService.get_today_items()` pour inclure les devoirs assignés avec deadline proche (≤ 3 jours).
  `commit: feat(classes): integrate assignments in Focus today items`

#### Frontend

- [x] **10.2.6** Créer `web/src/views/Classes/TeacherDashboard.vue` — vue prof : liste des classes, progression globale par classe, bouton créer un devoir.
  `commit: feat(classes): add TeacherDashboard view`

- [x] **10.2.7** Créer `web/src/views/Classes/StudentClassView.vue` — vue élève : liste des devoirs avec statut (à faire / en cours / terminé / en retard), lien vers le classeur.
  `commit: feat(classes): add StudentClassView`

- [x] **10.2.8** Créer `web/src/views/Classes/AssignmentDetail.vue` — vue prof : tableau de progression par élève (barres, scores, date de complétion).
  `commit: feat(classes): add AssignmentDetail view with student progress`

- [x] **10.2.9** Modifier `FocusWidget` et `FocusPage` pour afficher les devoirs avec deadline dans la file du jour.
  `commit: feat(classes): integrate assignments in Focus views`

---

### 10.3 Tests

```python
def test_only_teacher_can_create_assignment()
def test_student_cannot_see_other_student_flashcard_content()
def test_assignment_due_date_appears_in_focus_today()
def test_progress_aggregation_correct()
def test_class_type_group_creation()
def test_teacher_progress_view_forbidden_for_student()
```

---

## 11. Journal de développement

> L'agent met à jour cette section après chaque fonctionnalité complétée.

| Date | Fonctionnalité | Étapes complétées | Notes / Blocages |
|------|---------------|-------------------|-----------------|
| 2026-06-11 | Tags transversaux | 1.2.1 à 1.2.13 | Backend CRUD/liaisons/filtres livré et testé. Frontend livré pour store, badges, sélecteur, notes, decks, classeurs, diagrammes et PDFs avec filtre par tag sur toutes les listes. Tests exécutés avec succès. |
| 2026-06-11 | Espace Focus | 2.2.1 à 2.2.13 | Backend /focus/today, /focus/forecast et /focus/retention implémentés et testés. Vues frontend FocusPage, Forecast et Heatmap créées. Intégration du composable usePlatform. |
| 2026-06-11 | Planning des révisions | 3.2.1 à 3.2.13 | Backend /planning/calendar et /planning/advance implémentés et testés (SM-2, anticipation). Vue frontend PlanningPage avec sélection de deck et intégration de calendrier. |
| 2026-06-11 | Recherche globale full-text | 4.2.1 à 4.2.7 | Backend SearchDAO/SearchService (multi-dialecte PostgreSQL/SQLite) et endpoint de recherche implémentés. Composable useSearch et composant SearchModal créés avec raccourci Ctrl+K / Cmd+K et auto-sélection de deck/diagramme par ID. |
| 2026-06-11 | Minuteur Pomodoro | 5.2.1 à 5.2.5 | Composable usePomodoro et Pinia store pomodoro créés. Notification push natives (Capacitor) et web. Bips sonores auto-générés. Composant flottant PomodoroTimer avec panneau de paramètres. Logs de sessions. |
| 2026-06-11 | Import depuis Anki | 6.2.1 à 6.2.5 | Backend anki_parser (décompression zip, lecture collection.anki2 SQLite en mémoire), ImportService et endpoint /import/anki créés et testés avec succès (8/8 tests passés). Modal frontend AnkiImportModal et bouton intégrés dans Decks.vue. |
| 2026-06-11 | Génération de QCM | 7.2.1 à 7.2.8 | Modèles, DAO, Service, et endpoints d'API REST backend implémentés pour les QCM (avec rate-limiting de 10/heure par Gemini). Frontend : implémentation du service `quizService.ts`, de l'interface `NoteQuiz.vue` (génération IA, jeu de QCM interactif, scoring et export des mauvaises réponses vers les flashcards d'un deck), et bouton de lancement sur `NoteEdit.vue`. Tests unitaires (65/65 passés) et compilation de production Web OK. |

---

## Annexe — Checklist de régression globale

À exécuter avant tout merge sur `main` :

```bash
# Backend
cd backend
python -m pytest --cov=app --cov-report=term-missing
# Coverage minimale attendue : 80%

# Frontend
cd web
npm run test
npm run build
# Le build doit passer sans erreur TypeScript

# Intégration Docker
docker compose up --build -d
curl http://localhost:5000/api/v1/health
curl http://localhost:3000
docker compose down
```

Vérifications manuelles minimales :
- [ ] Authentification (register, login, logout, refresh)
- [ ] CRUD Notes (créer, éditer, supprimer, partager)
- [ ] CRUD Flashcards + session de révision SM-2
- [ ] Upload et lecture d'un PDF
- [ ] Dashboard s'affiche sans erreur console
