from app.utils.sql_profiler import assert_max_queries


def _seed_notes(client, headers, n: int, prefix: str):
    for i in range(n):
        client.post(
            "/api/v1/notes",
            json={"title": f"chimie {prefix}{i}", "content": "chimie organique"},
            headers=headers,
        )


def test_search_query_count_is_constant_in_number_of_results(client, auth_headers):
    _seed_notes(client, auth_headers, 4, "a")
    with assert_max_queries(12) as small:
        client.get("/api/v1/search?q=chimie&types=note", headers=auth_headers)

    _seed_notes(client, auth_headers, 10, "b")
    with assert_max_queries(12) as large:
        resp = client.get("/api/v1/search?q=chimie&types=note", headers=auth_headers)

    assert resp.status_code == 200
    # Les tags des résultats sont eager-loadés : le nb de requêtes ne grandit pas.
    assert large.count == small.count
