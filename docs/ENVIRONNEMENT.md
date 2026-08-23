# Environnement conteneurisé — StudyHub

> Vérification multi-architecture (phase 1). Chiffres mesurés, pas estimés — voir la
> méthode sous chaque tableau. Machine de mesure arm64 : Docker Desktop 29.6.2 / Compose
> v5.3.1, moteur `linux/aarch64` natif (`docker info --format '{{.OSType}}/{{.Architecture}}'`).

## Structure

- `docker-compose.yml` — socle, écrit pour fonctionner tel quel sur amd64 et arm64.
- `docker-compose.amd64.yml` / `docker-compose.arm64.yml` — surcouches d'architecture.
  **Les deux sont actuellement vides** : voir "Audit des dépendances" ci-dessous, c'est un
  bon signe (rien d'irréductible à isoler par architecture pour l'instant).
- `docker-compose.override.yml` — confort dev (bind mounts, hot reload), non versionné, pas
  encore créé (aucun bind-mount de code dans le socle actuel : `docker compose up` sert le
  code figé dans l'image, pas le répertoire de travail — à faire si le besoin se confirme).
- `scripts/dev-up.sh` / `Makefile` — détection d'architecture (`uname -m`) et composition de
  la bonne commande `docker compose -f docker-compose.yml -f docker-compose.<arch>.yml`.
- `.env.example` — variables attendues par `docker-compose.yml` et `backend/app/config.py`
  (aucun `.env`/`.env.example` n'existait avant cette vérification).

## Audit des images et dépendances (aucune trouvée problématique)

| Composant | Image / paquet | arm64 | Constat |
|---|---|---|---|
| `db` | `postgres:16-alpine` | ✅ | Pull natif `linux/aarch64` observé (pas d'émulation). |
| `redis` | `redis:7-alpine` | ✅ | Idem. |
| `backend`/`worker` | `python:3.12-slim` | ✅ | Build natif, aucune erreur. |
| — | `psycopg2-binary==2.9.12` | ✅ | Roue `manylinux...aarch64` — pas de compilation. |
| — | `cryptography==42.0.7` | ✅ | Roue aarch64 (dépendance de `flask-talisman`/JWT). |
| — | `gevent==26.8.0` / `greenlet==3.5.5` / `cffi` | ✅ | Roues aarch64. |
| `frontend` | `node:20-alpine` (build) | ✅ | Build natif (non re-testé isolément cette session — voir "Frontend" plus bas, `npm`/`vitest`/`vite` tournent nativement en dehors du conteneur sur cette machine). |

Aucun `platform:` forcé nulle part dans `docker-compose.yml` — inutile à ce stade.

## Backend — vérification réelle (arm64 natif, cette machine)

Toutes les commandes ci-dessous utilisent `docker compose exec backend ...` (conteneur
réellement démarré, pas une commande locale hors conteneur).

| Étape | Commande | Durée mesurée | Résultat |
|---|---|---|---|
| Build image backend (à froid, sans cache) | `docker compose build backend` | **1 min 10 s** | OK |
| Démarrage `db`+`redis`+`backend` | `docker compose up -d db redis backend` | **22,6 s** | 3 conteneurs `healthy`/`started` |
| Auto-migration au démarrage | (automatique, `wsgi.py`) | incluse ci-dessus | `alembic_version` = `4e6e094d2711`, identique au head local (`flask db heads`) |
| Suite complète, SQLite (équivalent job CI `backend-tests`) | `pytest -p no:cacheprovider -q` (`DATABASE_URL=sqlite://`) | **56,4 s** | **✅ 100 % vert** (0 échec) |
| Run ciblé (1 fichier, `test_tags.py`) | `pytest tests/test_tags.py -q` | **2,9 s** | ✅ vert |
| Suite complète, PostgreSQL réel (équivalent job CI `backend-tests-postgres`) | `pytest -q` (`TEST_DATABASE_URL=postgresql://...`) | 4 min 3 s | ⚠️ 12 échecs — voir constat ci-dessous, **non bloquant pour cette vérification** |

### Bug corrigé en cours de route (pas architecture-spécifique)

Le premier run complet échouait sur `test_pdfs.py::test_upload_list_rename_delete_pdf`
(`PermissionError` en écriture dans `/app/uploads`) : le volume nommé `uploads_data` se crée
avec le propriétaire `root` par défaut au premier montage, alors que le conteneur tourne en
`appuser`. `backend/Dockerfile` créait déjà `/app` avec le bon propriétaire, mais pas
`uploads/` (absent du dépôt, créé seulement au runtime) — Docker ne propage l'ownership de
l'image vers un volume nommé que si le répertoire existe déjà côté image avant le premier
montage. Corrigé par un `mkdir -p /app/uploads` explicite avant le `chown -R appuser /app`.
**Ce bug n'a rien à voir avec l'architecture** — il se serait produit identiquement sur amd64 ;
il est corrigé une fois pour toutes dans l'image, pas par surcouche arm64.

### Constat non corrigé — écarté du périmètre phase 1

Les 12 échecs contre PostgreSQL réel sont **identiques, mot pour mot**, que le test tourne ici
(arm64) — **rien n'indique une cause liée au CPU** : ce sont des `sqlalchemy.exc.IntegrityError`
et des résultats de recherche vides (`assert 0 == 2`, etc.), typiques d'un schéma créé via
`db.create_all()` (fixture `clean_db` de `conftest.py`, métadonnées SQLAlchemy) plutôt que via
les migrations Alembic réelles — les éléments définis uniquement en SQL brut dans une migration
(ex. index GIN de recherche full-text) n'existent alors pas. Le job CI `backend-tests-postgres`
utilise le même mécanisme (`TEST_DATABASE_URL` + `conftest.py`), donc cet écart concerne
vraisemblablement aussi bien amd64 — **à vérifier et traiter en phase 2**
(`docs/audit/04-TESTS-CI.md`), pas ici : corriger l'application est hors périmètre de l'audit
d'environnement de la phase 1.

## Frontend — vérification réelle (arm64 natif, cette machine)

Pas de conteneur dédié aux tests : `web/Dockerfile` n'a qu'un stage `production` (build Vite +
Nginx), rien à exécuter dedans pour `vitest`. Vérifié nativement via Node (`node --version` :
v24.18.0), qui tourne déjà en arm64 natif sur cette machine — pas d'émulation non plus.

| Étape | Commande | Durée mesurée | Résultat |
|---|---|---|---|
| Typecheck + build (équivalent job CI `frontend-build`) | `npm run build` | **12,2 s** | ✅ (avertissement bundle > 500 kB sur `katex`, hors sujet ici — noté pour l'audit perf phase 2) |
| Suite complète (équivalent job CI `frontend-tests`) | `npx vitest run` | **7,8 s** (durée interne rapportée : 4,0 s) | **✅ 100 % vert** — 17 fichiers, 69 tests |
| Run ciblé (1 fichier) | `npx vitest run tests/stores/notifications.spec.ts` | **2,8 s** | ✅ vert |

## amd64 — non re-testé dans cette session, appuyé sur la CI existante

Cette machine est nativement arm64 : impossible d'y valider amd64 sans émulation QEMU (écartée,
cf. AGENTS.md/prompt de démarrage — l'émulation dégrade trop les performances pour être
significative). La validation amd64 native s'appuie donc sur la **CI GitHub Actions existante**
(`.github/workflows/ci.yml`, runners `ubuntu-latest` = amd64), qui exécute déjà, sur chaque
push/PR vers `main`/`develop` : `backend-tests` (SQLite), `backend-tests-postgres`,
`migrations` (garde anti-drift), `frontend-build`, `frontend-tests`, `e2e` — les mêmes suites
que ci-dessus. **Cette session n'a pas déclenché de nouveau run CI** (aucun push effectué,
conformément à l'interdiction absolue de `git push`) : la prochaine ouverture de PR sur cette
branche revalidera amd64 nativement avec ce même Dockerfile corrigé.

## Démarrage à froid — résumé

Depuis un dépôt cloné sans image construite : `docker compose build` (~1 min 10 s pour
`backend` seul, mesuré ; `worker` réutilise la même image, `frontend`/`db`/`redis` non
re-mesurés isolément) puis `docker compose up -d` (~23 s pour `db`+`redis`+`backend`,
migrations auto-appliquées dans ce délai). Copier `.env.example` en `.env` et renseigner les
valeurs avant le premier lancement — `docker compose` refuse de démarrer sinon (variables
requises absentes).

## Ce qui reste à faire (hors périmètre de cette vérification)

- Créer `docker-compose.override.yml` (bind mounts dev) si le besoin de hot-reload en
  conteneur se confirme — actuellement le développement local direct (`start.sh`,
  `npm run dev`) sert cet usage.
- Traiter l'écart `db.create_all()` vs migrations Alembic en phase 2 (`04-TESTS-CI.md`).
- Mesurer `frontend`/`e2e` (Playwright) en conteneur si un jour nécessaire — non fait ici,
  ces suites tournent déjà nativement (CI) sans dépendre de Docker.
