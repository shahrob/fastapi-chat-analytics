"""
services/chat_service.py
─────────────────────────
Business logic for conversations and messages.
DB access is delegated to the repository layer.
"""

from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.exceptions import ConversationNotFoundError
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.repositories.conversation_repository import conversation_repository
from app.repositories.message_repository import message_repository
from app.schemas.conversation import ConversationCreate, ConversationUpdate
from app.schemas.message import MessageCreate
from app.services.ai_service import ai_service


class ChatService:
    """Manages conversations and chat messages, including AI responses."""

    # ── Conversations ──────────────────────────────────────────────────────────
    @staticmethod
    def create_conversation(
        db: Session, conversation: ConversationCreate, user: User
    ) -> Conversation:
        """Create a new conversation owned by *user*."""
        return conversation_repository.create(
            db,
            obj_in={"title": conversation.title, "user_id": user.id},
        )

    @staticmethod
    def get_user_conversations(
        db: Session, user: User, skip: int = 0, limit: int = 100
    ) -> List[Conversation]:
        """Return paginated conversations for *user*."""
        return conversation_repository.get_by_user(
            db, user_id=user.id, skip=skip, limit=limit
        )

    @staticmethod
    def get_conversation(
        db: Session, conversation_id: int, user: User
    ) -> Optional[Conversation]:
        """Return a conversation only if it belongs to *user*; else None."""
        return conversation_repository.get_by_id_and_user(
            db, conversation_id=conversation_id, user_id=user.id
        )

    @staticmethod
    def update_conversation(
        db: Session,
        conversation_id: int,
        conversation_update: ConversationUpdate,
        user: User,
    ) -> Optional[Conversation]:
        """Apply partial updates to a conversation. Returns None if not found."""
        conv = conversation_repository.get_by_id_and_user(
            db, conversation_id=conversation_id, user_id=user.id
        )
        if not conv:
            return None
        return conversation_repository.update(
            db,
            db_obj=conv,
            obj_in=conversation_update.model_dump(exclude_unset=True),
        )

    @staticmethod
    def delete_conversation(db: Session, conversation_id: int, user: User) -> bool:
        """Delete a conversation. Returns False if it doesn't exist / wrong owner."""
        conv = conversation_repository.get_by_id_and_user(
            db, conversation_id=conversation_id, user_id=user.id
        )
        if not conv:
            return False
        conversation_repository.delete(db, id=conversation_id)
        return True

    # ── Messages ───────────────────────────────────────────────────────────────
    @staticmethod
    def create_message(
        db: Session,
        message: MessageCreate,
        conversation_id: int,
        user: User,
        is_ai_response: bool = False,
    ) -> Message:
        """Persist a single message."""
        return message_repository.create(
            db,
            obj_in={
                "content": message.content,
                "conversation_id": conversation_id,
                "user_id": user.id,
                "is_ai_response": is_ai_response,
            },
        )

    @staticmethod
    def get_conversation_messages(
        db: Session,
        conversation_id: int,
        user: User,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Message]:
        """Return messages for a conversation — verifies user ownership first."""
        conv = conversation_repository.get_by_id_and_user(
            db, conversation_id=conversation_id, user_id=user.id
        )
        if not conv:
            return []
        return message_repository.get_by_conversation(
            db, conversation_id=conversation_id, skip=skip, limit=limit
        )

    @staticmethod
    async def send_message_with_ai_response(
        db: Session,
        message_content: str,
        conversation_id: int,
        user: User,
    ) -> Tuple[Message, Message]:
        """Persist the user message, call the AI service, and persist the reply."""
        # Persist user message
        user_message = ChatService.create_message(
            db,
            MessageCreate(content=message_content),
            conversation_id,
            user,
            is_ai_response=False,
        )

        # Build context from recent history (excludes the just-created message)
        recent = message_repository.get_recent_context(
            db, conversation_id=conversation_id, limit=10
        )
        # The last item is the message we just created; exclude it for context
        history = ai_service.format_conversation_history(recent[:-1])

        # Generate AI reply
        ai_content = await ai_service.generate_response(message_content, history)

        # Persist AI message
        ai_message = ChatService.create_message(
            db,
            MessageCreate(content=ai_content),
            conversation_id,
            user,
            is_ai_response=True,
        )

        return user_message, ai_message


chat_service = ChatService()
