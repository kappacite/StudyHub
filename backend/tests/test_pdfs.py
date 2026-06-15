"""
Tests de l'upload PDF réel : import multipart, listing, renommage, suppression.
"""
import io

# PDF minimal valide (détecté application/pdf par libmagic).
MINIMAL_PDF = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 200 200]>>endobj\n"
    b"trailer<</Root 1 0 R>>\n%%EOF\n"
)


def _upload(client, headers, name="Cours.pdf"):
    data = {"file": (io.BytesIO(MINIMAL_PDF), name)}
    return client.post(
        "/api/v1/pdfs", data=data, headers=headers, content_type="multipart/form-data"
    )


def test_upload_list_rename_delete_pdf(client, auth_headers):
    # Upload
    up = _upload(client, auth_headers, "Mon cours.pdf")
    assert up.status_code == 201, up.json
    pdf_id = up.json["id"]
    assert up.json["name"] == "Mon cours.pdf"
    assert up.json["read_only"] is False

    # Listing : le PDF apparaît
    listing = client.get("/api/v1/pdfs", headers=auth_headers).get_json()["data"]
    assert any(p["id"] == pdf_id for p in listing)

    # Renommage (PUT)
    renamed = client.put(f"/api/v1/pdfs/{pdf_id}", json={"name": "Chapitre 1"}, headers=auth_headers)
    assert renamed.status_code == 200
    assert renamed.json["name"] == "Chapitre 1"

    # Le fichier est servi (stream)
    file_resp = client.get(f"/api/v1/pdfs/{pdf_id}/file", headers=auth_headers)
    assert file_resp.status_code == 200
    assert file_resp.mimetype == "application/pdf"

    # Suppression
    assert client.delete(f"/api/v1/pdfs/{pdf_id}", headers=auth_headers).status_code == 204
    after = client.get("/api/v1/pdfs", headers=auth_headers).get_json()["data"]
    assert all(p["id"] != pdf_id for p in after)


def test_upload_rejects_non_pdf(client, auth_headers):
    data = {"file": (io.BytesIO(b"not a pdf"), "fake.txt")}
    resp = client.post(
        "/api/v1/pdfs", data=data, headers=auth_headers, content_type="multipart/form-data"
    )
    assert resp.status_code == 400
