from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
import json
import asyncio

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.user import User
from app.services.chat_service import ChatService
from app.schemas.message import MessageCreate

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, conversation_id: int):
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []
        self.active_connections[conversation_id].append(websocket)

    def disconnect(self, websocket: WebSocket, conversation_id: int):
        if conversation_id in self.active_connections:
            self.active_connections[conversation_id].remove(websocket)
            if not self.active_connections[conversation_id]:
                del self.active_connections[conversation_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_to_conversation(self, message: str, conversation_id: int):
        if conversation_id in self.active_connections:
            for connection in self.active_connections[conversation_id]:
                try:
                    await connection.send_text(message)
                except:
                    # Remove disconnected connections
                    self.active_connections[conversation_id].remove(connection)

manager = ConnectionManager()

@router.websocket("/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    conversation_id: int,
    token: str = None
):
    """WebSocket endpoint for real-time chat"""
    
    # For demo purposes, we'll accept connections without strict token validation
    # In production, implement proper WebSocket authentication
    
    await manager.connect(websocket, conversation_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
                message_content = message_data.get("message", "")
                
                if not message_content:
                    await manager.send_personal_message(
                        json.dumps({"error": "Message content is required"}),
                        websocket
                    )
                    continue
                
                # For demo purposes, echo the message back
                # In production, integrate with your chat service and database
                response = {
                    "type": "user_message",
                    "message": message_content,
                    "timestamp": "2025-01-29T12:00:00Z",
                    "conversation_id": conversation_id
                }
                
                # Broadcast user message to all connections in this conversation
                await manager.broadcast_to_conversation(
                    json.dumps(response),
                    conversation_id
                )
                
                # Simulate AI response (replace with actual AI service call)
                await asyncio.sleep(1)  # Simulate processing time
                
                ai_response = {
                    "type": "ai_response",
                    "message": f"🤖 I received your message: '{message_content}'. This is a demo WebSocket response.",
                    "timestamp": "2025-01-29T12:00:01Z",
                    "conversation_id": conversation_id
                }
                
                # Broadcast AI response
                await manager.broadcast_to_conversation(
                    json.dumps(ai_response),
                    conversation_id
                )
                
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    json.dumps({"error": "Invalid JSON format"}),
                    websocket
                )
            except Exception as e:
                await manager.send_personal_message(
                    json.dumps({"error": f"Error processing message: {str(e)}"}),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id)
        
        # Notify other users in the conversation
        await manager.broadcast_to_conversation(
            json.dumps({
                "type": "user_disconnected",
                "message": "A user left the conversation",
                "conversation_id": conversation_id
            }),
            conversation_id
        )
