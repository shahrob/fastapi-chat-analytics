from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import logging

from app.config import settings
from app.database import engine, Base
from app.mongodb import connect_to_mongo, close_mongo_connection
from app.routers import auth, chat, users, websocket, data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="FastAPI Chat Agent",
    description="A complete chat agent application with AI integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])
app.include_router(data.router, prefix="/data", tags=["data"])

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialize database tables and connections on startup"""
    # Create SQLite tables
    Base.metadata.create_all(bind=engine)
    
    # Connect to MongoDB
    await connect_to_mongo()
    
    logger.info("Application started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    # Close MongoDB connection
    await close_mongo_connection()
    
    logger.info("Application shutting down")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main chat interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FastAPI Chat Agent</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .chat-box { border: 1px solid #ddd; height: 400px; overflow-y: scroll; padding: 10px; margin-bottom: 10px; }
            .input-box { width: 70%; padding: 10px; }
            .send-btn { width: 20%; padding: 10px; background: #007bff; color: white; border: none; cursor: pointer; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user-message { background: #e3f2fd; text-align: right; }
            .ai-message { background: #f5f5f5; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 FastAPI Chat Agent</h1>
            <div id="chat-box" class="chat-box"></div>
            <input type="text" id="message-input" class="input-box" placeholder="Type your message..." />
            <button onclick="sendMessage()" class="send-btn">Send</button>
            <div style="margin-top: 20px;">
                <h3>API Documentation</h3>
                <p><a href="/docs" target="_blank">📖 Swagger UI</a> | <a href="/redoc" target="_blank">📋 ReDoc</a></p>
            </div>
        </div>

        <script>
            const chatBox = document.getElementById('chat-box');
            const messageInput = document.getElementById('message-input');
            
            function addMessage(content, isUser = false) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
                messageDiv.textContent = content;
                chatBox.appendChild(messageDiv);
                chatBox.scrollTop = chatBox.scrollHeight;
            }
            
            async function sendMessage() {
                const message = messageInput.value.trim();
                if (!message) return;
                
                addMessage(message, true);
                messageInput.value = '';
                
                try {
                    // This is a simple demo - in production, you'd handle authentication
                    addMessage("🤖 Chat agent is not connected. Please use the API endpoints with authentication.", false);
                } catch (error) {
                    addMessage("❌ Error sending message", false);
                }
            }
            
            messageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            // Welcome message
            addMessage("👋 Welcome! This is a demo interface. Use the API endpoints for full functionality.", false);
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "FastAPI Chat Agent is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
