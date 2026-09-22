"""
api/v1/endpoints/websocket.py
──────────────────────────────
WebSocket endpoint for real-time chat.
"""

import asyncio
import json
import logging
from typing import Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.chat_service import ChatService

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    """Manages active WebSocket connections grouped by conversation ID."""

    def __init__(self) -> None:
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, conversation_id: int) -> None:
        await websocket.accept()
        self.active_connections.setdefault(conversation_id, []).append(websocket)
        logger.info("WS connected: conversation_id=%s", conversation_id)

    def disconnect(self, websocket: WebSocket, conversation_id: int) -> None:
        connections = self.active_connections.get(conversation_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections:
            self.active_connections.pop(conversation_id, None)
        logger.info("WS disconnected: conversation_id=%s", conversation_id)

    async def send(self, message: str, websocket: WebSocket) -> None:
        await websocket.send_text(message)

    async def broadcast(self, message: str, conversation_id: int) -> None:
        for ws in list(self.active_connections.get(conversation_id, [])):
            try:
                await ws.send_text(message)
            except Exception:
                self.active_connections.get(conversation_id, []).remove(ws)


manager = ConnectionManager()


@router.websocket("/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: int) -> None:
    """
    WebSocket endpoint for real-time chat in a conversation.

    Expects JSON messages: ``{"message": "<text>"}``
    Responds with ``{"type": "user_message"|"ai_response"|"user_disconnected", ...}``

    Note: Implement proper token-based authentication before production use.
    """
    await manager.connect(websocket, conversation_id)

    try:
        while True:
            raw = await websocket.receive_text()

            try:
                data = json.loads(raw)
                content = data.get("message", "").strip()

                if not content:
                    await manager.send(
                        json.dumps({"error": "Message content is required"}), websocket
                    )
                    continue

                # Echo user message to all participants
                await manager.broadcast(
                    json.dumps({
                        "type": "user_message",
                        "message": content,
                        "conversation_id": conversation_id,
                    }),
                    conversation_id,
                )

                # Simulate AI processing delay then respond
                await asyncio.sleep(0.8)
                await manager.broadcast(
                    json.dumps({
                        "type": "ai_response",
                        "message": f"🤖 Received: '{content}'. (WebSocket demo — integrate AI service for production.)",
                        "conversation_id": conversation_id,
                    }),
                    conversation_id,
                )

            except json.JSONDecodeError:
                await manager.send(json.dumps({"error": "Invalid JSON"}), websocket)
            except Exception as exc:
                logger.exception("WS error: %s", exc)
                await manager.send(json.dumps({"error": str(exc)}), websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id)
        await manager.broadcast(
            json.dumps({
                "type": "user_disconnected",
                "message": "A user left the conversation",
                "conversation_id": conversation_id,
            }),
            conversation_id,
        )
