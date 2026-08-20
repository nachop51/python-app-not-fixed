import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def client():
    # Fresh in-memory DB per test so tests don't share state.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def register(client, username="alice", password="pw", is_admin=False):
    return client.post("/register", json={
        "username": username,
        "email": f"{username}@finance.co",
        "password": password,
        "is_admin": is_admin,
    })


def token(client, username="alice", password="pw"):
    r = client.post("/login", json={"username": username, "password": password})
    return r.json()["access_token"]


def auth(tok):
    return {"Authorization": f"Bearer {tok}"}
