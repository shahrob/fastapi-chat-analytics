"""
repositories/conversation_repository.py
────────────────────────────────────────
Data-access layer for the Conversation model.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    """CRUD + user-scoped queries for Conversation."""

    def get_by_user(
        self,
        db: Session,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Conversation]:
        """Return all conversations belonging to *user_id*."""
        return (
            db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc().nullslast(), Conversation.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id_and_user(
        self,
        db: Session,
        *,
        conversation_id: int,
        user_id: int,
    ) -> Optional[Conversation]:
        """Fetch a single conversation, ensuring it belongs to *user_id*."""
        return (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
            .first()
        )

    def count_by_user(self, db: Session, *, user_id: int) -> int:
        """Return the total number of conversations for *user_id*."""
        return (
            db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .count()
        )


# Module-level singleton
conversation_repository = ConversationRepository(Conversation)
