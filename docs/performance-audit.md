# Audit de performance de l'API — StudyHub

> Statut : **bilan + plan de remédiation**. Aucune optimisation n'est encore
> implémentée. Point de départ : « les decks mettent ~1s à charger ».

## Méthode
Lecture du chemin `route → service → DAO → modèle → schéma` à partir du cas concret
(decks lents), puis recherche des **mêmes patterns** sur tout le backend :
sur-récupération ORM, index, agrégations en Python, cache, concurrence, observabilité.

---

## Bilan — constats par thème

### 🔴 A. Sur-récupération ORM (N+1 / over-fetch) — cause directe des decks lents

| # | Constat | Emplacement |
|---|---|---|
| **A1** | `Deck.card_count = len(self.cards)` + le DAO fait `selectinload(self.model.cards)`. Lister 20 decks **charge en ORM toutes les cartes de tous les decks de la page** juste pour un `len()`. Un deck à 2 000 cartes → 2 000 objets instanciés pour afficher « 2000 ». **C'est le ~1s.** | `models/deck.py:32`, `dao/deck_dao.py:57-62` |
| **A2** | `focus_service` : `decks = ...all()` puis **boucle** avec une requête `due_cards` **par deck** (N+1), puis filtrage Python par parsing de `original_text` (`{{vf::}}`, `{{qcm::}}`…). | `services/focus_service.py:23,36,177` |
| **A3** | `class_service` (progression d'un classeur) : descente récursive de l'arbre des binders avec, par binder, une requête decks puis **par deck** une requête cartes (N+1 récursif). | `services/class_service.py:470-475` |
| **A4** | **Frontend** : les stores demandent `per_page=1000` (notes, binders, tags, diagrammes). `NoteEdit` charge **4 listes complètes** au montage. | `web/src/stores/*`, `views/Notes/NoteEdit.vue:1190` |

### 🔴 B. Index manquants — dégradation qui empire avec la croissance des données
Seuls **3 index applicatifs** existent (`users.email`, `notes.share_token`,
`flashcards.placeholder_hash`). **PostgreSQL n'indexe pas les FK automatiquement.**
Manquent notamment :
- `flashcards.deck_id` (→ `selectinload(cards)` et toute requête de cartes = *seq scan*)
- `flashcards.next_review` (→ requêtes « cartes dues » SM-2)
- `decks.user_id`, `decks.binder_id`, `notes.user_id`, `notes.binder_id`,
  `binders.user_id`, `binders.parent_id`, `study_sessions.user_id`
- tables d'association `deck_tags` / `note_tags`

Chaque `filter_by(user_id=…)` (sur **tous** les endpoints de liste) et chaque `IN (...)`
de `selectinload` scanne la table. Masqué aujourd'hui par le faible volume.

### 🟠 C. Agrégations en Python au lieu de SQL
- `card_count` via `len()` (cf. A1) → devrait être `COUNT()` / sous-requête.
- `focus_service` / `stats_service` : chargement de **toutes** les sessions/cartes en
  mémoire pour compter/filtrer (`focus_service.py:177` charge toutes les flashcards).
- `count_decks` est une 2ᵉ requête séparée (acceptable ; *window function* possible).

### 🟠 D. Cache sous-exploité
- `@cache_route` n'est posé **que** sur `stats`. Listes coûteuses (decks/notes/binders) non cachées.
- `SmartRedis` retombe sur un **dict en mémoire par processus** si Redis est absent →
  avec 4 workers gunicorn, cache **non partagé**. À vérifier : Redis tourne-t-il en prod ?

### 🟠 E. Concurrence serveur (I/O)
- gunicorn en `--worker-class gevent`, mais **psycopg2 est bloquant** et non patché
  (psycogreen) → chaque requête DB **bloque tout le worker**. Sous charge, sérialisation.
- Pool SQLAlchemy par défaut (`pool_size=5`), seul `pool_pre_ping` réglé.

### 🟡 F. Observabilité — prérequis manquant
Aucune instrumentation : pas de timing par requête, pas de log « requête lente », pas de
compteur SQL. On audite à l'aveugle ; impossible de prioriser/prouver un gain.

---

## Synthèse : « decks = 1s »
**A1 (over-fetch via `card_count`) + B (pas d'index sur `flashcards.deck_id`).** On charge
trop de cartes, et via un scan. Deux premiers chantiers à fort ROI.

---

## Plan de remédiation

> Transverse : `main` protégée → chaque thématique = **une branche + PR**, **commit à
> chaque étape**, les **6 checks CI** restent verts (dont `Backend · tests (PostgreSQL)`,
> idéal pour valider index/EXPLAIN sur le vrai moteur).

### Thématique 1 — Observabilité & mesure (prérequis)
- **1.1** Middleware de timing : log `méthode chemin status durée_ms` + seuil « lent ». → *commit*
- **1.2** Compteur de requêtes SQL par requête HTTP (event `before_cursor_execute`) pour détecter les N+1 (dev/test). → *commit*
- **1.3** Script de bench reproductible : seed paramétrable (ex. 50 decks × 2 000 cartes) + mesure de latence. → *commit*

### Thématique 2 — Index base de données (ROI le plus élevé)
- **2.1** Migration Alembic : index FK/filtrage (`flashcards.deck_id`, `decks.user_id`, `decks.binder_id`, `notes.user_id`, `notes.binder_id`, `binders.user_id`, `binders.parent_id`, `study_sessions.user_id`). → *commit*
- **2.2** Index composites : `flashcards(deck_id, next_review)`, `study_sessions(user_id, created_at)`, tables `*_tags`. → *commit*
- **2.3** Validation `EXPLAIN (ANALYZE)` avant/après (job Postgres) + bench (1.3). → *commit*

### Thématique 3 — Supprimer l'over-fetch sur les listes (decks d'abord)
- **3.1** `card_count` via `COUNT()` SQL (sous-requête / `GROUP BY`), **retirer `selectinload(cards)`** de la liste. → *commit*
- **3.2** Étendre aux autres listes (vérifier `notes`, `binders`, `pdfs`). → *commit*
- **3.3** Test « budget de requêtes » : la liste de N decks tient en un nombre **borné et constant** de requêtes (compteur 1.2). → *commit*

### Thématique 4 — Éliminer les N+1 dans `focus` et `classes`
- **4.1** `focus_service` : une **requête agrégée** (`GROUP BY deck_id`, `COUNT` des dues) au lieu de la boucle. → *commit*
- **4.2** Filtrage `original_text` : le pousser en SQL ou précalculer un flag/type de carte en colonne. → *commit*
- **4.3** `class_service` : remplacer la récursion N+1 par une **CTE récursive** / agrégat. → *commit*

### Thématique 5 — Cache
- **5.1** Garantir **Redis partagé** entre les 4 workers en prod (sinon cache par-process inutile). → *commit*
- **5.2** Étendre `@cache_route` aux listes coûteuses **avec invalidation** sur mutation. → *commit*

### Thématique 6 — Concurrence serveur
- **6.1** I/O DB coopératives sous gevent : `psycogreen` **ou** workers `sync` + threads. → *commit*
- **6.2** Tuning pool SQLAlchemy (`pool_size`, `max_overflow`, `pool_recycle`). → *commit*

### Thématique 7 — Frontend (réduire la charge demandée)
- **7.1** Supprimer les `per_page=1000` : paginer / charger à la demande. → *commit*
- **7.2** `NoteEdit` : ne plus charger 4 listes complètes au montage. → *commit*

---

## Ordonnancement recommandé (par ROI)
**1 (mesurer) → 2 (index) → 3 (over-fetch decks) → 4 (N+1) → 6 (concurrence) → 5 (cache) → 7 (frontend).**
Les thématiques 2 et 3 devraient régler le « decks 1s » ; la 1 conditionne tout (elle
permet de **prouver** chaque gain).
