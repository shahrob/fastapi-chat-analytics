# Backwards-compatibility shim — import from app.db.session instead
from app.db.session import Base, engine, SessionLocal, get_db  # noqa: F401
