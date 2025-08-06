from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ConversationBase(BaseModel):
    title: str

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(BaseModel):
    title: Optional[str] = None

class Conversation(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ConversationWithMessages(Conversation):
    messages: List["Message"] = []

# Forward reference for Message
from app.schemas.message import Message
ConversationWithMessages.model_rebuild()
