from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.schemas.conversation import ConversationCreate, ConversationUpdate
from app.schemas.message import MessageCreate
from app.services.ai_service import ai_service

class ChatService:
    @staticmethod
    def create_conversation(db: Session, conversation: ConversationCreate, user: User) -> Conversation:
        """Create a new conversation"""
        db_conversation = Conversation(
            title=conversation.title,
            user_id=user.id
        )
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)
        return db_conversation

    @staticmethod
    def get_user_conversations(db: Session, user: User, skip: int = 0, limit: int = 100) -> List[Conversation]:
        """Get user's conversations"""
        return db.query(Conversation).filter(
            Conversation.user_id == user.id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_conversation(db: Session, conversation_id: int, user: User) -> Optional[Conversation]:
        """Get conversation by ID (user must own it)"""
        return db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id
        ).first()

    @staticmethod
    def update_conversation(db: Session, conversation_id: int, conversation_update: ConversationUpdate, user: User) -> Optional[Conversation]:
        """Update conversation"""
        conversation = ChatService.get_conversation(db, conversation_id, user)
        if not conversation:
            return None
        
        for field, value in conversation_update.dict(exclude_unset=True).items():
            setattr(conversation, field, value)
        
        db.commit()
        db.refresh(conversation)
        return conversation

    @staticmethod
    def delete_conversation(db: Session, conversation_id: int, user: User) -> bool:
        """Delete conversation"""
        conversation = ChatService.get_conversation(db, conversation_id, user)
        if not conversation:
            return False
        
        db.delete(conversation)
        db.commit()
        return True

    @staticmethod
    def create_message(db: Session, message: MessageCreate, conversation_id: int, user: User, is_ai_response: bool = False) -> Message:
        """Create a new message"""
        db_message = Message(
            content=message.content,
            conversation_id=conversation_id,
            user_id=user.id,
            is_ai_response=is_ai_response
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message

    @staticmethod
    def get_conversation_messages(db: Session, conversation_id: int, user: User, skip: int = 0, limit: int = 100) -> List[Message]:
        """Get messages for a conversation"""
        # First verify user owns the conversation
        conversation = ChatService.get_conversation(db, conversation_id, user)
        if not conversation:
            return []
        
        return db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).offset(skip).limit(limit).all()

    @staticmethod
    async def send_message_with_ai_response(db: Session, message_content: str, conversation_id: int, user: User) -> tuple[Message, Message]:
        """Send message and get AI response"""
        
        # Create user message
        user_message = ChatService.create_message(
            db, 
            MessageCreate(content=message_content), 
            conversation_id, 
            user, 
            is_ai_response=False
        )
        
        # Get conversation history for AI context
        messages = ChatService.get_conversation_messages(db, conversation_id, user, limit=10)
        conversation_history = ai_service.format_conversation_history(messages[:-1])  # Exclude the just-created message
        
        # Generate AI response
        ai_response_content = await ai_service.generate_response(message_content, conversation_history)
        
        # Create AI response message
        ai_message = ChatService.create_message(
            db,
            MessageCreate(content=ai_response_content),
            conversation_id,
            user,
            is_ai_response=True
        )
        
        return user_message, ai_message
