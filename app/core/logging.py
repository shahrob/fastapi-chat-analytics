"""
core/logging.py
───────────────
Centralised logging configuration.

• Development: human-readable coloured output
• Production:  JSON-structured output (machine-parseable by log aggregators)

Call ``setup_logging()`` once at application startup (in ``app/main.py``).
"""

import logging
import sys
from app.core.config import settings


def setup_logging() -> None:
    """Configure root logger based on the current APP_ENV and LOG_LEVEL."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    if settings.is_production:
        # JSON-structured format for production log aggregators (e.g. Datadog, CloudWatch)
        fmt = (
            '{"time":"%(asctime)s","level":"%(levelname)s",'
            '"logger":"%(name)s","message":"%(message)s"}'
        )
    else:
        # Pretty format for local development
        fmt = "%(asctime)s  [%(levelname)-8s]  %(name)s — %(message)s"

    logging.basicConfig(
        level=log_level,
        format=fmt,
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
        force=True,
    )

    # Silence noisy third-party loggers in non-debug environments
    if not settings.DEBUG:
        for noisy in ("uvicorn.access", "sqlalchemy.engine", "motor"):
            logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        "Logging initialised | env=%s level=%s", settings.APP_ENV, settings.LOG_LEVEL
    )


def get_logger(name: str) -> logging.Logger:
    """Convenience wrapper — returns a named logger."""
    return logging.getLogger(name)
