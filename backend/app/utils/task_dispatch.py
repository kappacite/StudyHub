import logging

logger = logging.getLogger(__name__)


def dispatch_or_run(task, *args, **kwargs):
    """Envoie une tâche Celery via le broker, avec repli synchrone.

    Si le broker / result-backend Redis est injoignable (typiquement en
    développement sans Redis ni worker), exécute la tâche en synchrone (inline)
    et renvoie son résultat — au lieu de remonter une 500. La production, qui
    dispose d'un Redis et d'un worker, conserve le comportement asynchrone.

    Calqué sur l'esprit de `SmartRedis` (cf. `app.extensions`) : dégradation
    gracieuse plutôt qu'échec dur quand l'infra optionnelle est absente.

    Returns:
        tuple[str, Any]:
          - ("async", AsyncResult) : tâche mise en file, à sonder via /tasks/<id>.
          - ("sync", result)       : tâche déjà exécutée, résultat disponible.
    """
    try:
        async_result = task.delay(*args, **kwargs)
    except Exception as exc:  # broker / result-backend Redis injoignable
        logger.warning(
            "Broker Celery injoignable (%s) — exécution inline de %s",
            exc, task.name,
        )
        # L'appel direct passe par ContextTask : un contexte applicatif est déjà
        # actif (requête en cours), il est réutilisé. Toute erreur réelle de la
        # tâche se propage normalement (et sera traduite par error_handler).
        return "sync", task(*args, **kwargs)
    return "async", async_result
