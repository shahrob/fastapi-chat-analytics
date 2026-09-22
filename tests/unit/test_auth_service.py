"""
tests/unit/test_auth_service.py
────────────────────────────────
Unit tests for AuthService business logic.
"""

import pytest
from app.services.auth_service import AuthService
from app.core.exceptions import DuplicateUsernameError, DuplicateEmailError, UnauthorizedError
from app.schemas.user import UserCreate


def _make_user_create(**kwargs) -> UserCreate:
    defaults = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "AlicePass1!",
        "full_name": "Alice Example",
    }
    defaults.update(kwargs)
    return UserCreate(**defaults)


class TestAuthServiceRegister:
    def test_register_success(self, db):
        user = AuthService.register(db, _make_user_create())
        assert user.id is not None
        assert user.username == "alice"
        assert user.email == "alice@example.com"
        assert user.hashed_password != "AlicePass1!"  # Should be hashed

    def test_register_duplicate_username(self, db):
        AuthService.register(db, _make_user_create())
        with pytest.raises(DuplicateUsernameError):
            AuthService.register(db, _make_user_create(email="different@example.com"))

    def test_register_duplicate_email(self, db):
        AuthService.register(db, _make_user_create())
        with pytest.raises(DuplicateEmailError):
            AuthService.register(db, _make_user_create(username="different"))


class TestAuthServiceAuthenticate:
    def test_authenticate_success(self, db):
        AuthService.register(db, _make_user_create())
        user = AuthService.authenticate(db, "alice", "AlicePass1!")
        assert user.username == "alice"

    def test_authenticate_wrong_password(self, db):
        AuthService.register(db, _make_user_create())
        with pytest.raises(UnauthorizedError):
            AuthService.authenticate(db, "alice", "WrongPassword!")

    def test_authenticate_unknown_user(self, db):
        with pytest.raises(UnauthorizedError):
            AuthService.authenticate(db, "nobody", "whatever")


class TestAuthServiceToken:
    def test_create_token_returns_string(self, db):
        user = AuthService.register(db, _make_user_create())
        token = AuthService.create_token(user)
        assert isinstance(token, str)
        assert len(token) > 10
