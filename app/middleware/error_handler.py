"""
middleware/error_handler.py
────────────────────────────
Global exception handler middleware.

Maps domain exceptions (from app.core.exceptions) to appropriate HTTP
responses so that routers and services never need to import FastAPI HTTP
primitives directly.
"""

import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import (
    AppBaseException,
    ConversationNotFoundError,
    DuplicateEmailError,
    DuplicateUsernameError,
    ForbiddenError,
    InactiveUserError,
    MessageNotFoundError,
    NotFoundError,
    ServiceUnavailableError,
    UnauthorizedError,
    UserNotFoundError,
    ValidationError,
)

logger = logging.getLogger(__name__)

# ── Exception → HTTP status code mapping ───────────────────────────────────────
_STATUS_MAP = {
    UnauthorizedError: 401,
    ForbiddenError: 403,
    UserNotFoundError: 404,
    ConversationNotFoundError: 404,
    MessageNotFoundError: 404,
    NotFoundError: 404,
    DuplicateEmailError: 409,
    DuplicateUsernameError: 409,
    InactiveUserError: 400,
    ValidationError: 422,
    ServiceUnavailableError: 503,
}


class DomainExceptionMiddleware(BaseHTTPMiddleware):
    """Convert domain exceptions into structured JSON error responses."""

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except AppBaseException as exc:
            status_code = _STATUS_MAP.get(type(exc), 500)
            logger.warning(
                "Domain exception [%s]: %s", type(exc).__name__, exc.message
            )
            return JSONResponse(
                status_code=status_code,
                content={"detail": exc.message, "type": type(exc).__name__},
            )
        except Exception as exc:
            logger.exception("Unhandled exception: %s", exc)
            return JSONResponse(
                status_code=500,
                content={"detail": "An internal server error occurred.", "type": "InternalServerError"},
            )
