"""
app/main.py
────────────
FastAPI application factory.

Call ``create_app()`` to get a fully configured FastAPI instance.
The root entry point (``run.py``) calls this and passes the result to Uvicorn.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import Base, engine
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.api.v1.router import api_router
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.error_handler import DomainExceptionMiddleware


# ── Lifespan (replaces deprecated on_event) ───────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle handler."""
    import logging
    logger = logging.getLogger(__name__)

    # Startup
    setup_logging()
    Base.metadata.create_all(bind=engine)
    await connect_to_mongo()
    logger.info("🚀 %s v%s started [env=%s]", settings.PROJECT_NAME, settings.VERSION, settings.APP_ENV)

    yield  # Application is running

    # Shutdown
    await close_mongo_connection()
    logger.info("🛑 %s shutting down.", settings.PROJECT_NAME)


def create_app() -> FastAPI:
    """Construct and return the configured FastAPI application."""

    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
    )

    # ── Middleware (order matters — added last, executed first) ────────────────
    app.add_middleware(DomainExceptionMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── API routes ─────────────────────────────────────────────────────────────
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # ── Static files ───────────────────────────────────────────────────────────
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # ── Root & health endpoints ────────────────────────────────────────────────
    @app.get("/", tags=["Root"])
    async def root():
        return {
            "project": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.APP_ENV,
            "docs": f"{settings.API_V1_STR}/docs",
            "redoc": f"{settings.API_V1_STR}/redoc",
            "api_prefix": settings.API_V1_STR,
        }

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "healthy", "service": settings.PROJECT_NAME}

    return app
