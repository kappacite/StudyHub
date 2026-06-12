from app import create_app
from app.extensions import db
from app.models.binder import Binder
from app.models.user import User
import json

app = create_app("testing")
client = app.test_client()

with app.app_context():
    db.create_all()
    # Create test user
    user = User(email="test@example.com", username="testuser")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    user_id = user.id

# Connect user to get auth headers
response = client.post("/api/v1/auth/login", json={
    "email": "test@example.com",
    "password": "password123"
})
print("Login Status:", response.status_code)
token = response.json["access_token"]
headers = {"Authorization": f"Bearer {token}"}

with app.app_context():
    # Create binder
    binder = Binder(user_id=user_id, name="Classeur Gynéco")
    db.session.add(binder)
    db.session.commit()
    db.session.refresh(binder)
    binder_id = binder.id

# Create group
resp = client.post("/api/v1/groups", json={
    "name": "Groupe Santé"
}, headers=headers)
print("Create Group Status:", resp.status_code)
group_id = resp.json["id"]

# Share binder
share_resp = client.post(f"/api/v1/groups/{group_id}/binders", json={
    "binder_id": binder_id,
    "permission": "read"
}, headers=headers)
print("Share Binder Status:", share_resp.status_code)
if share_resp.status_code != 200:
    print("Response JSON:", share_resp.json)
