import os
from flask import Flask
from flask_cors import CORS
from app.config import config_by_name
from app.extensions import db, jwt, migrate, limiter

def create_app(config_name=None):
    flask_app = Flask(__name__)
    CORS(flask_app, resources={r"/api/.*": {"origins": "*", "allow_headers": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}})
    
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
        from app.api.v1.flashcards import flashcards_bp
        from app.api.v1.notes import notes_bp
        from app.api.v1.diagrams import diagrams_bp
        from app.api.v1.pdfs import pdfs_bp
        from app.api.v1.stats import stats_bp
        from app.api.v1.health import health_bp
        
        flask_app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
        flask_app.register_blueprint(users_bp, url_prefix="/api/v1/users")
        flask_app.register_blueprint(binders_bp, url_prefix="/api/v1/binders")
        flask_app.register_blueprint(decks_bp, url_prefix="/api/v1/decks")
        flask_app.register_blueprint(flashcards_bp, url_prefix="/api/v1/decks/<int:deck_id>/cards")
        flask_app.register_blueprint(notes_bp, url_prefix="/api/v1/notes")
        flask_app.register_blueprint(diagrams_bp, url_prefix="/api/v1/diagrams")
        flask_app.register_blueprint(pdfs_bp, url_prefix="/api/v1/pdfs")
        flask_app.register_blueprint(stats_bp, url_prefix="/api/v1/stats")
        flask_app.register_blueprint(health_bp, url_prefix="/api/v1/health")
        
        # Auto-create tables in development mode if they don't exist
        if flask_app.config.get("DEBUG") or flask_app.config.get("TESTING"):
            # Import models to ensure they are registered
            import app.models.user
            import app.models.binder
            import app.models.deck
            import app.models.flashcard
            import app.models.note
            import app.models.diagram
            import app.models.pdf_document
            import app.models.study_session
            db.create_all()
            
    return flask_app
