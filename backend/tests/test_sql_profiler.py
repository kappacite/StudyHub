import pytest

from app.utils.sql_profiler import assert_max_queries


def test_assert_max_queries_counts_executed_queries(client, auth_headers):
    # Une création de deck implique au moins un INSERT.
    with assert_max_queries(50) as counter:
        resp = client.post(
            "/api/v1/decks",
            json={"name": "Bench"},
            headers=auth_headers,
        )
    assert resp.status_code == 201
    assert counter.count > 0


def test_assert_max_queries_raises_when_budget_exceeded(client, auth_headers):
    # Budget volontairement impossible (0) -> doit lever.
    with pytest.raises(AssertionError):
        with assert_max_queries(0):
            client.get("/api/v1/decks", headers=auth_headers)
