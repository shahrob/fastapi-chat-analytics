"""
db/session.py
─────────────
SQLAlchemy engine, session factory, and declarative base.

All ORM models must import ``Base`` from here to be picked up by Alembic.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# ── Engine ─────────────────────────────────────────────────────────────────────
_connect_args = (
    {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=_connect_args,
    # Enable connection pool pre-ping to detect stale connections (PostgreSQL)
    pool_pre_ping=True,
)

# ── Session factory ────────────────────────────────────────────────────────────
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ── Declarative base ───────────────────────────────────────────────────────────
Base = declarative_base()


# ── FastAPI dependency ─────────────────────────────────────────────────────────
def get_db():
    """Yield a SQLAlchemy session and guarantee it is closed afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
