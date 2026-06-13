from app.utils.sql_profiler import assert_max_queries


def _seed(client, headers, n_decks: int, n_cards: int):
    for i in range(n_decks):
        deck = client.post(
            "/api/v1/decks", json={"name": f"Deck {i}"}, headers=headers
        ).get_json()
        for j in range(n_cards):
            client.post(
                f"/api/v1/decks/{deck['id']}/cards",
                json={"front": f"Q{j}", "back": f"A{j}"},
                headers=headers,
            )


def test_decks_list_uses_bounded_queries_and_correct_count(client, auth_headers):
    _seed(client, auth_headers, n_decks=6, n_cards=4)

    with assert_max_queries(8):
        resp = client.get("/api/v1/decks?per_page=20", headers=auth_headers)

    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert len(data) == 6
    # card_count correct, sans charger les cartes en ORM.
    assert all(d["card_count"] == 4 for d in data)


def test_decks_list_query_count_is_constant_in_number_of_decks(client, auth_headers):
    _seed(client, auth_headers, n_decks=3, n_cards=2)
    with assert_max_queries(8) as small:
        client.get("/api/v1/decks?per_page=20", headers=auth_headers)

    _seed(client, auth_headers, n_decks=12, n_cards=2)
    with assert_max_queries(8) as large:
        client.get("/api/v1/decks?per_page=20", headers=auth_headers)

    # Le nombre de requêtes ne grandit pas avec le nombre de decks (pas de N+1).
    assert large.count == small.count
