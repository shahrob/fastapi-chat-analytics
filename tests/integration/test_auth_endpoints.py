"""
tests/integration/test_auth_endpoints.py
─────────────────────────────────────────
Integration tests for the /api/v1/auth endpoints.

These tests exercise the full HTTP stack: routing → service → DB.
"""

import pytest


BASE = "/api/v1/auth"

VALID_USER = {
    "username": "integrationuser",
    "email": "integration@example.com",
    "password": "IntegrationPass1!",
    "full_name": "Integration Test",
}


class TestRegister:
    def test_register_returns_201(self, client):
        response = client.post(f"{BASE}/register", json=VALID_USER)
        assert response.status_code == 201

    def test_register_response_shape(self, client):
        response = client.post(f"{BASE}/register", json=VALID_USER)
        data = response.json()
        assert "id" in data
        assert data["username"] == VALID_USER["username"]
        assert data["email"] == VALID_USER["email"]
        assert "password" not in data
        assert "hashed_password" not in data

    def test_register_duplicate_username_returns_400(self, client):
        client.post(f"{BASE}/register", json=VALID_USER)
        response = client.post(
            f"{BASE}/register",
            json={**VALID_USER, "email": "other@example.com"},
        )
        assert response.status_code == 400

    def test_register_duplicate_email_returns_400(self, client):
        client.post(f"{BASE}/register", json=VALID_USER)
        response = client.post(
            f"{BASE}/register",
            json={**VALID_USER, "username": "otherusername"},
        )
        assert response.status_code == 400

    def test_register_missing_fields_returns_422(self, client):
        response = client.post(f"{BASE}/register", json={"username": "incomplete"})
        assert response.status_code == 422


class TestLogin:
    def test_login_returns_token(self, client):
        client.post(f"{BASE}/register", json=VALID_USER)
        response = client.post(
            f"{BASE}/login",
            data={"username": VALID_USER["username"], "password": VALID_USER["password"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password_returns_401(self, client):
        client.post(f"{BASE}/register", json=VALID_USER)
        response = client.post(
            f"{BASE}/login",
            data={"username": VALID_USER["username"], "password": "WrongPassword!"},
        )
        assert response.status_code == 401

    def test_login_unknown_user_returns_401(self, client):
        response = client.post(
            f"{BASE}/login",
            data={"username": "nobody", "password": "whatever"},
        )
        assert response.status_code == 401


class TestProtectedEndpoints:
    def test_get_profile_without_token_returns_403(self, client):
        response = client.get("/api/v1/users/me")
        assert response.status_code in (401, 403)

    def test_get_profile_with_valid_token(self, client, auth_headers):
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"
