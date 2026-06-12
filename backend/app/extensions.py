import os
import logging
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
from celery import Celery

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
celery_app = Celery("studyhub")


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

# Smart Redis Client that falls back to in-memory dictionary if Redis is not running
logger = logging.getLogger(__name__)

class RedisFallback:
    def __init__(self):
        self._data = {}
        
    def get(self, key):
        return self._data.get(key)
        
    def set(self, key, value, ex=None):
        self._data[key] = value
        return True
        
    def setex(self, key, time, value):
        self._data[key] = value
        return True
        
    def exists(self, key):
        return 1 if key in self._data else 0
        
    def delete(self, key):
        if key in self._data:
            del self._data[key]
            return 1
        return 0

class SmartRedis:
    def __init__(self):
        self._real_redis = None
        self._fallback = RedisFallback()
        self._use_fallback = False
        self._initialized = False

    def init_app(self, app):
        redis_url = app.config.get("REDIS_URL", os.environ.get("REDIS_URL", "redis://localhost:6379/0"))
        try:
            self._real_redis = redis.Redis.from_url(redis_url, decode_responses=True)
            self._real_redis.ping()
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis, using in-memory fallback: {e}")
            self._use_fallback = True
        self._initialized = True

    def _call(self, method_name, *args, **kwargs):
        if not self._initialized:
            return getattr(self._fallback, method_name)(*args, **kwargs)
        if self._use_fallback:
            return getattr(self._fallback, method_name)(*args, **kwargs)
        try:
            return getattr(self._real_redis, method_name)(*args, **kwargs)
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
            logger.warning(f"Redis connection lost, falling back to in-memory: {e}")
            self._use_fallback = True
            return getattr(self._fallback, method_name)(*args, **kwargs)

    def get(self, key):
        return self._call("get", key)

    def set(self, key, value, ex=None):
        return self._call("set", key, value, ex=ex)

    def setex(self, key, time, value):
        return self._call("setex", key, time, value)

    def exists(self, key):
        return self._call("exists", key)

    def delete(self, key):
        return self._call("delete", key)

redis_client = SmartRedis()

