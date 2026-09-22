"""
tests/conftest.py
──────────────────
Shared pytest fixtures for unit and integration tests.

Database isolation strategy
───────────────────────────
Each test gets a fresh in-memory SQLite database so tests are fully
independent and don't leave state behind.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import create_app

# ── In-memory test database ────────────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite://"  # In-memory SQLite

_test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Keep the same in-memory DB across the session
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)


@pytest.fixture(scope="function")
def db():
    """Create all tables, yield a fresh DB session, then drop all tables."""
    Base.metadata.create_all(bind=_test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=_test_engine)


@pytest.fixture(scope="function")
def client(db):
    """HTTP test client with the DB dependency overridden to the test session."""
    app = create_app()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c


@pytest.fixture
def registered_user(client) -> dict:
    """Register a test user and return the response JSON."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def auth_headers(client, registered_user) -> dict:
    """Return Authorization headers for the registered test user."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "TestPass123!"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
