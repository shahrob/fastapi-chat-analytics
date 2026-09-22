"""
services/ai_service.py
───────────────────────
OpenAI integration for generating chat responses.
"""

import logging
from typing import List, Optional

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Thin wrapper around the OpenAI async client."""

    def __init__(self) -> None:
        if settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI client initialised (model=%s)", settings.OPENAI_MODEL)
        else:
            self.client = None
            logger.warning(
                "OPENAI_API_KEY is not set — AI responses will be stubbed."
            )

    async def generate_response(
        self,
        message: str,
        conversation_history: Optional[List[dict]] = None,
    ) -> str:
        """Generate a chat completion from OpenAI.

        Falls back to a friendly stub if the API key is not configured.
        """
        if not self.client:
            return (
                "🤖 AI service is not configured. "
                "Please set OPENAI_API_KEY in your environment variables."
            )

        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful AI assistant. "
                        "Provide concise, helpful, and friendly responses."
                    ),
                }
            ]
            if conversation_history:
                messages.extend(conversation_history[-10:])
            messages.append({"role": "user", "content": message})

            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()

        except Exception as exc:
            logger.error("OpenAI API error: %s", exc)
            return f"🤖 Sorry, I'm having trouble processing your request. Error: {exc}"

    def format_conversation_history(self, messages: List) -> List[dict]:
        """Convert ORM Message objects to OpenAI message dicts."""
        return [
            {
                "role": "assistant" if msg.is_ai_response else "user",
                "content": msg.content,
            }
            for msg in messages
        ]


ai_service = AIService()
