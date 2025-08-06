from openai import AsyncOpenAI
from typing import List, Optional
from app.config import settings

class AIService:
    def __init__(self):
        if settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None

    async def generate_response(self, message: str, conversation_history: Optional[List[dict]] = None) -> str:
        """Generate AI response using OpenAI API"""
        
        if not self.client:
            return "🤖 AI service is not configured. Please set your OpenAI API key in the environment variables."
        
        try:
            # Prepare conversation context
            messages = [
                {
                    "role": "system", 
                    "content": "You are a helpful AI assistant. Provide concise, helpful, and friendly responses."
                }
            ]
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history[-10:]:  # Last 10 messages for context
                    messages.append(msg)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Generate response
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"🤖 Sorry, I'm having trouble processing your request. Error: {str(e)}"

    def format_conversation_history(self, messages: List) -> List[dict]:
        """Format conversation history for AI context"""
        formatted_messages = []
        
        for msg in messages:
            role = "assistant" if msg.is_ai_response else "user"
            formatted_messages.append({
                "role": role,
                "content": msg.content
            })
        
        return formatted_messages

ai_service = AIService()
