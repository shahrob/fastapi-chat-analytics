from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_active_user
from app.schemas.user import User
from app.schemas.conversation import Conversation, ConversationCreate, ConversationUpdate, ConversationWithMessages
from app.schemas.message import Message, MessageCreate, ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()

# Conversation endpoints
@router.post("/conversations", response_model=Conversation, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new conversation"""
    return ChatService.create_conversation(db=db, conversation=conversation, user=current_user)

@router.get("/conversations", response_model=List[Conversation])
async def get_conversations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's conversations"""
    return ChatService.get_user_conversations(db=db, user=current_user, skip=skip, limit=limit)

@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get conversation with messages"""
    conversation = ChatService.get_conversation(db=db, conversation_id=conversation_id, user=current_user)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get messages for this conversation
    messages = ChatService.get_conversation_messages(db=db, conversation_id=conversation_id, user=current_user)
    
    # Convert to schema with messages
    conversation_dict = {
        "id": conversation.id,
        "title": conversation.title,
        "user_id": conversation.user_id,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "messages": messages
    }
    
    return ConversationWithMessages(**conversation_dict)

@router.put("/conversations/{conversation_id}", response_model=Conversation)
async def update_conversation(
    conversation_id: int,
    conversation_update: ConversationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update conversation"""
    conversation = ChatService.update_conversation(
        db=db, 
        conversation_id=conversation_id, 
        conversation_update=conversation_update, 
        user=current_user
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete conversation"""
    success = ChatService.delete_conversation(db=db, conversation_id=conversation_id, user=current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")

# Message endpoints
@router.get("/conversations/{conversation_id}/messages", response_model=List[Message])
async def get_conversation_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get messages for a conversation"""
    messages = ChatService.get_conversation_messages(
        db=db, 
        conversation_id=conversation_id, 
        user=current_user, 
        skip=skip, 
        limit=limit
    )
    if not messages and skip == 0:  # Check if conversation exists
        conversation = ChatService.get_conversation(db=db, conversation_id=conversation_id, user=current_user)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    
    return messages

@router.post("/conversations/{conversation_id}/messages", response_model=ChatResponse)
async def send_message(
    conversation_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Send a message and get AI response"""
    
    # Verify conversation exists and user owns it
    conversation = ChatService.get_conversation(db=db, conversation_id=conversation_id, user=current_user)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Send message and get AI response
    user_message, ai_message = await ChatService.send_message_with_ai_response(
        db=db,
        message_content=message.content,
        conversation_id=conversation_id,
        user=current_user
    )
    
    return ChatResponse(
        message=user_message.content,
        conversation_id=conversation_id,
        ai_response=ai_message.content
    )

@router.post("/quick-chat", response_model=ChatResponse)
async def quick_chat(
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Quick chat - create conversation if needed and send message"""
    
    conversation_id = chat_request.conversation_id
    
    # Create new conversation if not provided
    if not conversation_id:
        conversation = ChatService.create_conversation(
            db=db,
            conversation=ConversationCreate(title=f"Chat - {chat_request.message[:30]}..."),
            user=current_user
        )
        conversation_id = conversation.id
    
    # Send message and get AI response
    user_message, ai_message = await ChatService.send_message_with_ai_response(
        db=db,
        message_content=chat_request.message,
        conversation_id=conversation_id,
        user=current_user
    )
    
    return ChatResponse(
        message=user_message.content,
        conversation_id=conversation_id,
        ai_response=ai_message.content
    )
