import os
import pytest
from app import create_app
from app.extensions import db
from app.models.user import User

@pytest.fixture(scope="session")
def app():
    app = create_app("testing")

    # SQLite en mémoire par défaut (rapide, isolé). Si TEST_DATABASE_URL est défini
    # (job CI "Backend · tests (PostgreSQL)"), on tourne sur PostgreSQL pour attraper
    # les divergences SQLite/PG invisibles autrement (ex. func.date() -> date vs str).
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("TEST_DATABASE_URL", "sqlite://")

    # Désactiver le rate limiting pour les tests
    app.config["RATELIMIT_ENABLED"] = False

    return app

@pytest.fixture(scope="function", autouse=True)
def clean_db(app):
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="function")
def client(app):
    return app.test_client()

@pytest.fixture(scope="function")
def test_user(app):
    with app.app_context():
        user = User(email="test@example.com", username="testuser")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        
        # Recharger depuis la session
        db.session.refresh(user)
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "password": "password123"
        }

@pytest.fixture(scope="function")
def auth_headers(client, test_user):
    # Connecter l'utilisateur pour avoir le token
    response = client.post("/api/v1/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    token = response.json["access_token"]
    return {
        "Authorization": f"Bearer {token}"
    }
