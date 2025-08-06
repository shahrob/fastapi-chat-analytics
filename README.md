# FastAPI Chat Agent with Data Analytics

A comprehensive FastAPI application featuring AI chat functionality, MongoDB integration, pandas data analytics, and real-time communication capabilities.

## 🚀 Features

- 🤖 **AI Chat Agent** - OpenAI GPT integration for intelligent conversations
- 🔒 **JWT Authentication** - Secure user authentication and authorization
- 💬 **Real-time Chat** - WebSocket support for instant messaging
- 📊 **Data Analytics** - MongoDB integration with pandas for data analysis
- 📈 **MongoDB Stats** - Complete database statistics and collection analysis
- 🐼 **Pandas Integration** - Advanced data processing and analysis capabilities
- 📝 **Auto Documentation** - Swagger/OpenAPI with interactive API docs
- 🌐 **Network Access** - Accessible from external devices on local network
- 🔄 **Image Processing** - Ready for image conversion capabilities

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.13+
- **Database**: SQLite (local), MongoDB (analytics)
- **Data Processing**: Pandas, NumPy
- **Authentication**: JWT tokens, bcrypt, passlib
- **AI**: OpenAI GPT API
- **Real-time**: WebSockets
- **Async Database**: Motor (MongoDB async driver)
- **Validation**: Pydantic v2

## ⚡ Quick Start

### Prerequisites

- Python 3.13+
- MongoDB (optional, for analytics features)
- OpenAI API Key (optional, for AI responses)

### Installation

1. **Clone and setup virtual environment**

   ```bash
   cd fast-api-python
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Environment configuration**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Access the application**
   - **Local**: http://localhost:8000
   - **Network**: http://192.168.1.7:8000 (replace with your IP)
   - **API Docs**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### 🔐 Authentication

- `POST /auth/register` - User registration
- `POST /auth/login` - User login (returns JWT token)

### 💬 Chat System

- `GET /chat/conversations` - Get user's conversations (🔒 Auth required)
- `POST /chat/conversations` - Create new conversation (🔒 Auth required)
- `GET /chat/conversations/{id}/messages` - Get messages (🔒 Auth required)
- `POST /chat/conversations/{id}/messages` - Send message (🔒 Auth required)
- `WS /ws/{conversation_id}` - WebSocket real-time chat

### 👥 User Management

- `GET /users/me` - Get current user profile (🔒 Auth required)
- `PUT /users/me` - Update user profile (🔒 Auth required)

### 📊 Data Analytics (No Auth Required)

- `GET /data/analytics` - Get chat analytics with pandas (🔒 Auth required)
- `GET /data/analytics/history` - Get analytics history from MongoDB
- `GET /data/export/csv` - Export data to CSV format (🔒 Auth required)
- `POST /data/process` - Process custom data with pandas
- `GET /data/sample` - Generate sample data for testing (🔒 Auth required)
- `GET /data/health` - Check data services health
- `GET /data/dashboard` - Complete analytics dashboard (🔒 Auth required)

### 🗄️ MongoDB Integration

- `GET /data/mongodb/stats` - Complete MongoDB database statistics
- `GET /data/pandas/analyze` - Analyze first MongoDB collection with pandas
- `GET /data/pandas/analyze/{collection_name}` - Analyze specific collection
- `POST /data/pandas/custom-analysis` - Custom pandas analysis on any data

### 🌐 WebSocket

- `WS /ws/{conversation_id}` - Real-time chat communication

## 🏗️ Project Structure

```
fast-api-python/
├── app/
│   ├── __init__.py
│   ├── config.py               # Application settings
│   ├── database.py             # SQLite database setup
│   ├── mongodb.py              # MongoDB async connection
│   ├── dependencies.py         # FastAPI dependencies
│   │
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py             # User model
│   │   ├── conversation.py     # Conversation model
│   │   └── message.py          # Message model
│   │
│   ├── schemas/                # Pydantic models
│   │   ├── __init__.py
│   │   ├── user.py             # User schemas
│   │   ├── conversation.py     # Conversation schemas
│   │   ├── message.py          # Message schemas
│   │   └── auth.py             # Auth schemas
│   │
│   ├── routers/                # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication routes
│   │   ├── chat.py             # Chat functionality
│   │   ├── users.py            # User management
│   │   ├── websocket.py        # WebSocket handlers
│   │   └── data.py             # Data analytics endpoints
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py     # Authentication service
│   │   ├── chat_service.py     # Chat business logic
│   │   ├── ai_service.py       # OpenAI integration
│   │   └── data_service.py     # Pandas & MongoDB analytics
│   │
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       └── websocket_manager.py # WebSocket connection manager
│
├── alembic/                    # Database migrations
├── static/                     # Static files (HTML, CSS, JS)
├── venv/                       # Virtual environment
├── main.py                     # FastAPI application entry point
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .env                        # Your environment variables
├── chatapp.db                  # SQLite database file
└── README.md                   # This file
```

## ⚙️ Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=sqlite:///./chatapp.db

# MongoDB (Optional - for analytics)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=mail-cub

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI (Optional - for AI responses)
OPENAI_API_KEY=your-openai-api-key-here

# Redis (Optional)
REDIS_URL=redis://localhost:6379

# App Settings
DEBUG=True
HOST=0.0.0.0
PORT=8000

# CORS (Modify with your network IP)
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8000","http://127.0.0.1:8000","http://192.168.1.7:8000","*"]
```

