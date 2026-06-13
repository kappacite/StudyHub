import time
import logging
from flask import request, g
from app.utils.sql_profiler import current_request_query_count

logger = logging.getLogger("request_logger")

def register_request_logger(app):
    slow_ms = app.config.get("SLOW_REQUEST_MS", 500)

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
        duration_ms = (time.time() - start_time) * 1000 if start_time is not None else 0.0
        queries = current_request_query_count()

        # Une requête lente (ou avec beaucoup de requêtes SQL = N+1 probable)
        # est loguée en WARNING pour ressortir dans les logs.
        log = logger.warning if duration_ms >= slow_ms else logger.info
        log(
            "%s %s %s %s %.1fms queries=%d",
            request.remote_addr,
            request.method,
            request.path,
            response.status_code,
            duration_ms,
            queries,
        )
        return response
