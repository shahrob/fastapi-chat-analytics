<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# FastAPI Chat Agent Project Instructions

This is a FastAPI Python project for building a chat agent application with AI integration. When working on this project, please follow these guidelines:

## Code Style & Standards

- Follow PEP 8 Python style guide
- Use type hints for all function parameters and return values
- Use async/await for all database operations and API calls
- Implement proper error handling with custom exceptions
- Use Pydantic models for request/response validation

## Architecture Patterns

- Follow the repository pattern for data access
- Use dependency injection for services
- Implement proper separation of concerns (models, schemas, services, routers)
- Use SQLAlchemy ORM for database operations
- Implement proper JWT authentication and authorization

## FastAPI Best Practices

- Use proper HTTP status codes
- Implement request/response models with Pydantic
- Add proper API documentation with descriptions and examples
- Use FastAPI dependency injection system
- Implement proper error responses

## Database & ORM

- Use SQLAlchemy async sessions
- Implement proper database relationships
- Use Alembic for database migrations
- Follow naming conventions for tables and columns
- Implement proper indexing for performance

## AI Integration

- Use OpenAI API for chat responses
- Implement proper error handling for AI service calls
- Add rate limiting for AI API calls
- Store conversation context appropriately
- Handle AI response streaming for better UX

## WebSocket Implementation

- Use FastAPI WebSocket support
- Implement proper connection management
- Handle WebSocket disconnections gracefully
- Add proper authentication for WebSocket connections
- Implement message broadcasting for group chats

## Security

- Use bcrypt for password hashing
- Implement proper JWT token validation
- Add CORS configuration
- Validate all user inputs
- Implement rate limiting
- Use environment variables for sensitive data

## Testing

- Write unit tests for all business logic
- Use pytest with async support
- Mock external API calls (OpenAI, database)
- Test WebSocket connections
- Implement integration tests for API endpoints

## File Organization

- Keep models in `app/models/`
- Keep Pydantic schemas in `app/schemas/`
- Keep business logic in `app/services/`
- Keep API routes in `app/routers/`
- Keep utilities in `app/utils/`
