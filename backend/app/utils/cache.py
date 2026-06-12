import json
from functools import wraps
from typing import Optional
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import redis_client

def cache_route(timeout=300):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                user_id = get_jwt_identity()
            except Exception:
                user_id = "anon"
            
            # Construct a unique cache key for the route, query params, and user
            query_str = request.query_string.decode("utf-8")
            cache_key = f"route_cache:{request.path}:{query_str}:{user_id}"
            
            # Try to get from cache
            cached_val = redis_client.get(cache_key)
            if cached_val is not None:
                try:
                    data, status_code = json.loads(cached_val)
                    return jsonify(data), status_code
                except Exception:
                    pass
            
            # Execute the actual controller function
            response = f(*args, **kwargs)
            
            # Extract data and status code
            status_code = 200
            if isinstance(response, tuple):
                res_obj, status_code = response
            else:
                res_obj = response
                
            # Retrieve JSON data from Flask response object if possible
            if hasattr(res_obj, "get_json"):
                json_data = res_obj.get_json()
            elif hasattr(res_obj, "json"):
                json_data = res_obj.json
            else:
                json_data = res_obj
                
            # Store in Redis cache
            try:
                redis_client.setex(cache_key, timeout, json.dumps((json_data, status_code)))
            except Exception:
                pass
                
            return response
        return decorated_function
    return decorator

def invalidate_stats_cache(user_id: int, deck_id: Optional[int] = None):
    """Invalidates the stats cache for a specific user, and optionally a specific deck."""
    redis_client.delete(f"route_cache:/api/v1/stats/overview::{user_id}")
    redis_client.delete(f"route_cache:/api/v1/stats/heatmap::{user_id}")
    redis_client.delete(f"route_cache:/api/v1/stats/dashboard::{user_id}")
    if deck_id is not None:
        redis_client.delete(f"route_cache:/api/v1/stats/decks/{deck_id}::{user_id}")
