---
name: deployment
description: Déploiement StudyHub (docker-compose, CI GitHub Actions, migrations Alembic & auto-migration au démarrage, garde anti-drift). À charger avant de toucher Docker, la CI, ou une migration.
---

# deployment

Référence canonique migrations : `docs/migrations.md`. Ce skill couvre Docker, CI et le cycle
de migration.

## Topologie Docker (`docker-compose.yml`)

| Service | Image / build | Rôle |
|---|---|---|
| `db` | `postgres:16-alpine` | Base prod (volume `pgdata`). |
| `redis` | `redis:7-alpine` | Broker / cache (tâches async IA). |
| `backend` | `backend/Dockerfile` | API Flask via `gunicorn wsgi:app`. |
| `worker` | `backend/Dockerfile` | Worker tâches asynchrones (évaluations IA). |
| `frontend` | `web/Dockerfile` | Build Vue servi par Nginx (proxifie `/api/v1`). |

Volumes : `pgdata`, `uploads_data` (PDFs).

## Migrations Alembic — règle d'or

Le « schéma voulu » = le **head Alembic** (`backend/migrations/versions/`). On applique
uniquement des migrations **déjà écrites et versionnées** ; jamais d'autogenerate en prod.

### Auto-migration au démarrage

- Vit **uniquement** dans `backend/wsgi.py` → `create_app()` puis `run_auto_migrations(app)`.
- `backend/app/db_migrate.py` : ignore `TESTING` ; en PostgreSQL sérialise les workers gunicorn
  via `pg_advisory_lock` (un seul migre) ; idempotent (no-op si déjà au head).
- **Ne vit pas** dans `create_app` ni dans `flask db` (`FLASK_APP=app`) → n'interfère pas avec un
  `downgrade` manuel.

| Contexte | Commande | Auto-migre ? |
|---|---|---|
| Prod Docker | `gunicorn wsgi:app` | ✅ |
| Dev `start.sh` | `FLASK_APP=wsgi:app flask run` | ✅ |
| CLI migrations | `FLASK_APP=app flask db ...` | ❌ |
| Tests | pytest (`TESTING`) | ❌ |

### Workflow développeur

```bash
cd backend
FLASK_APP=app flask db migrate -m "describe change"   # après modif d'un modèle
# relire le fichier généré, puis :
FLASK_APP=app flask db upgrade
# committer la migration AVEC le changement de modèle
```

## CI (`.github/workflows/ci.yml`) — ce qui bloque une PR

- **Backend · tests & coverage** : pytest, gate coverage (≥ 80 %).
- **Backend · tests (PostgreSQL)** : suite contre Postgres réel.
- **Backend · migrations (PostgreSQL)** : applique toutes les migrations sur une base vierge,
  puis `flask db migrate` (autogenerate) — si une migration non vide est produite, un modèle a
  divergé → **PR bloquée**, diff affiché. ⚠️ tourne sur **PostgreSQL** (les index GIN full-text
  `*_search_idx` apparaîtraient en faux drift sous SQLite).
- **Frontend** : typecheck + build (`vue-tsc`), Vitest, E2E Playwright.

Cause racine historique des bugs de migration : un modèle modifié **sans** migration. La garde
anti-drift existe pour ça — ne jamais la contourner.
