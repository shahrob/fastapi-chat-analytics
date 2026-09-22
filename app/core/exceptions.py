"""
core/exceptions.py
──────────────────
Domain-specific exceptions for the application.

These are plain Python exceptions — HTTP mapping happens in the
middleware/error_handler.py so business logic stays free of FastAPI details.
"""


class AppBaseException(Exception):
    """Root exception for all application-level errors."""

    def __init__(self, message: str = "An unexpected error occurred."):
        self.message = message
        super().__init__(self.message)


# ── Auth / User ────────────────────────────────────────────────────────────────
class UnauthorizedError(AppBaseException):
    """Raised when a request cannot be authenticated."""

    def __init__(self, message: str = "Could not validate credentials."):
        super().__init__(message)


class ForbiddenError(AppBaseException):
    """Raised when the authenticated user lacks permission."""

    def __init__(self, message: str = "You do not have permission to perform this action."):
        super().__init__(message)


class UserNotFoundError(AppBaseException):
    """Raised when a user lookup returns no result."""

    def __init__(self, identifier: str = ""):
        msg = f"User not found: {identifier}" if identifier else "User not found."
        super().__init__(msg)


class DuplicateEmailError(AppBaseException):
    """Raised when registering with an already-taken e-mail."""

    def __init__(self, email: str = ""):
        msg = f"Email already registered: {email}" if email else "Email already registered."
        super().__init__(msg)


class DuplicateUsernameError(AppBaseException):
    """Raised when registering with an already-taken username."""

    def __init__(self, username: str = ""):
        msg = f"Username already taken: {username}" if username else "Username already taken."
        super().__init__(msg)


class InactiveUserError(AppBaseException):
    """Raised when an inactive user attempts to log in."""

    def __init__(self):
        super().__init__("This account is inactive.")


# ── Chat / Conversation ────────────────────────────────────────────────────────
class ConversationNotFoundError(AppBaseException):
    """Raised when a conversation does not exist or doesn't belong to the user."""

    def __init__(self, conversation_id: int = 0):
        msg = f"Conversation not found: {conversation_id}" if conversation_id else "Conversation not found."
        super().__init__(msg)


class MessageNotFoundError(AppBaseException):
    """Raised when a message cannot be located."""

    def __init__(self, message_id: int = 0):
        msg = f"Message not found: {message_id}" if message_id else "Message not found."
        super().__init__(msg)


# ── Generic resource ───────────────────────────────────────────────────────────
class NotFoundError(AppBaseException):
    """Generic 404-equivalent exception."""

    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found.")


class ValidationError(AppBaseException):
    """Raised on domain-level validation failures (distinct from Pydantic)."""

    def __init__(self, message: str = "Validation failed."):
        super().__init__(message)


class ServiceUnavailableError(AppBaseException):
    """Raised when an external service (AI, MongoDB, …) is unreachable."""

    def __init__(self, service: str = "Service"):
        super().__init__(f"{service} is currently unavailable.")
