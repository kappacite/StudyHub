"""Entrypoint WSGI de production (gunicorn) et serveur de dev.

C'est ici — et nulle part ailleurs — que l'on applique automatiquement les
migrations en attente au démarrage. Les commandes `flask db ...` continuent
d'utiliser `FLASK_APP=app` (la factory pure), sans auto-migration.

Usage :
  - prod  : gunicorn ... wsgi:app
  - dev   : FLASK_APP=wsgi:app flask run
"""
from app import create_app
from app.db_migrate import run_auto_migrations

app = create_app()
run_auto_migrations(app)
