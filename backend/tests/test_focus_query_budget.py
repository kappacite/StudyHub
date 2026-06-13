from app.utils.sql_profiler import assert_max_queries


def _seed_decks_with_due_cards(client, headers, n_decks: int):
    for i in range(n_decks):
        deck = client.post(
            "/api/v1/decks", json={"name": f"Deck {i}"}, headers=headers
        ).get_json()
        # Les cartes créées sont dues immédiatement (next_review = now par défaut).
        for j in range(2):
            client.post(
                f"/api/v1/decks/{deck['id']}/cards",
                json={"front": f"Q{j}", "back": f"A{j}"},
                headers=headers,
            )


def test_focus_today_query_count_is_constant_in_number_of_decks(client, auth_headers):
    _seed_decks_with_due_cards(client, auth_headers, 3)
    with assert_max_queries(15) as small:
        client.get("/api/v1/focus/today", headers=auth_headers)

    _seed_decks_with_due_cards(client, auth_headers, 10)
    with assert_max_queries(15) as large:
        resp = client.get("/api/v1/focus/today", headers=auth_headers)

    assert resp.status_code == 200
    # Plus de decks ne doit pas augmenter le nombre de requêtes (pas de N+1).
    assert large.count == small.count
