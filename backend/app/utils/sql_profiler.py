"""Compteur de requêtes SQL — instrumentation des performances.

Un listener SQLAlchemy global incrémente un compteur à chaque exécution de
requête. Deux usages :
  - en requête HTTP : le compte est posé sur `flask.g` et logué par le
    request_logger (détection des N+1) ;
  - en test : le context manager `assert_max_queries(n)` borne le nombre de
    requêtes d'un bloc (tests « budget de requêtes »).

Coût négligeable (un incrément d'entier par requête).
"""
import contextvars

from flask import g, has_request_context
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Compteur indépendant du contexte Flask (utilisé par les tests / le bench).
_query_counter: contextvars.ContextVar[int] = contextvars.ContextVar(
    "sql_query_count", default=0
)


@event.listens_for(Engine, "before_cursor_execute")
def _count_query(conn, cursor, statement, parameters, context, executemany):
    _query_counter.set(_query_counter.get() + 1)
    if has_request_context():
        g._sql_query_count = getattr(g, "_sql_query_count", 0) + 1


def current_request_query_count() -> int:
    """Nombre de requêtes SQL exécutées pour la requête HTTP courante."""
    if has_request_context():
        return getattr(g, "_sql_query_count", 0)
    return 0


class assert_max_queries:
    """Context manager de test : échoue si le bloc dépasse `max_queries`.

    Exemple :
        with assert_max_queries(3):
            client.get("/api/v1/decks", headers=auth_headers)
    """

    def __init__(self, max_queries: int):
        self.max_queries = max_queries
        self.count = 0
        self._start = 0

    def __enter__(self) -> "assert_max_queries":
        self._start = _query_counter.get()
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.count = _query_counter.get() - self._start
        if exc_type is None and self.count > self.max_queries:
            raise AssertionError(
                f"{self.count} requêtes SQL exécutées, budget = {self.max_queries}"
            )
        return False
