# Backwards-compatibility shim — import from app.core.dependencies instead
from app.core.dependencies import get_current_user, get_current_active_user  # noqa: F401
