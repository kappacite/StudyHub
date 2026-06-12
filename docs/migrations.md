# Migrations & auto-migration — StudyHub

## Principe

Le « schéma voulu » = le **head Alembic** (`backend/migrations/versions/`).
Au démarrage du serveur, si la base est en retard sur ce head, les migrations
versionnées manquantes sont **appliquées automatiquement** (`upgrade head`).

> On applique uniquement des migrations **déjà écrites et versionnées**. On ne
> génère jamais de migration à la volée en production (autogenerate peut rater
> des renommages/types et provoquer des pertes de données).

## Où vit l'auto-migration

- **`backend/wsgi.py`** — entrypoint serveur. À l'import : `create_app()` puis
  `run_auto_migrations(app)`. C'est le **seul** endroit qui auto-migre.
- **`backend/app/db_migrate.py`** — `run_auto_migrations()` :
  - ignore le mode `TESTING` (les tests gèrent leur schéma via `db.create_all`) ;
  - en **PostgreSQL**, sérialise les 4 workers gunicorn avec un **verrou d'avis**
    (`pg_advisory_lock`) — un seul migre, les autres voient « déjà à jour » ;
  - idempotent : ne fait rien si la base est déjà au head.

L'auto-migration **ne vit pas** dans `create_app` ni dans les commandes `flask db`
(`FLASK_APP=app`), pour ne pas interférer avec un `downgrade` manuel.

| Contexte | Commande | Auto-migration ? |
|---|---|---|
| Prod (Docker) | `gunicorn ... wsgi:app` | ✅ oui |
| Dev (`start.sh`) | `FLASK_APP=wsgi:app flask run` | ✅ oui |
| CLI migrations | `FLASK_APP=app flask db ...` | ❌ non (volontaire) |
| Tests | pytest | ❌ non (`TESTING`) |

## Garde-fou CI anti-drift

Cause racine des anciens bugs de migration : un modèle modifié **sans** migration
correspondante. Le job CI `Backend · migrations (PostgreSQL)` :
1. applique toutes les migrations sur une base Postgres vierge (`flask db upgrade`) ;
2. lance `flask db migrate` (autogenerate). Si une migration non vide est produite,
   c'est qu'un modèle a divergé → **la PR est bloquée** et le diff est affiché.

⚠️ Le check tourne sur **PostgreSQL** : sous SQLite, les index GIN full-text
(`*_search_idx`) apparaîtraient comme un faux drift (SQLite ne les supporte pas).

## Workflow développeur

```bash
# Modifier un modèle SQLAlchemy, puis générer la migration :
cd backend
FLASK_APP=app flask db migrate -m "describe change"
# Relire le fichier généré, puis l'appliquer :
FLASK_APP=app flask db upgrade
# Committer le fichier de migration AVEC le changement de modèle.
```

Si on oublie la migration, la CI le détecte. En local/dev, le serveur applique de
toute façon les migrations en attente au prochain démarrage.
