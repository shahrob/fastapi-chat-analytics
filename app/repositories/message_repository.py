"""
repositories/message_repository.py
────────────────────────────────────
Data-access layer for the Message model.
"""

from typing import List

from sqlalchemy.orm import Session

from app.models.message import Message
from app.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    """CRUD + conversation-scoped queries for Message."""

    def get_by_conversation(
        self,
        db: Session,
        *,
        conversation_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Message]:
        """Return messages for *conversation_id*, ordered chronologically."""
        return (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_conversation(self, db: Session, *, conversation_id: int) -> int:
        """Return total number of messages in a conversation."""
        return (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .count()
        )

    def get_ai_messages_by_conversation(
        self,
        db: Session,
        *,
        conversation_id: int,
    ) -> List[Message]:
        """Return only AI-generated messages for a conversation."""
        return (
            db.query(Message)
            .filter(
                Message.conversation_id == conversation_id,
                Message.is_ai_response.is_(True),
            )
            .order_by(Message.created_at.asc())
            .all()
        )

    def get_recent_context(
        self,
        db: Session,
        *,
        conversation_id: int,
        limit: int = 10,
    ) -> List[Message]:
        """Return the most recent *limit* messages for AI context building."""
        return (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()[::-1]  # reverse to chronological order
        )


# Module-level singleton
message_repository = MessageRepository(Message)
