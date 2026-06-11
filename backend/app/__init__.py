import os
from flask import Flask
from flask_cors import CORS
from app.config import config_by_name
from app.extensions import db, jwt, migrate, limiter

def create_app(config_name=None):
    flask_app = Flask(__name__)
    CORS(flask_app, resources={r"/api/.*": {"origins": "*", "allow_headers": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]}})
    
    if not config_name:
        config_name = os.environ.get("FLASK_ENV", "development")
        
    flask_app.config.from_object(config_by_name[config_name])
    
    # Initialisation des extensions
    db.init_app(flask_app)
    jwt.init_app(flask_app)
    migrate.init_app(flask_app, db)
    limiter.init_app(flask_app)
    
    # Assurer que le dossier d'upload existe
    os.makedirs(flask_app.config["UPLOAD_FOLDER"], exist_ok=True)
    
    # Enregistrement des middlewares et des routes (à faire après leur création)
    with flask_app.app_context():
        # Forcer l'enregistrement des callbacks JWT
        import app.middlewares.auth_middleware
        
        # Enregistrement des gestionnaires d'erreurs globaux
        from app.middlewares.error_handler import register_error_handlers
        register_error_handlers(flask_app)
        
        # Enregistrement du logger de requêtes
        from app.middlewares.request_logger import register_request_logger
        register_request_logger(flask_app)
        
        # Enregistrement des blueprints
        from app.api.v1.auth import auth_bp
        from app.api.v1.users import users_bp
        from app.api.v1.binders import binders_bp
        from app.api.v1.decks import decks_bp
        from app.api.v1.flashcards import flashcards_bp, flashcards_global_bp
        from app.api.v1.notes import notes_bp
        from app.api.v1.diagrams import diagrams_bp
        from app.api.v1.pdfs import pdfs_bp
        from app.api.v1.stats import stats_bp
        from app.api.v1.health import health_bp
        from app.api.v1.blurting import blurting_bp
        from app.api.v1.packages import packages_bp
        from app.api.v1.tags import tags_bp
        from app.api.v1.focus import focus_bp
        
        flask_app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
        flask_app.register_blueprint(users_bp, url_prefix="/api/v1/users")
        flask_app.register_blueprint(binders_bp, url_prefix="/api/v1/binders")
        flask_app.register_blueprint(decks_bp, url_prefix="/api/v1/decks")
        flask_app.register_blueprint(flashcards_bp, url_prefix="/api/v1/decks/<int:deck_id>/cards")
        flask_app.register_blueprint(flashcards_global_bp, url_prefix="/api/v1/flashcards")
        flask_app.register_blueprint(notes_bp, url_prefix="/api/v1/notes")
        flask_app.register_blueprint(diagrams_bp, url_prefix="/api/v1/diagrams")
        flask_app.register_blueprint(pdfs_bp, url_prefix="/api/v1/pdfs")
        flask_app.register_blueprint(stats_bp, url_prefix="/api/v1/stats")
        flask_app.register_blueprint(health_bp, url_prefix="/api/v1/health")
        flask_app.register_blueprint(blurting_bp, url_prefix="/api/v1/blurting")
        flask_app.register_blueprint(packages_bp, url_prefix="/api/v1/packages")
        flask_app.register_blueprint(tags_bp, url_prefix="/api/v1/tags")
        flask_app.register_blueprint(focus_bp, url_prefix="/api/v1/focus")
        
        # Import all models so Alembic can detect them and db.create_all() works
        import app.models.user
        import app.models.binder
        import app.models.deck
        import app.models.flashcard
        import app.models.note
        import app.models.diagram
        import app.models.pdf_document
        import app.models.study_session
        import app.models.tag

        # En dev/test : créer les tables directement sans migrations
        if flask_app.config.get("DEBUG") or flask_app.config.get("TESTING"):
            db.create_all()
        else:
            # En production : auto-migration au démarrage
            from flask_migrate import upgrade as flask_db_upgrade, stamp as flask_db_stamp
            from sqlalchemy import inspect
            try:
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                
                if tables:
                    # La base de données existe et contient des tables
                    if "alembic_version" not in tables:
                        # Cas où la base a été créée sans Alembic (avant les migrations)
                        # On la tamponne sur la version initiale de référence
                        flask_app.logger.info("Base de données existante sans Alembic. Tamponnage sur la version 06f0ddaea360...")
                        flask_db_stamp(revision="06f0ddaea360")
                
                # Exécuter les migrations en attente
                flask_db_upgrade()
                flask_app.logger.info("Migrations de base de données appliquées automatiquement avec succès.")
            except Exception as e:
                flask_app.logger.error(f"Erreur lors de l'exécution automatique des migrations: {e}")
            
    return flask_app
