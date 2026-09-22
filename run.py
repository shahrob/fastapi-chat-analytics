"""
run.py
───────
Root entry point for the FastAPI Chat Analytics application.

Development:
    python run.py

Production (Uvicorn directly):
    uvicorn run:app --host 0.0.0.0 --port 8000 --workers 4

Docker / Gunicorn + Uvicorn workers:
    gunicorn run:app -k uvicorn.workers.UvicornWorker
"""

import uvicorn

from app.main import create_app
from app.core.config import settings

# Build the application instance — used by Uvicorn / Gunicorn import
app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "run:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
