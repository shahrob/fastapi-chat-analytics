"""
DEPRECATED: This file is kept for backwards compatibility.
Please use `run.py` as the application entry point.

    python run.py            # development
    uvicorn run:app ...      # production
"""
# Re-export `app` from the new entry point so `uvicorn main:app` still works.
from run import app  # noqa: F401

import warnings
warnings.warn(
    "main.py at the project root is deprecated. Use run.py instead.",
    DeprecationWarning,
    stacklevel=1,
)
