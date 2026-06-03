import time
import logging
from flask import request, g

logger = logging.getLogger("request_logger")

def register_request_logger(app):
    @app.before_request
    def before_request():
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        if request.path.startswith("/api/v1/health"):
            return response
            
        try:
            start_time = g.start_time
        except AttributeError:
            start_time = None
        duration = time.time() - start_time if start_time is not None else 0.0
        
        logger.info(
            "%s %s %s %s %.2fms",
            request.remote_addr,
            request.method,
            request.path,
            response.status_code,
            duration * 1000
        )
        return response
