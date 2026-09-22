"""
api/v1/router.py
─────────────────
Central APIRouter that aggregates all v1 endpoint routers.

Import this in ``app/main.py`` and mount at ``settings.API_V1_STR``.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, chat, users, websocket, data

api_router = APIRouter()

api_router.include_router(auth.router,      prefix="/auth",      tags=["Authentication"])
api_router.include_router(users.router,     prefix="/users",     tags=["Users"])
api_router.include_router(chat.router,      prefix="/chat",      tags=["Chat"])
api_router.include_router(websocket.router, prefix="/ws",        tags=["WebSocket"])
api_router.include_router(data.router,      prefix="/data",      tags=["Data & Analytics"])
