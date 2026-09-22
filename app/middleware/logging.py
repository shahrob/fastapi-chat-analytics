"""
middleware/logging.py
──────────────────────
Request / response logging middleware.

Logs: method, path, status code, and wall-clock duration for every request.
"""

import logging
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("app.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Starlette middleware that logs each HTTP request with timing info."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start = time.perf_counter()

        # Attach request ID for downstream traceability
        request.state.request_id = request_id

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "[%s] %s %s → %s  (%.1f ms)",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        # Expose request ID in response header for client-side correlation
        response.headers["X-Request-ID"] = request_id
        return response
