# Stack Technologique — StudyHub

> Document de référence généré en mode cartographie (GSD).
> Inventaire exhaustif et sourcé (`fichier:ligne`) de l'ensemble des technologies, dépendances, environnements et configurations du projet StudyHub.

---

## 1. Vue d'ensemble & Architecture Polyglotte

StudyHub repose sur une architecture distribuée et multi-plateforme où un code frontend unique (`web/`) alimente l'application Web, l'application Mobile (via Capacitor) et l'application Bureau (via Electron), s'interfaçant avec un backend REST Flask conteneurisé, orchestré par Docker Compose et soutenu par PostgreSQL, Redis et Celery.

```
[Desktop: Electron 33] ──┐
                         ├─ wraps ──> [Frontend: Vue 3.5 + Vite 8]
[Mobile: Capacitor 8]   ──┘                    │
                                                ▼ (HTTP REST / Axios, JWT)
[Worker: Celery 5.4] <─── [Broker / Cache: Redis 7] <─── [Backend: Flask 3.0 + Gunicorn]
       │                                                              │
       ▼ (Gemini REST API)                                            ▼ (SQLAlchemy 2.0)
[Google Gemini AI]                                              [PostgreSQL 16 / SQLite]
```

---

## 2. Backend

### 2.1 Langage et Runtime
- **Python** : `3.12+` (image de production : `python:3.12-slim` sous Debian, [`backend/Dockerfile:1`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/Dockerfile#L1))
- **Serveur WSGI (Production)** : `gunicorn==22.0.0` avec workers `gthread` (4 workers × 4 threads, timeout 120s, [`backend/Dockerfile:22`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/Dockerfile#L22))
  - *Choix technique* : Workers `gthread` privilégiés par rapport à `gevent` car `psycopg2` libère le GIL lors des entrées/sorties réseau base de données, éliminant les blocages sans recourir au monkey-patching complexe ([`backend/Dockerfile:20-21`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/Dockerfile#L20-L21)).
- **Serveur de développement** : Flask CLI intégré / `wsgi:app` ([`backend/wsgi.py:1-16`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/wsgi.py#L1-L16), [`start.sh:94-100`](file:///C:/Users/denoe/Documents/Dev/StudyHub/start.sh#L94-L100))

### 2.2 Framework & Écosystème Flask
- **Flask** : `3.0.3` ([`backend/requirements.txt:1`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/requirements.txt#L1))
- **Werkzeug** : `3.0.3` ([`backend/requirements.txt:8`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/requirements.txt#L8))
- **Proxy Fix** : `werkzeug.middleware.proxy_fix.ProxyFix` configuré pour Nginx / Cloudflare (`x_for=1, x_proto=1, x_host=1, x_prefix=1`, [`backend/app/__init__.py:37-38`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/app/__init__.py#L37-L38))

### 2.3 Base de données & ORM
- **SGBD Production** : PostgreSQL 16 (`postgres:16-alpine`, [`docker-compose.yml:3`](file:///C:/Users/denoe/Documents/Dev/StudyHub/docker-compose.yml#L3))
- **SGBD Développement & Tests** : SQLite (`studyhub_dev.db` en dev, SQLite in-memory `sqlite://` en test, [`backend/app/config.py:37,44`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/app/config.py#L37-L44))
- **Pilote PostgreSQL** : `psycopg2-binary>=2.9.9` ([`backend/requirements.txt:10`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/requirements.txt#L10))
- **ORM** : `SQLAlchemy>=2.0.35` avec extension `Flask-SQLAlchemy==3.1.1` ([`backend/requirements.txt:2-3`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/requirements.txt#L2-L3))
  - Configuration du pool : `pool_pre_ping=True`, `pool_size=5`, `max_overflow=5`, `pool_recycle=1800` en production ([`backend/app/config.py:68-73`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/app/config.py#L68-L73))
- **Migrations de schéma** : Alembic via `Flask-Migrate==4.0.7` ([`backend/requirements.txt:4`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/requirements.txt#L4))
  - *Mécanisme d'auto-migration* : Déclenché à l'initialisation du WSGI ([`backend/wsgi.py:15`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/wsgi.py#L15), [`backend/app/db_migrate.py:25-39`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/app/db_migrate.py#L25-L39)).
  - *Verrou d'avis PostgreSQL* : `SELECT pg_advisory_lock(7270727)` sérialise les migrations entre les workers gunicorn au démarrage ([`backend/app/db_migrate.py:22,43-47`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/app/db_migrate.py#L22-L47)).

### 2.4 Authentification & Sécurité
- **Authentification** : JWT stateless via `Flask-JWT-Extended==4.6.0` et `PyJWT==2.8.0` ([`backend/requirements.txt:5,9`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/requirements.txt#L5-L9))
- **Révocation de jetons** : Blocklist gérée dans Redis basée sur l'identifiant `jti` ([`backend/app/middlewares/auth_middleware.py:6-11`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/app/middlewares/auth_middleware.py#L6-L11))
- **Cryptographie** : `cryptography==42.0.7` ([`backend/requirements.txt:15`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/requirements.txt#L15))
- **Validation des données** : `pydantic>=2.7.2` et `email-validator==2.1.1` ([`backend/requirements.txt:6-7`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/requirements.txt#L6-L7))
- **En-têtes HTTP & CSP** : `flask-talisman>=1.1.0` avec politique CSP stricte ([`backend/requirements.txt:22`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/requirements.txt#L22), [`backend/app/__init__.py:64-106`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/app/__init__.py#L64-L106))
- **Rate Limiting** : `Flask-Limiter==3.7.0` (200/jour, 50/heure en prod ; 2000/jour, 500/heure en dev ; désactivé en tests, [`backend/app/extensions.py:18-25`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/app/extensions.py#L18-L25), [`backend/app/config.py:49`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/app/config.py#L49))
- **CORS** : `flask-cors>=4.0.1` avec whitelist stricte incluant web (`https://study.leshen.cloud`, `http://localhost:5173`, `http://localhost:3000`), Electron (`app://-`), et Capacitor (`https://localhost`, `capacitor://localhost`) ([`backend/app/__init__.py:13-24`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/app/__init__.py#L13-L24))
- **Sanitisation HTML** : `bleach>=6.0.0` et `tinycss2>=1.2.0` ([`backend/requirements.txt:23-24`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/requirements.txt#L23-L24))
- **Validation des types MIME** : `python-magic==0.4.27` (Linux) / `python-magic-bin==0.4.14` (Windows) ([`backend/requirements.txt:18-19`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/requirements.txt#L18-L19))

### 2.5 Traitements Asynchrones & Cache
- **Broker & Backend Celery** : `redis>=5.0.0` (image `redis:7-alpine`, [`backend/requirements.txt:20`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/requirements.txt#L20), [`docker-compose.yml:22`](file:///C:/Users/denoe/Documents/Dev/StudyHub/docker-compose.yml#L22))
- **Moteur de tâches** : `celery>=5.4.0` ([`backend/requirements.txt:25`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/requirements.txt#L25))
- **Worker conteneurisé** : Commande `celery -A celery_worker:celery_app worker --loglevel=info --concurrency=2` ([`docker-compose.yml:85`](file:///C:/Users/denoe/Documents/Dev/StudyHub/docker-compose.yml#L85))
- **Tolérance aux pannes (Smart Fallback)** :
  - `SmartRedis` : Bascule transparente sur un dictionnaire mémoire interne `RedisFallback` si Redis est inaccessible ([`backend/app/extensions.py:34-103`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/app/extensions.py#L34-L103)).
  - `dispatch_or_run` : Envoi asynchrone Celery avec bascule automatique en exécution synchrone inline si le broker Redis est indisponible ([`backend/app/utils/task_dispatch.py:6-33`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/app/utils/task_dispatch.py#L6-L33)).

### 2.6 Intégration IA (Google Gemini)
- **Modèle cible** : `gemini-2.0-flash` (défaut `docker-compose.yml:55` et `.env.example:21` ; `gemini-3.5-flash` en fallback code [`backend/app/services/ai_service.py:10`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/app/services/ai_service.py#L10))
- **Client HTTP** : Directement via `urllib.request` standard (évite les lourdes dépendances SDK `google-generativeai`, [`backend/app/services/ai_service.py:1-4,124-135`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/app/services/ai_service.py#L1-L4))
- **Fonctionnalités IA couvertes** :
  1. Blurting / Page blanche (`analyze_blurting`, [`backend/app/services/ai_service.py:12`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/app/services/ai_service.py#L12))
  2. Méthode Feynman (`analyze_feynman`, [`backend/app/services/ai_service.py:270`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/app/services/ai_service.py#L270))
  3. Génération de flashcards atomiques avec taux de couverture ([`backend/app/services/ai_service.py:344`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/app/services/ai_service.py#L344))
  4. Génération de quiz QCM ([`backend/app/services/ai_service.py:428`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/app/services/ai_service.py#L428))
  5. Génération d'évaluations formatives ([`backend/app/services/ai_service.py:489`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/app/services/ai_service.py#L489))
  6. Notation de fiches de cours (`grade_note`, [`backend/app/services/ai_service.py:738`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/app/services/ai_service.py#L738))
  7. Synthèse des lacunes collectives de classe (`summarize_class_gaps`, [`backend/app/services/ai_service.py:840`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/app/services/ai_service.py#L840))

### 2.7 Outillage de Test & Qualité Backend
- **Test Runner** : `pytest==8.2.1` et `pytest-flask==1.3.0` ([`backend/requirements.txt:13-14`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/requirements.txt#L13-L14))
- **Couverture de code** : `pytest-cov==7.1.0` avec seuil CI bloquant à 80% (`--cov-fail-under=80`, [`backend/requirements-dev.txt:6`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/requirements-dev.txt#L6), [`.github/workflows/ci.yml:41`](file:///C:/Users/denoe/Documents/Dev/StudyHub/.github/workflows/ci.yml#L41))
- **Fixtures & Bouchons** : `factory-boy==3.3.1`, `Faker==30.8.2`, `freezegun==1.5.1` ([`backend/requirements-dev.txt:9-11`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/requirements-dev.txt#L9-L11))
- **Linter & Formatter** : `ruff==0.16.4` ([`backend/requirements-dev.txt:14`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/requirements-dev.txt#L14))
- **Profilage SQL** : Profiler personnalisé `assert_max_queries` et écouteur d'événements Engine (`before_cursor_execute`) pour traquer les régressions N+1 ([`backend/app/utils/sql_profiler.py:1-62`](file:///C:/Users/denoe/Documents/Dev/StudyHub/backend/app/utils/sql_profiler.py#L1-L62))

---

## 3. Frontend Web

### 3.1 Langage, Framework & Build
- **Framework** : `vue==^3.5.34` (Composition API, `<script setup lang="ts">`, [`web/package.json:35`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L35))
- **Outil de build** : `vite==^8.0.12` avec plugin `@vitejs/plugin-vue==^6.0.6` ([`web/package.json:48,64`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L48-L64))
- **Langage** : `typescript==~6.0.2` avec vérificateur strict `vue-tsc==^3.2.8` ([`web/package.json:62,66`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L62-L66))
- **Configuration TS** : Base `@vue/tsconfig==^0.9.1` ([`web/package.json:51`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L51))

### 3.2 Routage & État Applicatif
- **Routing** : `vue-router==^4.6.4` ([`web/package.json:36`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L36))
  - Modes d'historique dynamiques : HTML5 History (`createWebHistory`) pour le Web et le Mobile Capacitor ; Hash History (`createWebHashHistory`) pour Electron afin d'éviter la rupture des deep links sous protocole `app://-` ([`web/src/router/index.ts:262-265`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/src/router/index.ts#L262-L265)).
  - Guards d'authentification : Protection globale via `router.beforeEach` (`requiresAuth`, `guestOnly`, [`web/src/router/index.ts:279-290`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/src/router/index.ts#L279-L290)).
- **Gestion de l'état (State Management)** : `pinia==^3.0.4` ([`web/package.json:34`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L34))
  - 12 stores modulaires : `auth`, `binders`, `decks`, `focus`, `groups`, `notes`, `notifications`, `pdf`, `planning`, `pomodoro`, `revision`, `tags` ([`web/src/stores/`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/src/stores/)).

### 3.3 Style & Design System
- **CSS Utility** : `tailwindcss==^3.4.19`, `postcss==^8.5.15`, `autoprefixer==^10.5.0` ([`web/package.json:52,59,61`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L52-L61))
- **Composants Headless** : `@headlessui/vue==^1.7.23` ([`web/package.json:26`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L26))
- **Animations & Transitions** : `@vueuse/motion==^3.0.3` ([`web/package.json:27`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L27), [`web/src/main.ts:19`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/src/main.ts#L19))
- **Pack d'icônes** : `lucide-vue-next==^1.0.0` et `@lucide/vue==^1.17.0` ([`web/package.json:32,42`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L32-L42))
- **Design System** : Direction A (« Fiche »), remplaçant l'ancien thème White/Pink par un thème épuré avec tokens CSS dans `web/src/style.css`, vérification de contraste AA automatisée et 10 primitives de base en TDD (`BaseButton`, `BaseInput`, `BaseCard`, `BaseModal`, `BaseBadge`, `BaseToast`, `BaseTooltip`, `BaseEmptyState`, `BaseSkeleton`, `Tabs`, [`web/src/components/ui/base/`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/src/components/ui/base/)).

### 3.4 Rendu de Contenu & Richesse Éditoriale
- **Client HTTP** : `axios==^1.16.1` avec instance pré-configurée (injection Bearer JWT, refresh automatique sur 401, timeout 120s pour appels IA, [`web/package.json:28`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L28), [`web/src/services/api.ts:5-61`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/src/services/api.ts#L5-L61)).
- **Rendu Markdown** : `marked==^18.0.4` ([`web/package.json:33`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L33))
- **Sanitisation DOM** : `dompurify==^3.4.10` avec directive Vue `v-dompurify-html` ([`web/package.json:29`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L29), [`web/src/main.ts:14-16`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/src/main.ts#L14-L16))
- **Coloration Syntaxique** : `highlight.js==^11.11.1` ([`web/package.json:30`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L30))
- **Formules Mathématiques (LaTeX)** : `katex==^0.17.0` ([`web/package.json:31`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L31))
- **Moteur de Diagrammes** : Éditeur SVG réactif maison (glisser-déposer, canevas infini, snapping, historique undo/redo), sans dépendance Mermaid runtime ([`web/src/views/Diagrams/Diagrams.vue`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/src/views/Diagrams/Diagrams.vue), [`web/tests/diagram/`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/tests/diagram/)).
- **Agent Discovery (WebMCP)** : Exposition d'outils WebMCP via `navigator.modelContext.registerTool` pour les agents autonomes ([`web/src/main.ts:28-48`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/src/main.ts#L28-L48)).

### 3.5 Outillage de Test & Qualité Frontend
- **Tests Unitaires & Composants** : `vitest==^4.1.8`, `@vue/test-utils==^2.4.11`, environnement DOM `happy-dom==^20.10.2` ([`web/package.json:50,58,65`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L50-L65))
- **Couverture Frontend** : `@vitest/coverage-v8==^4.1.8` ([`web/package.json:49`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L49))
- **Tests Basés sur les Propriétés (Property-based Testing)** : `fast-check==^4.9.0` (notamment pour l'historique de l'éditeur de diagrammes, [`web/package.json:57`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L57))
- **Tests End-to-End (E2E)** : `@playwright/test==^1.60.0` avec navigateur Chromium ([`web/package.json:43`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L43), [`.github/workflows/ci.yml:207-211`](file:///C:/Users/denoe/Documents/Dev/StudyHub/.github/workflows/ci.yml#L207-L211))
- **Linter & Formatteur** : `eslint==^10.9.0`, `typescript-eslint==^8.67.0`, `eslint-plugin-vue==^10.10.0`, `prettier==^3.9.6`, `eslint-config-prettier==^10.1.8` ([`web/package.json:54-56,60,63`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L54-L63))

### 3.6 Serveur Web de Production (Conteneur Frontend)
- **Serveur HTTP** : `nginx:alpine` ([`web/Dockerfile:12`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/Dockerfile#L12))
- **Configuration SPA & Reverse Proxy** : `web/nginx.spa.conf` ([`web/nginx.spa.conf:1-108`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/nginx.spa.conf#L1-L108))
  - Support du routage HTML5 (`try_files $uri $uri/ /index.html`, [`web/nginx.spa.conf:24`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/nginx.spa.conf#L24))
  - Négociation de contenu pour agents IA (`Accept: text/markdown`, [`web/nginx.spa.conf:14-19`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/nginx.spa.conf#L14-L19))
  - En-têtes RFC 8288 de découverte d'agents (`Link: </.well-known/api-catalog>`, [`web/nginx.spa.conf:21-22`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/nginx.spa.conf#L21-L22))
  - Redirection interne `X-Accel-Redirect` vers `/internal_uploads/` pour le streaming de PDF sans monopoliser les workers Python ([`web/nginx.spa.conf:98-101`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/nginx.spa.conf#L98-L101)).

---

## 4. Mobile (Capacitor)

- **Framework d'encapsulation** : Capacitor **8** (`@capacitor/core==^8.4.1`, `@capacitor/cli==^8.4.1`, [`web/package.json:21,40`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L21-L40))
- **Plateformes cibles** : Android 10+ / iOS 16+
- **Projet Android Natif** : Généré directement dans `web/android/` ([`web/android/build.gradle`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/android/build.gradle), [`web/android/app/`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/android/app/))
- **Schéma Android** : `androidScheme: 'https'` permettant à l'application d'être servie depuis `https://localhost` (origine HTTP réelle garantissant le fonctionnement de l'historique HTML5 et du CORS, [`web/capacitor.config.ts:10`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/capacitor.config.ts#L10))
- **Plugins natifs intégrés** :
  - Système de fichiers : `@capacitor/filesystem==^8.1.2` ([`web/package.json:22`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L22))
  - Retours haptiques : `@capacitor/haptics==^8.0.2` ([`web/package.json:23`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L23))
  - Notifications locales : `@capacitor/local-notifications==^8.2.0` ([`web/package.json:24`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L24))
  - Stockage de préférences : `@capacitor/preferences==^8.0.1` ([`web/package.json:25`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/package.json#L25))
- **Détection de la plateforme** : Composable `usePlatform()` basé sur `Capacitor.isNativePlatform()` et `Capacitor.getPlatform()` ([`web/src/composables/usePlatform.ts:18-27`](file:///C:/Users/denoe/Documents/Dev/StudyHub/web/src/composables/usePlatform.ts#L18-L27)).

---

## 5. Bureau (Electron)

- **Runtime** : `electron==^33.2.1` ([`desktop/package.json:26`](file:///C:/Users/denoe/Documents/Dev/StudyHub/desktop/package.json#L26))
- **Packager / Distributeur** : `electron-builder==^25.1.8` (cibles Linux AppImage/deb, Windows NSIS/portable, macOS dmg, [`desktop/package.json:27`](file:///C:/Users/denoe/Documents/Dev/StudyHub/desktop/package.json#L27), [`desktop/electron-builder.yml`](file:///C:/Users/denoe/Documents/Dev/StudyHub/desktop/electron-builder.yml))
- **Serveur de fichiers packagé** : `electron-serve==^2.1.1` servant les ressources `web/dist` sous le schéma personnalisé sécurisé `app://-` ([`desktop/package.json:32`](file:///C:/Users/denoe/Documents/Dev/StudyHub/desktop/package.json#L32), [`desktop/src/main.ts:51-54`](file:///C:/Users/denoe/Documents/Dev/StudyHub/desktop/src/main.ts#L51-L54))
- **Sécurité Electron** :
  - `contextIsolation: true`, `nodeIntegration: false`, `sandbox: true` ([`desktop/src/main.ts:24-26`](file:///C:/Users/denoe/Documents/Dev/StudyHub/desktop/src/main.ts#L24-L26))
  - Navigation externe strictement déléguée au navigateur système par défaut (`shell.openExternal`, blocage de `window.open`, [`desktop/src/main.ts:34-45`](file:///C:/Users/denoe/Documents/Dev/StudyHub/desktop/src/main.ts#L34-L45))
- **Pont IPC / Preload** : `desktop/src/preload.ts` exposant uniquement l'objet immuable `{ isDesktop: true, version }` via `contextBridge.exposeInMainWorld` ([`desktop/src/preload.ts:9-12`](file:///C:/Users/denoe/Documents/Dev/StudyHub/desktop/src/preload.ts#L9-L12)).

---

## 6. Infrastructure, Déploiement & Multi-Architecture

### 6.1 Topologie Docker Compose
Fichier unique racine `docker-compose.yml` définissant 5 services interconnectés ([`docker-compose.yml:1-106`](file:///C:/Users/denoe/Documents/Dev/StudyHub/docker-compose.yml#L1-L106)) :

| Service | Image / Base | Rôle | Exposition / Ports | Volumes |
|---|---|---|---|---|
| `db` | `postgres:16-alpine` | Base de données relationnelle | 5432 (interne au réseau) | `pgdata:/var/lib/postgresql/data` |
| `redis` | `redis:7-alpine` | Cache & Broker de messages Celery | 6379 (interne au réseau) | Éphémère / RAM |
| `backend` | `./backend` (`python:3.12-slim`) | API REST Flask (gunicorn) | 5000 (interne au réseau) | `uploads_data:/app/uploads` |
| `worker` | `./backend` (`python:3.12-slim`) | Exécuteur de tâches asynchrones Celery | Aucun (consommateur Redis) | `uploads_data:/app/uploads` |
| `frontend` | `./web` (`node:20` build -> `nginx:alpine`) | Serveur HTTP Nginx, SPA & Reverse Proxy | **80:80** (public) | `uploads_data:/app/uploads:ro` |

### 6.2 Support Multi-Architecture (amd64 & arm64)
- Testé et validé nativement sur architecture x86_64 (`amd64` en runners CI) et Apple Silicon / ARM (`linux/aarch64` / `arm64` natif, [`docs/ENVIRONNEMENT.md:3-6`](file:///C:/Users/denoe/Documents/Dev/StudyHub/docs/ENVIRONNEMENT.md#L3-L6)).
- Roues Python (`psycopg2-binary`, `cryptography`, `gevent`, `greenlet`) disponibles pré-compilées pour les deux architectures sans compilation GCC ([`docs/ENVIRONNEMENT.md:28-30`](file:///C:/Users/denoe/Documents/Dev/StudyHub/docs/ENVIRONNEMENT.md#L28-L30)).
- `Makefile` et `scripts/dev-up.sh` avec détection automatique de l'architecture (`uname -m`) pour appliquer les surcouches `docker-compose.amd64.yml` ou `docker-compose.arm64.yml` ([`Makefile:3-15`](file:///C:/Users/denoe/Documents/Dev/StudyHub/Makefile#L3-L15)).

---

## 7. Pipeline CI/CD (GitHub Actions)

Fichier de workflow principal : `.github/workflows/ci.yml` ([`.github/workflows/ci.yml:1-212`](file:///C:/Users/denoe/Documents/Dev/StudyHub/.github/workflows/ci.yml#L1-L212)) déclenché sur `push` et `pull_request` vers `main` et `develop` avec `cancel-in-progress: true` :

1. **`backend-tests`** : Pytest avec couverture sur base SQLite mémoire (`--cov-fail-under=80`, [`.github/workflows/ci.yml:16-42`](file:///C:/Users/denoe/Documents/Dev/StudyHub/.github/workflows/ci.yml#L16-L42)).
2. **`backend-tests-postgres`** : Rejeu de la suite complète sur service conteneurisé `postgres:16-alpine` réel afin de détecter les divergences SQL dialect-spécifiques ([`.github/workflows/ci.yml:43-84`](file:///C:/Users/denoe/Documents/Dev/StudyHub/.github/workflows/ci.yml#L43-L84)).
3. **`migrations` (Garde Anti-Drift)** : Exécute `flask db upgrade` sur une base Postgres vierge, puis lance `flask db migrate -m "ci_drift_check"`. Échoue si un modèle a changé sans migration committée ([`.github/workflows/ci.yml:85-146`](file:///C:/Users/denoe/Documents/Dev/StudyHub/.github/workflows/ci.yml#L85-L146)).
4. **`frontend-build`** : Validation des types via `vue-tsc -b` et build Vite production ([`.github/workflows/ci.yml:147-167`](file:///C:/Users/denoe/Documents/Dev/StudyHub/.github/workflows/ci.yml#L147-L167)).
5. **`frontend-tests`** : Exécution de Vitest en mode headless (`test:run`, [`.github/workflows/ci.yml:168-188`](file:///C:/Users/denoe/Documents/Dev/StudyHub/.github/workflows/ci.yml#L168-L188)).
6. **`e2e`** : Tests End-to-End Playwright avec Chromium sur frontend Vite instrumenté et API mockée ([`.github/workflows/ci.yml:189-212`](file:///C:/Users/denoe/Documents/Dev/StudyHub/.github/workflows/ci.yml#L189-L212)).

---

## 8. Référentiel des Variables d'Environnement

Inventaire exhaustif établi depuis `.env.example`, `docker-compose.yml` et `backend/app/config.py` :

| Variable | Composant | Rôle | Valeur par défaut / Exemple | Sensibilité |
|---|---|---|---|---|
| `POSTGRES_USER` | DB, Backend, Worker | Utilisateur PostgreSQL | `studyhub` | Moyenne |
| `POSTGRES_PASSWORD` | DB, Backend, Worker | Mot de passe PostgreSQL | `changeme` | **Critique** |
| `POSTGRES_DB` | DB, Backend, Worker | Nom de la base relationnelle | `studyhub` | Faible |
| `DATABASE_URL` | Backend, Worker | Chaîne de connexion SQLAlchemy | `postgresql://user:pass@db:5432/db` (prod) / `sqlite:///...` (dev) | **Critique** |
| `FLASK_ENV` | Backend, Worker | Environnement d'exécution Flask | `development` / `production` / `testing` | Faible |
| `REDIS_URL` | Backend, Worker | URL de connexion Redis (Cache & Celery) | `redis://localhost:6379/0` (dev) / `redis://redis:6379/0` (docker) | Moyenne |
| `SECRET_KEY` | Backend, Worker | Clé secrète de signature de session Flask | Défaut non sécurisé en dev, **requis** en prod | **Critique** |
| `JWT_SECRET_KEY` | Backend, Worker | Clé secrète de signature des jetons JWT | Défaut non sécurisé en dev, **requis** en prod | **Critique** |
| `JWT_ACCESS_TOKEN_EXPIRES` | Backend | Durée de validité du jeton d'accès (secondes) | `900` (15 min en dev/prod, 5s en test) | Faible |
| `JWT_REFRESH_TOKEN_EXPIRES` | Backend | Durée de validité du jeton de rafraîchissement | `2592000` (30 jours en dev/prod, 10s en test) | Faible |
| `UPLOAD_FOLDER` | Backend, Worker | Répertoire de stockage des fichiers uploadés (PDF) | `/app/uploads` (prod) / `../uploads` (dev) | Faible |
| `MAX_CONTENT_LENGTH` | Backend | Taille maximale autorisée pour un payload/upload | `52428800` (50 Mo) | Faible |
| `GEMINI_API_KEY` | Backend, Worker | Clé d'API Google Gemini pour les inférences IA | Variable secrète utilisateur | **Critique** |
| `GEMINI_MODEL` | Backend, Worker | Identifiant du modèle Google Gemini utilisé | `gemini-2.0-flash` | Faible |
| `SLOW_REQUEST_MS` | Backend | Seuil en millisecondes pour journalisation WARNING | `500` | Faible |
| `LOG_LEVEL` | Backend | Niveau de verbosité des logs racine | `INFO` | Faible |
| `CORS_ALLOWED_ORIGINS` | Backend | Whitelist d'origines autorisées séparées par virgule | `https://study.leshen.cloud,http://localhost:5173,...` | Moyenne |
| `VITE_API_BASE_URL` | Frontend | URL de base de l'API consommée au build/runtime | `http://localhost:5000` (dev) / vide (prod, proxy Nginx) | Faible |
| `VITE_DESKTOP` | Frontend | Flag de compilation pour activer le Hash History | `true` (uniquement lors du packaging Electron) | Faible |
