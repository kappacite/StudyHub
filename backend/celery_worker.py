from app import create_app
from app.extensions import celery_app

# Create the Flask application instance, which registers all blueprints and configures Celery
flask_app = create_app()
