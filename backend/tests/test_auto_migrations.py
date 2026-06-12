from sqlalchemy import inspect


def test_run_auto_migrations_upgrades_a_fresh_database(tmp_path):
    """Sur une base vierge, run_auto_migrations doit appliquer toute la chaîne
    de migrations jusqu'au head (tables créées + alembic_version renseignée)."""
    from app import create_app
    from app.db_migrate import run_auto_migrations
    from app.extensions import db

    app = create_app("development")
    # Base SQLite jetable, isolée du reste de la suite.
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{tmp_path / 'fresh.db'}"

    run_auto_migrations(app)

    with app.app_context():
        tables = set(inspect(db.engine).get_table_names())

    assert "users" in tables
    assert "binders" in tables
    assert "alembic_version" in tables


def test_run_auto_migrations_is_skipped_under_testing(tmp_path):
    """En mode TESTING, l'auto-migration ne doit rien faire (les tests gèrent
    leur schéma via db.create_all)."""
    from app import create_app
    from app.db_migrate import run_auto_migrations
    from app.extensions import db

    app = create_app("testing")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{tmp_path / 'skip.db'}"

    run_auto_migrations(app)

    with app.app_context():
        tables = set(inspect(db.engine).get_table_names())

    # Aucune migration appliquée -> pas de table alembic_version.
    assert "alembic_version" not in tables