## 🔧 Usage Examples

### 1. Register and Login

```bash
# Register
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'

# Login
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=testuser&password=password123"
```

### 2. Data Analytics (No Auth Required)

```bash
# Get MongoDB stats
curl "http://localhost:8000/data/mongodb/stats"

# Process custom data with pandas
curl -X POST "http://localhost:8000/data/process" \
     -H "Content-Type: application/json" \
     -d '[{"name": "Alice", "age": 25, "salary": 50000}, {"name": "Bob", "age": 30, "salary": 60000}]'

# Analyze MongoDB collection
curl "http://localhost:8000/data/pandas/analyze/clients"
```

### 3. Chat Functionality

```bash
# Start conversation (requires auth token)
curl -X POST "http://localhost:8000/chat/conversations" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title": "My AI Chat"}'

# Send message
curl -X POST "http://localhost:8000/chat/conversations/1/messages" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"content": "Hello, how can you help me?"}'
```

## 📊 Data Analytics Features

### MongoDB Analytics

- **Database Statistics**: Complete MongoDB database info, collection stats, document counts
- **Collection Analysis**: Individual collection statistics with sample documents
- **Server Metrics**: MongoDB server uptime, connection statistics

### Pandas Integration

- **Data Processing**: Advanced data analysis with pandas and NumPy
- **Statistical Analysis**: Descriptive statistics, correlations, outlier detection
- **Data Visualization Prep**: Histogram and chart data generation
- **CSV Export**: Export processed data to CSV format
- **Custom Analysis**: Process any JSON data with pandas operations

### Real-time Analytics

- **Chat Analytics**: Message counts, user activity, conversation insights
- **Historical Data**: Analytics history stored in MongoDB
- **Dashboard Data**: Comprehensive dashboard endpoints

## 🌐 Network Access

The application is configured to accept connections from:

- **Localhost**: `http://localhost:8000`
- **Network Devices**: `http://YOUR_IP:8000` (e.g., `http://192.168.1.7:8000`)
- **Mobile Devices**: Access from phones/tablets on same network

## 🧪 Development

### Run Tests

```bash
pytest  # When test files are added
```

### Database Operations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

### Check Application Health

```bash
# Health check
curl http://localhost:8000/data/health

# MongoDB connection status
curl http://localhost:8000/data/mongodb/stats
```

## 🔮 Future Enhancements

- 📷 **Image Processing**: Convert between image formats (JPEG, PNG, WebP, etc.)
- 📈 **Advanced Analytics**: More sophisticated data analysis features
- 🔄 **Real-time Dashboard**: Live data visualization
- 🛡️ **Enhanced Security**: Rate limiting, advanced authentication
- 📱 **Mobile API**: Mobile-optimized endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

If you encounter any issues:

1. Check the logs for error details
2. Ensure all dependencies are installed
3. Verify your `.env` configuration
4. Check network connectivity for external access
5. Open an issue on GitHub

---

**Built with ❤️ using FastAPI, MongoDB, and Pandas**
