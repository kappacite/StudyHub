# AGENTS.md — StudyHub : Application d'étude tout-en-un

> Ce fichier définit les règles, conventions et responsabilités pour chaque agent IA
> intervenant sur le projet. Il est **impératif** de le lire intégralement avant toute
> contribution au code.

---

## Table des matières

1. [Vue d'ensemble du projet](#1-vue-densemble-du-projet)
2. [Choix technologiques](#2-choix-technologiques)
3. [Structure du dépôt](#3-structure-du-dépôt)
4. [Architecture en couches](#4-architecture-en-couches)
5. [Agent Backend (Flask)](#5-agent-backend-flask)
6. [Agent Frontend Web (Vue.js + TailwindCSS)](#6-agent-frontend-web-vuejs--tailwindcss)
7. [Agent Mobile (Capacitor)](#7-agent-mobile-capacitor)
8. [Agent Transverse — Système utilisateur & Auth](#8-agent-transverse--système-utilisateur--auth)
9. [Agent Dashboard & Suivi](#9-agent-dashboard--suivi)
10. [Conventions de code globales](#10-conventions-de-code-globales)
11. [Spécification REST API](#11-spécification-rest-api)
12. [Déploiement](#12-déploiement)
13. [Checklist avant PR](#13-checklist-avant-pr)

---

## 1. Vue d'ensemble du projet

**StudyHub** est une application web & mobile permettant aux étudiants de centraliser
tous leurs outils d'apprentissage :

| Module | Description |
|---|---|
| **Flashcards** | Cartes mémoire avec algorithme de répétition espacée (SM-2) |
| **Notes** | Éditeur de texte riche (Markdown + WYSIWYG) |
| **Diagrammes** | Éditeur de schémas (mind maps, flowcharts) |
| **PDF** | Visualisation, annotation et organisation de fichiers PDF |
| **Classeurs** | Arborescence de dossiers pour organiser tous les contenus |
| **Dashboard** | Suivi des sessions d'étude, statistiques, objectifs |

---

## 2. Choix technologiques

### Backend
- **Langage** : Python 3.12+
- **Framework** : Flask 3.x
- **ORM** : SQLAlchemy 2.x (pattern DAO)
- **Base de données** : PostgreSQL 16 (prod) / SQLite (dev)
- **Auth** : JWT via `flask-jwt-extended`
- **Migrations** : Alembic via `flask-migrate`
- **Validation** : Pydantic v2 (schémas de requête/réponse)
- **Tests** : Pytest + pytest-flask

### Frontend Web
- **Framework** : Vue.js 3 (Composition API + `<script setup>`)
- **Build** : Vite 5
- **Style** : TailwindCSS 3 + HeadlessUI
- **State** : Pinia
- **Routing** : Vue Router 4
- **HTTP** : Axios (instance centralisée avec intercepteurs)
- **Éditeur** : Tiptap 2 (notes), Mermaid.js (diagrammes)
- **PDF** : PDF.js
- **Tests** : Vitest + Vue Testing Library

### Mobile
- **Technologie retenue : Capacitor 6 (Ionic)**
  - *Justification* : Capacitor encapsule le build Vue.js produit par Vite sans
    réécriture. Un seul codebase `web/` génère l'application web ET la coque mobile
    iOS/Android. Accès natif caméra, stockage local, notifications push via plugins
    Capacitor officiels. Alternatives écartées : React Native (changement de stack),
    Flutter (Dart, pas de partage de code).
- **Cible** : iOS 16+ / Android 10+ (API 29+)
- **Plugins Capacitor** : `@capacitor/filesystem`, `@capacitor/local-notifications`,
  `@capacitor/camera`, `@capacitor/haptics`

### Décision d'architecture globale
```
[Mobile: Capacitor]
        ↓ (wraps)
[Web: Vue.js + Vite]  ←→  [API REST: Flask]  ←→  [PostgreSQL]
```

---

## 3. Structure du dépôt

```
studyhub/
├── AGENTS.md                  ← CE FICHIER
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
│
├── backend/                   ← Agent Backend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic/
│   ├── app/
│   │   ├── __init__.py        # Application factory (auto-migrations)
│   │   ├── config.py          # Config par environnement
│   │   ├── extensions.py      # SQLAlchemy, JWT, Migrate...
│   │   │
│   │   ├── dao/               # COUCHE ACCÈS DONNÉES
│   │   │   ├── base_dao.py
│   │   │   ├── user_dao.py
│   │   │   ├── deck_dao.py
│   │   │   ├── flashcard_dao.py
│   │   │   ├── note_dao.py
│   │   │   ├── diagram_dao.py
│   │   │   ├── pdf_dao.py
│   │   │   └── binder_dao.py
│   │   │
│   │   ├── models/            # Modèles SQLAlchemy (entités)
│   │   │   ├── user.py
│   │   │   ├── deck.py
│   │   │   ├── flashcard.py
│   │   │   ├── note.py
│   │   │   ├── diagram.py
│   │   │   ├── pdf_document.py
│   │   │   └── binder.py
│   │   │
│   │   ├── services/          # COUCHE LOGIQUE MÉTIER
│   │   │   ├── ai_service.py         # Intégration IA (Gemini - Blurting)
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── deck_service.py
│   │   │   ├── flashcard_service.py
│   │   │   ├── spaced_repetition.py  # Algo SM-2
│   │   │   ├── note_service.py
│   │   │   ├── diagram_service.py
│   │   │   ├── pdf_service.py
│   │   │   ├── binder_service.py
│   │   │   ├── community_service.py  # Gestion packages/marketplace
│   │   │   └── stats_service.py
│   │   │
│   │   ├── schemas/           # Pydantic — validation I/O
│   │   │   ├── user_schema.py
│   │   │   ├── auth_schema.py
│   │   │   ├── flashcard_schema.py
│   │   │   ├── note_schema.py
│   │   │   └── ...
│   │   │
│   │   ├── middlewares/       # COUCHE MIDDLEWARES
│   │   │   ├── auth_middleware.py    # Vérification JWT
│   │   │   ├── rate_limiter.py      # flask-limiter
│   │   │   ├── error_handler.py     # Handlers globaux
│   │   │   └── request_logger.py    # Logging structuré
│   │   │
│   │   ├── api/               # COUCHE PRÉSENTATION (routes)
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── decks.py
│   │   │   │   ├── flashcards.py
│   │   │   │   ├── notes.py
│   │   │   │   ├── diagrams.py
│   │   │   │   ├── pdfs.py
│   │   │   │   ├── binders.py
│   │   │   │   ├── blurting.py        # Analyse de feuilles blanches par IA
│   │   │   │   ├── packages.py        # Marketplace communautaire
│   │   │   │   └── stats.py
│   │   │   └── __init__.py
│   │   │
│   │   └── utils/
│   │       ├── pagination.py
│   │       └── file_storage.py
│   │
│   └── tests/
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_flashcards.py
│       └── ...
│
├── web/                       ← Agent Frontend Web + source Mobile
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── capacitor.config.ts    # Config Capacitor (pointé depuis mobile/)
│   ├── public/
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── router/
│   │   │   └── index.ts
│   │   ├── stores/            # Pinia
│   │   │   ├── auth.ts
│   │   │   ├── decks.ts
│   │   │   ├── notes.ts
│   │   │   └── ui.ts
│   │   ├── services/          # Appels API (Axios)
│   │   │   ├── api.ts         # Instance Axios + intercepteurs
│   │   │   ├── authService.ts
│   │   │   ├── deckService.ts
│   │   │   └── ...
│   │   ├── composables/       # Logique réutilisable (hooks Vue)
│   │   │   ├── useFlashcards.ts
│   │   │   ├── useAuth.ts
│   │   │   └── usePlatform.ts # Détecte web vs mobile Capacitor
│   │   ├── components/
│   │   │   ├── ui/            # Design system (boutons, modales…)
│   │   │   ├── flashcards/
│   │   │   ├── notes/
│   │   │   ├── diagrams/
│   │   │   ├── pdf/
│   │   │   └── dashboard/
│   │   ├── views/
│   │   │   ├── Auth/
│   │   │   ├── Dashboard/
│   │   │   ├── Decks/
│   │   │   ├── Notes/
│   │   │   ├── Diagrams/
│   │   │   ├── PDFs/
│   │   │   └── Binders/
│   │   └── assets/
│   └── tests/
│
└── mobile/                    ← Agent Mobile (Capacitor wrapper)
    ├── android/
    ├── ios/
    ├── package.json           # Dépendances Capacitor uniquement
    └── README.md              # Instructions build natif
```

---

## 4. Architecture en couches

### Principes SOLID appliqués

| Principe | Application concrète |
|---|---|
| **S** — Single Responsibility | Chaque DAO gère une seule entité. Chaque Service contient une seule logique métier. |
| **O** — Open/Closed | `BaseDAO` est extensible sans modification. Les services sont extensibles via héritage ou composition. |
| **L** — Liskov Substitution | Toute implémentation concrète de DAO peut remplacer `BaseDAO` sans briser le contrat. |
| **I** — Interface Segregation | Les schémas Pydantic sont séparés (requête vs réponse). Pas de schéma "fourre-tout". |
| **D** — Dependency Inversion | Les services reçoivent leur DAO en injection (constructeur ou factory). Pas d'import direct. |

### Flux de données (Backend)

```
HTTP Request
    ↓
[Middleware] auth_middleware → rate_limiter → request_logger
    ↓
[API Layer]  Route Flask — valide le body avec Pydantic Schema
    ↓
[Service]    Logique métier, règles, orchestration
    ↓
[DAO]        Requêtes SQLAlchemy — AUCUNE logique métier ici
    ↓
[Model]      Entité SQLAlchemy (table)
    ↓
PostgreSQL
```

### Règle stricte de séparation des couches

- **DAO** → ne connaît que les modèles SQLAlchemy et la session DB.
  N'importe **jamais** de service.
- **Service** → ne connaît que les DAO et les schémas Pydantic.
  N'effectue **jamais** de requête SQL directe.
- **API (routes)** → ne contient **aucune** logique métier. Délègue au service,
  retourne un `jsonify` + code HTTP approprié.
- **Middleware** → transversal, ne contient pas de logique applicative.

---

## 5. Agent Backend (Flask)

### Responsabilités
- Implémenter et maintenir tous les endpoints REST sous `/api/v1/`
- Garantir la couverture de tests ≥ 80 % (Pytest)
- Gérer les migrations Alembic
- Respecter strictement la séparation DAO / Service / Route

### Pattern BaseDAO obligatoire

```python
# app/dao/base_dao.py
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session

T = TypeVar("T")

class BaseDAO(Generic[T]):
    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, entity_id: int) -> Optional[T]:
        return self.db.get(self.model, entity_id)

    def get_all(self, user_id: int, limit: int = 20, offset: int = 0) -> List[T]:
        return (
            self.db.query(self.model)
            .filter_by(user_id=user_id)
            .limit(limit)
            .offset(offset)
            .all()
        )

    def create(self, entity: T) -> T:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, entity: T) -> T:
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: T) -> None:
        self.db.delete(entity)
        self.db.commit()
```

### Pattern Service obligatoire

```python
# app/services/deck_service.py
class DeckService:
    def __init__(self, deck_dao: DeckDAO, flashcard_dao: FlashcardDAO):
        self._deck_dao = deck_dao        # Injection de dépendance
        self._flashcard_dao = flashcard_dao

    def create_deck(self, user_id: int, data: DeckCreateSchema) -> DeckResponseSchema:
        # Logique métier ici (vérifications, transformations)
        deck = Deck(user_id=user_id, **data.model_dump())
        created = self._deck_dao.create(deck)
        return DeckResponseSchema.model_validate(created)
```

### Gestion des erreurs

Tout endpoint doit retourner des erreurs dans ce format JSON :

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Le deck demandé n'existe pas.",
    "details": {}
  }
}
```

L'agent backend doit enregistrer un handler global dans `error_handler.py` pour :
- `404` → `ResourceNotFoundError`
- `400` → `ValidationError` (Pydantic)
- `401` → `UnauthorizedError`
- `403` → `ForbiddenError`
- `409` → `ConflictError`
- `500` → erreur générique sans stack trace en production

### Variables d'environnement attendues

```ini
FLASK_ENV=development|production
DATABASE_URL=postgresql://user:pass@db:5432/studyhub
SECRET_KEY=<clé aléatoire 64 chars>
JWT_SECRET_KEY=<clé aléatoire 64 chars>
JWT_ACCESS_TOKEN_EXPIRES=3600        # secondes
JWT_REFRESH_TOKEN_EXPIRES=2592000    # 30 jours
UPLOAD_FOLDER=/app/uploads
MAX_CONTENT_LENGTH=52428800          # 50 MB
```

---

## 6. Agent Frontend Web (Vue.js + TailwindCSS)

### Responsabilités
- Implémenter toutes les vues et composants Vue.js 3
- Utiliser exclusivement la Composition API avec `<script setup lang="ts">`
- Gérer l'état global via Pinia (pas de Vuex)
- Garantir le responsive design (mobile-first avec Tailwind)

### Instance Axios centralisée (obligatoire)

```typescript
// src/services/api.ts
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL + '/api/v1',
  timeout: 10000,
})

// Intercepteur requête : injecte le JWT
api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) config.headers.Authorization = `Bearer ${auth.token}`
  return config
})

// Intercepteur réponse : gère le refresh token et les 401
api.interceptors.response.use(
  (res) => res,
  async (err) => {
    if (err.response?.status === 401) {
      // Tenter le refresh, sinon rediriger vers /login
      await useAuthStore().refresh()
      if (!useAuthStore().token) router.push('/login')
    }
    return Promise.reject(err)
  }
)

export default api
```

### Composable `usePlatform` (détection web vs mobile)

```typescript
// src/composables/usePlatform.ts
import { Capacitor } from '@capacitor/core'

export function usePlatform() {
  const isNative = Capacitor.isNativePlatform()
  const platform = Capacitor.getPlatform() // 'web' | 'ios' | 'android'
  return { isNative, platform }
}
```

Utiliser ce composable pour conditionner les comportements natifs
(ex : accès fichiers via `@capacitor/filesystem` sur mobile, `<input type="file">`
sur web).

### Conventions composants

- Fichiers : `PascalCase.vue`
- Composables : `useCamelCase.ts`
- Stores : `camelCase.ts`
- Services : `camelCaseService.ts`
- Un composant = une seule responsabilité visuelle
- Les composants dans `components/ui/` ne doivent **jamais** appeler l'API directement

### Design System Tailwind

Définir dans `tailwind.config.ts` les tokens de design :

```typescript
theme: {
  extend: {
    colors: {
      primary:  { DEFAULT: '#4F46E5', dark: '#3730A3' },
      surface:  { DEFAULT: '#FFFFFF', dark: '#1E1E2E' },
      muted:    '#6B7280',
      success:  '#22C55E',
      warning:  '#F59E0B',
      danger:   '#EF4444',
    },
    fontFamily: {
      sans: ['Inter Variable', 'sans-serif'],
      mono: ['JetBrains Mono', 'monospace'],
    },
  },
}
```

Supporter obligatoirement le mode sombre (`dark:` prefix Tailwind).

---

## 7. Agent Mobile (Capacitor)

### Responsabilités
- Maintenir la configuration Capacitor dans `web/capacitor.config.ts`
- Gérer les plugins natifs dans `web/src/composables/`
- Synchroniser le build web vers les projets `mobile/android` et `mobile/ios`
- Ne PAS modifier le code Vue.js pour le mobile : utiliser `usePlatform()`

### Configuration Capacitor

```typescript
// web/capacitor.config.ts
import { CapacitorConfig } from '@capacitor/cli'

const config: CapacitorConfig = {
  appId: 'com.studyhub.app',
  appName: 'StudyHub',
  webDir: 'dist',
  server: {
    androidScheme: 'https',
  },
  plugins: {
    LocalNotifications: {
      smallIcon: 'ic_stat_icon',
      iconColor: '#4F46E5',
    },
  },
}

export default config
```

### Commandes de build mobile

```bash
# 1. Build du frontend Vue.js
cd web && npm run build

# 2. Synchronisation vers les projets natifs
npx cap sync

# 3. Ouvrir dans Android Studio
npx cap open android

# 4. Ouvrir dans Xcode
npx cap open ios
```

### Plugins natifs à utiliser

| Fonctionnalité | Plugin Capacitor |
|---|---|
| Import PDF / fichiers | `@capacitor/filesystem` |
| Notifications révisions | `@capacitor/local-notifications` |
| Scan de document | `@capacitor/camera` |
| Retour haptique (flashcards) | `@capacitor/haptics` |
| Stockage offline | `@capacitor/preferences` |

### Offline-first (mobile)

Implémenter dans `usePlatform.ts` un mécanisme de cache local via
`@capacitor/preferences` pour les flashcards et notes, synchronisé avec l'API
au retour de la connexion (stratégie "cache then network").

---

## 8. Agent Transverse — Système utilisateur & Auth

### Modèle de données & Partage

```python
# app/models/user.py
class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True)
    email         = Column(String(255), unique=True, nullable=False, index=True)
    username      = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime, server_default=func.now())
    updated_at    = Column(DateTime, onupdate=func.now())

    # Relations
    binders    = relationship("Binder", back_populates="user", cascade="all, delete")
    decks      = relationship("Deck",   back_populates="user", cascade="all, delete")
    notes      = relationship("Note",   back_populates="user", cascade="all, delete")

# app/models/binder.py
class Binder(Base):
    __tablename__ = "binders"

    id                 = Column(Integer, primary_key=True)
    name               = Column(String(100), nullable=False)
    user_id            = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id          = Column(Integer, ForeignKey("binders.id"), nullable=True)
    is_public          = Column(Boolean, default=False, nullable=False)
    description        = Column(Text, nullable=True)
    tags               = Column(JSON, nullable=True)
    fork_count         = Column(Integer, default=0, nullable=False)
    original_author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at         = Column(DateTime, server_default=func.now())
    updated_at         = Column(DateTime, onupdate=func.now())

# app/models/note.py
class Note(Base):
    __tablename__ = "notes"

    id          = Column(Integer, primary_key=True)
    title       = Column(String(200), nullable=False)
    content     = Column(Text, default="", nullable=False)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    binder_id   = Column(Integer, ForeignKey("binders.id"), nullable=True)
    is_public   = Column(Boolean, default=False, nullable=False)
    share_token = Column(String(64), unique=True, nullable=True, index=True)
    created_at  = Column(DateTime, server_default=func.now())
    updated_at  = Column(DateTime, onupdate=func.now())
```

### Endpoints Auth

```
POST   /api/v1/auth/register      → 201 Created
POST   /api/v1/auth/login         → 200 OK  {access_token, refresh_token, user}
POST   /api/v1/auth/refresh       → 200 OK  {access_token}
POST   /api/v1/auth/logout        → 204 No Content
DELETE /api/v1/auth/account       → 204 No Content (RGPD)
```

### Middleware JWT (obligatoire sur toutes les routes protégées)

```python
# app/middlewares/auth_middleware.py
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def jwt_required_middleware(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        return f(*args, **kwargs)
    return decorated
```

### Isolation des données utilisateur

**Règle absolue** : tout DAO qui liste des ressources DOIT filtrer par `user_id`.
Aucune ressource d'un utilisateur ne doit être accessible par un autre.
Vérifier systématiquement l'appartenance avant tout update/delete.

```python
def get_deck_or_404(self, deck_id: int, user_id: int) -> Deck:
    deck = self._deck_dao.get_by_id(deck_id)
    if not deck:
        raise ResourceNotFoundError("Deck introuvable")
    if deck.user_id != user_id:
        raise ForbiddenError("Accès interdit")
    return deck
```

---

## 9. Agent Dashboard & Suivi

### Métriques à collecter

Créer une table `study_sessions` :

```
id, user_id, module (flashcard|note|diagram), duration_seconds,
cards_reviewed, cards_correct, created_at
```

### Endpoints Stats

```
GET /api/v1/stats/overview         → Résumé global (streak, total temps, score)
GET /api/v1/stats/sessions         → Liste sessions (filtres: ?from=&to=&module=)
GET /api/v1/stats/heatmap          → Données calendrier activité (365 jours)
GET /api/v1/stats/decks/:id        → Stats par deck (taux de rétention, prochain réveil)
```

### Composants Dashboard Vue.js

- `StudyHeatmap.vue` — calendrier GitHub-style (365 jours)
- `RetentionChart.vue` — courbe rétention par deck (recharts ou Chart.js)
- `StreakCounter.vue` — jours consécutifs d'étude
- `GoalTracker.vue` — objectifs hebdomadaires configurables
- `ModuleStats.vue` — répartition du temps par module

---

## 10. Conventions de code globales

### Git — Commits (Conventional Commits)

```
feat(flashcards): ajout algorithme SM-2
fix(auth): correction expiration refresh token
refactor(dao): extraction BaseDAO générique
docs(api): documentation endpoint /decks
test(notes): ajout tests service NoteService
chore(docker): optimisation image multi-stage
```

### Branches

```
main          → production stable
develop       → intégration continue
feature/*     → nouvelles fonctionnalités
fix/*         → corrections de bugs
release/*     → préparation de release
```

### Nommage

| Contexte | Convention |
|---|---|
| Python (backend) | `snake_case` pour variables/fonctions, `PascalCase` pour classes |
| TypeScript (web) | `camelCase` pour variables/fonctions, `PascalCase` pour classes/composants |
| Endpoints API | `kebab-case` (`/study-sessions`) |
| Variables env | `SCREAMING_SNAKE_CASE` |
| Fichiers Vue | `PascalCase.vue` |
| Fichiers Python | `snake_case.py` |

### Interdictions strictes

- ❌ Logique métier dans les routes Flask
- ❌ Requêtes SQL directes dans les services
- ❌ Appels API dans les composants UI (`components/ui/`)
- ❌ `any` en TypeScript (utiliser des types stricts)
- ❌ `console.log` en production (utiliser un logger)
- ❌ Secrets en dur dans le code (utiliser `.env`)
- ❌ Endpoints sans authentification JWT (sauf auth + health)

---

## 11. Spécification REST API

### Préfixe global

Tous les endpoints sont préfixés par `/api/v1/`.

### Codes HTTP à respecter

| Situation | Code |
|---|---|
| Lecture réussie | `200 OK` |
| Création réussie | `201 Created` |
| Succès sans contenu (delete, logout) | `204 No Content` |
| Requête invalide (validation) | `400 Bad Request` |
| Non authentifié | `401 Unauthorized` |
| Accès interdit (mauvais user) | `403 Forbidden` |
| Ressource introuvable | `404 Not Found` |
| Conflit (email déjà pris) | `409 Conflict` |
| Erreur serveur | `500 Internal Server Error` |

### Pagination (query parameters standards)

```
GET /api/v1/decks?page=1&per_page=20&sort=created_at&order=desc&search=chimie
```

Réponse paginée obligatoire :

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 142,
    "pages": 8
  }
}
```

### Endpoints principaux

```
# Authentification
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout

# Utilisateurs
GET    /api/v1/users/me
PUT    /api/v1/users/me
DELETE /api/v1/users/me

# Classeurs
GET    /api/v1/binders                    ?page&per_page&parent_id
POST   /api/v1/binders
GET    /api/v1/binders/:id
PUT    /api/v1/binders/:id
DELETE /api/v1/binders/:id
GET    /api/v1/binders/public/:id         → Accès public à un classeur
PATCH  /api/v1/binders/:id/visibility     → Toggle visibilité publique (is_public: bool)

# Decks de flashcards
GET    /api/v1/decks                      ?page&per_page&binder_id&search
POST   /api/v1/decks
GET    /api/v1/decks/:id
PUT    /api/v1/decks/:id
DELETE /api/v1/decks/:id
GET    /api/v1/decks/:id/study            → cartes à réviser aujourd'hui (SM-2)
POST   /api/v1/decks/:id/study/answer     → enregistre réponse, recalcule intervalle

# Flashcards
GET    /api/v1/decks/:id/cards            ?page&per_page
POST   /api/v1/decks/:id/cards
GET    /api/v1/decks/:id/cards/:card_id
PUT    /api/v1/decks/:id/cards/:card_id
DELETE /api/v1/decks/:id/cards/:card_id

# Notes
GET    /api/v1/notes                      ?page&per_page&binder_id&search
POST   /api/v1/notes
GET    /api/v1/notes/:id
PUT    /api/v1/notes/:id
DELETE /api/v1/notes/:id
GET    /api/v1/notes/public/:token        → Accès public à une note par share_token
PATCH  /api/v1/notes/:id/visibility       → Toggle visibilité publique (is_public: bool)

# Espace Communautaire (Packages)
GET    /api/v1/packages                   ?search&page&per_page (public)
GET    /api/v1/packages/:binder_id        → Détails du package public (public)
POST   /api/v1/packages/:binder_id/clone  → Cloner le package dans son compte (sécurisé)

# Révision Blurting (Feuille Blanche IA)
POST   /api/v1/blurting/analyze           → Analyse IA (Gemini) de la restitution (sécurisé)
POST   /api/v1/blurting/create-flashcards → Crée des cartes générées par l'analyse (sécurisé)

# Diagrammes
GET    /api/v1/diagrams                   ?page&per_page&binder_id
POST   /api/v1/diagrams
GET    /api/v1/diagrams/:id
PUT    /api/v1/diagrams/:id
DELETE /api/v1/diagrams/:id

# PDFs
GET    /api/v1/pdfs                       ?page&per_page&binder_id
POST   /api/v1/pdfs                       (multipart/form-data)
GET    /api/v1/pdfs/:id
GET    /api/v1/pdfs/:id/file              → stream du fichier PDF
DELETE /api/v1/pdfs/:id

# Stats / Dashboard
GET    /api/v1/stats/overview
GET    /api/v1/stats/sessions             ?from=ISO8601&to=ISO8601&module=
GET    /api/v1/stats/heatmap
GET    /api/v1/stats/decks/:id

# Santé
GET    /api/v1/health                     → {"status": "ok", "version": "1.0.0"}
```

---

## 12. Déploiement

### Fichier `docker-compose.yml` (développement)

```yaml
version: '3.9'

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: studyhub
      POSTGRES_USER: studyhub
      POSTGRES_PASSWORD: studyhub_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U studyhub"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      target: development
    environment:
      FLASK_ENV: development
      DATABASE_URL: postgresql://studyhub:studyhub_dev@db:5432/studyhub
      JWT_SECRET_KEY: dev_jwt_secret_change_in_prod
      SECRET_KEY: dev_secret_change_in_prod
      UPLOAD_FOLDER: /app/uploads
    ports:
      - "5000:5000"
    volumes:
      - ./backend:/app
      - uploads_data:/app/uploads
    depends_on:
      db:
        condition: service_healthy
    command: flask run --host=0.0.0.0 --port=5000 --debug

  web:
    build:
      context: ./web
      target: development
    ports:
      - "3000:3000"
    volumes:
      - ./web:/app
      - /app/node_modules
    environment:
      VITE_API_BASE_URL: http://localhost:5000
    command: npm run dev -- --host 0.0.0.0 --port 3000

volumes:
  postgres_data:
  uploads_data:
```

### Fichier `docker-compose.prod.yml` (production)

```yaml
version: '3.9'

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      target: production
    environment:
      FLASK_ENV: production
      DATABASE_URL: ${DATABASE_URL}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      SECRET_KEY: ${SECRET_KEY}
      UPLOAD_FOLDER: /app/uploads
    volumes:
      - uploads_data:/app/uploads
    depends_on:
      - db
    restart: unless-stopped

  web:
    build:
      context: ./web
      target: production
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - web
    restart: unless-stopped

volumes:
  postgres_data:
  uploads_data:
```

### Dockerfile Backend (multi-stage)

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS development
RUN pip install flask-debugtoolbar pytest pytest-flask
COPY . .

FROM base AS production
COPY . .
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", \
     "--timeout", "120", "app:create_app()"]
```

### Dockerfile Frontend Web (multi-stage)

```dockerfile
# web/Dockerfile
FROM node:20-alpine AS base
WORKDIR /app
COPY package*.json .
RUN npm ci

FROM base AS development
COPY . .

FROM base AS builder
COPY . .
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

FROM nginx:alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.spa.conf /etc/nginx/conf.d/default.conf
```

### Script de lancement rapide (`scripts/dev.sh`)

```bash
#!/bin/bash
# scripts/dev.sh — Lancement de l'environnement de développement

set -e

echo "🚀 Démarrage de StudyHub en développement..."

# Vérification des prérequis
command -v docker >/dev/null 2>&1 || { echo "Docker requis"; exit 1; }
command -v docker compose >/dev/null 2>&1 || { echo "Docker Compose requis"; exit 1; }

# Copie du .env si absent
[ ! -f .env ] && cp .env.example .env && echo "⚠️  .env créé depuis .env.example — vérifiez les valeurs"

# Build et démarrage
docker compose up --build -d

# Attente DB prête
echo "⏳ Attente de la base de données..."
docker compose exec backend flask db upgrade

echo "✅ StudyHub disponible :"
echo "   → API    : http://localhost:5000/api/v1/health"
echo "   → Web    : http://localhost:3000"
echo "   → DB     : localhost:5432"
```

### Script migration production (`scripts/deploy.sh`)

```bash
#!/bin/bash
# scripts/deploy.sh — Déploiement production

set -e

echo "📦 Déploiement StudyHub production..."

# Pull dernières images
docker compose -f docker-compose.prod.yml pull

# Migration DB avant le démarrage
docker compose -f docker-compose.prod.yml run --rm backend flask db upgrade

# Redémarrage sans downtime
docker compose -f docker-compose.prod.yml up -d --remove-orphans

echo "✅ Déploiement terminé"
docker compose -f docker-compose.prod.yml ps
```

### Commandes utiles

```bash
# Développement
./scripts/dev.sh                              # Démarrage complet
docker compose logs -f backend               # Logs API
docker compose exec backend pytest           # Tests backend
docker compose exec backend flask db migrate # Nouvelle migration

# Mobile (depuis web/)
cd web && npm run build && npx cap sync      # Build + sync
npx cap run android                          # Lancer sur émulateur Android
npx cap run ios                              # Lancer sur simulateur iOS

# Production
./scripts/deploy.sh                          # Déployer
docker compose -f docker-compose.prod.yml logs -f   # Logs prod
```

---

## 13. Checklist avant PR

### Pratiques de développement (Obligatoire)

- [ ] Un commit Git a été effectué immédiatement après chaque modification/correction.
- [ ] La documentation technique dans le dossier docs/ a été complétée ou mise à jour.
- [ ] Le journal de développement a été enrichi avec les changements du jour.

### Backend
- [ ] Les routes ne contiennent aucune logique métier
- [ ] Chaque endpoint filtre les données par `user_id`
- [ ] Codes HTTP corrects (201 création, 204 suppression…)
- [ ] Schémas Pydantic définis pour requête et réponse
- [ ] Tests ajoutés ou mis à jour (coverage ≥ 80%)
- [ ] Migration Alembic créée si modèle modifié
- [ ] Pas de secret en dur

### Frontend Web
- [ ] Composition API avec `<script setup lang="ts">` uniquement
- [ ] Appels API uniquement dans les stores Pinia ou services
- [ ] Responsive vérifié (mobile 375px + desktop 1440px)
- [ ] Mode sombre supporté
- [ ] Gestion des états loading / error / empty dans chaque vue

### Mobile
- [ ] `usePlatform()` utilisé pour les comportements conditionnels
- [ ] `npx cap sync` exécuté après le build
- [ ] Testé sur émulateur Android ET simulateur iOS

### Global
- [ ] Commit message conforme (Conventional Commits)
- [ ] Pas de `console.log` / `print` de debug
- [ ] `.env.example` mis à jour si nouvelle variable

---

*Document maintenu par l'équipe StudyHub. Toute modification architecturale majeure
doit être discutée et reflétée ici avant implémentation.*
