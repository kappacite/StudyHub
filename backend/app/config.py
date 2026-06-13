import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_key_change_me_in_production_123456")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev_jwt_secret_key_change_me_in_production_123456")
    
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 900)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRES", 2592000)))
    
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.join(os.path.abspath(os.path.dirname(__file__)), "../uploads"))
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 52428800))  # 50 MB
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # Seuil (ms) au-delà duquel une requête HTTP est loguée en WARNING.
    SLOW_REQUEST_MS = int(os.environ.get("SLOW_REQUEST_MS", 500))

    # Redis (cache de routes partagé entre workers + broker Celery).
    # En prod, doit pointer vers un Redis accessible par TOUS les workers gunicorn,
    # sinon le cache retombe sur un dict en mémoire PAR PROCESSUS (non partagé) —
    # un WARNING est alors logué au démarrage (cf. extensions.SmartRedis).
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # Celery Config
    CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", 
        "sqlite:///" + os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../studyhub_dev.db")
    )

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite://"
    )
    # Désactive le rate limiting de façon déterministe pour les tests.
    # Lu par limiter.init_app() (contrairement au réglage post-création du conftest),
    # ce qui évite des 429 en cours de suite selon FLASK_ENV / l'ordre des tests.
    RATELIMIT_ENABLED = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=5)  # Court pour les tests
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=10)
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_BROKER_URL = "memory://"
    CELERY_RESULT_BACKEND = "cache+memory://"
    CELERY_TASK_STORE_EAGER_RESULT = True




class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
}
