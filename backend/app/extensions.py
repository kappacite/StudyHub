import os
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

# Set larger default limits for development to avoid blocking auto-save
is_dev = os.environ.get("FLASK_ENV", "development") == "development"
default_limits = ["2000 per day", "500 per hour"] if is_dev else ["200 per day", "50 per hour"]

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=default_limits
)

@limiter.request_filter
def exempt_options_requests():
    return request.method == "OPTIONS"
