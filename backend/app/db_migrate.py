"""Migration automatique au démarrage du serveur.

Si le schéma de la base est en retard sur le head Alembic (le « schéma voulu »),
on applique automatiquement les migrations versionnées manquantes (`upgrade head`).

À n'appeler que depuis l'entrypoint serveur (`wsgi.py`), JAMAIS depuis `create_app`
ni une commande `flask db ...` : on évite ainsi d'interférer avec un `downgrade`
manuel ou avec la suite de tests.

En production (gunicorn, 4 workers), l'opération est sérialisée par un verrou
d'avis PostgreSQL pour qu'un seul worker migre à la fois.
"""
import logging

from flask import Flask, current_app

from flask_migrate import upgrade as alembic_upgrade

log = logging.getLogger("studyhub.migrate")

# Clé arbitraire mais stable du verrou d'avis Postgres (sérialise les workers).
_ADVISORY_LOCK_KEY = 7270727


def run_auto_migrations(app: Flask) -> None:
    """Applique les migrations en attente. Idempotent et sûr en concurrence."""
    if app.config.get("TESTING"):
        return

    with app.app_context():
        from app.extensions import db

        dialect = db.engine.dialect.name
        if dialect == "postgresql":
            _upgrade_with_pg_lock(db)
        else:
            # SQLite (dev) : un seul processus, pas de verrou nécessaire.
            _upgrade(db)


def _upgrade_with_pg_lock(db) -> None:
    with db.engine.connect() as conn:
        conn.exec_driver_sql("SELECT pg_advisory_lock(%s)", (_ADVISORY_LOCK_KEY,))
        try:
            _upgrade(db)
        finally:
            conn.exec_driver_sql("SELECT pg_advisory_unlock(%s)", (_ADVISORY_LOCK_KEY,))


def _upgrade(db) -> None:
    before = _current_revision(db)
    alembic_upgrade()  # -> head (no-op si déjà à jour)
    after = _current_revision(db)

    if before == after:
        log.info("Schéma déjà à jour (révision %s).", after)
    else:
        log.info("Migrations appliquées automatiquement : %s -> %s", before, after)


def _current_revision(db):
    from alembic.runtime.migration import MigrationContext

    with db.engine.connect() as conn:
        return MigrationContext.configure(conn).get_current_revision()
