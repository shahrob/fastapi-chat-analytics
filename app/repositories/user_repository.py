"""
repositories/user_repository.py
────────────────────────────────
Data-access layer for the User model.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """CRUD operations + user-specific lookups for the User model."""

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Return the user matching *username*, or None."""
        return db.query(User).filter(User.username == username).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Return the user matching *email*, or None."""
        return db.query(User).filter(User.email == email).first()

    def get_active_by_username(self, db: Session, username: str) -> Optional[User]:
        """Return an *active* user matching *username*, or None."""
        return (
            db.query(User)
            .filter(User.username == username, User.is_active.is_(True))
            .first()
        )

    def deactivate(self, db: Session, *, user: User) -> User:
        """Set a user as inactive (soft delete)."""
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user


# Module-level singleton — import this from services
user_repository = UserRepository(User)
