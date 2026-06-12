def _create_binder(client, headers, name="Classeur"):
    resp = client.post("/api/v1/binders", json={"name": name}, headers=headers)
    assert resp.status_code == 201
    return resp.json


def test_get_binder_by_id(client, auth_headers):
    created = _create_binder(client, auth_headers, "Maths")
    resp = client.get(f"/api/v1/binders/{created['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json["name"] == "Maths"


def test_update_binder_renames(client, auth_headers):
    created = _create_binder(client, auth_headers, "Ancien")
    resp = client.put(
        f"/api/v1/binders/{created['id']}",
        json={"name": "Nouveau"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json["name"] == "Nouveau"


def test_delete_binder(client, auth_headers):
    created = _create_binder(client, auth_headers, "ASupprimer")
    resp = client.delete(f"/api/v1/binders/{created['id']}", headers=auth_headers)
    assert resp.status_code == 204

    follow_up = client.get(f"/api/v1/binders/{created['id']}", headers=auth_headers)
    assert follow_up.status_code in (403, 404)


def test_get_all_binders_flat(client, auth_headers):
    _create_binder(client, auth_headers, "A")
    _create_binder(client, auth_headers, "B")
    resp = client.get("/api/v1/binders?all=true", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json["data"]) >= 2


def test_toggle_visibility_requires_is_public_field(client, auth_headers):
    created = _create_binder(client, auth_headers, "Vis")
    resp = client.patch(
        f"/api/v1/binders/{created['id']}/visibility",
        json={},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_toggle_visibility_makes_binder_publicly_accessible(client, auth_headers):
    created = _create_binder(client, auth_headers, "Public")
    resp = client.patch(
        f"/api/v1/binders/{created['id']}/visibility",
        json={"is_public": True},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json["is_public"] is True

    # Accès public sans authentification.
    public = client.get(f"/api/v1/binders/public/{created['id']}")
    assert public.status_code == 200
    assert public.json["id"] == created["id"]


def test_get_public_binder_not_found(client):
    resp = client.get("/api/v1/binders/public/inexistant-uuid")
    assert resp.status_code == 404
