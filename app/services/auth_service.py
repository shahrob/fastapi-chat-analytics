"""
services/auth_service.py
─────────────────────────
Authentication business logic.

Security primitives (hashing, JWT) live in ``app.core.security``.
DB access is delegated to ``UserRepository``.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.exceptions import (
    DuplicateEmailError,
    DuplicateUsernameError,
    UnauthorizedError,
)
from app.models.user import User
from app.repositories.user_repository import user_repository
from app.schemas.user import UserCreate


class AuthService:
    """Handles user registration and authentication workflows."""

    @staticmethod
    def register(db: Session, user_in: UserCreate) -> User:
        """
        Register a new user.

        Raises
        ------
        DuplicateUsernameError
            If the username is already taken.
        DuplicateEmailError
            If the email is already registered.
        """
        if user_repository.get_by_username(db, user_in.username):
            raise DuplicateUsernameError(user_in.username)
        if user_repository.get_by_email(db, user_in.email):
            raise DuplicateEmailError(user_in.email)

        return user_repository.create(
            db,
            obj_in={
                "username": user_in.username,
                "email": user_in.email,
                "full_name": user_in.full_name,
                "hashed_password": get_password_hash(user_in.password),
            },
        )

    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> User:
        """
        Verify credentials and return the User.

        Raises
        ------
        UnauthorizedError
            If the username does not exist or the password is incorrect.
        """
        user = user_repository.get_by_username(db, username)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Incorrect username or password.")
        return user

    @staticmethod
    def create_token(user: User) -> str:
        """Generate a JWT access token for *user*."""
        return create_access_token(data={"sub": user.username})

    # ── Kept for backwards-compatibility (used by dependencies.py) ─────────────
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        return user_repository.get_by_username(db, username)

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return user_repository.get_by_email(db, email)

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        return AuthService.register(db, user)


auth_service = AuthService()
