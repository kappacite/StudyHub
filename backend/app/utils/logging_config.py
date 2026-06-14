"""Configuration du logging applicatif.

Sans handler explicite, les loggers applicatifs (`logging.getLogger(__name__)`,
`request_logger`) n'ont aucun handler : sous gunicorn, `logger.exception()` dans
`handle_generic_exception` n'émet donc RIEN dans la sortie du conteneur. Résultat :
des 500 totalement invisibles dans les logs (cf. [[project-celery-asyncresult-gotcha]],
diagnostic qui a coûté une heure). On pose ici un handler sur le logger racine pour
que tout remonte sur stdout.
"""
import logging
import sys

_HANDLER_NAME = "studyhub_stream"


def configure_logging(app):
    """Pose (une seule fois) un handler stdout sur le logger racine.

    Idempotent : `create_app` est appelé plusieurs fois (un worker gunicorn par
    process, ou de nombreux appels au sein d'un même process de test) — on ne pose
    qu'un unique handler nommé. Sauté en mode test pour ne pas interférer avec la
    capture de logs de pytest.
    """
    if app.config.get("TESTING"):
        return

    level_name = str(app.config.get("LOG_LEVEL", "INFO")).upper()
    level = getattr(logging, level_name, logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)

    if any(getattr(h, "name", None) == _HANDLER_NAME for h in root.handlers):
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.name = _HANDLER_NAME
    handler.setFormatter(
        logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
    )
    root.addHandler(handler)
