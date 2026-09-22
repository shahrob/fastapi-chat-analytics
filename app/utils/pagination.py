"""
utils/pagination.py
────────────────────
Reusable pagination helpers.

Usage in endpoints
------------------
    from app.utils.pagination import PaginationParams, paginate

    @router.get("/items")
    async def list_items(
        pagination: PaginationParams = Depends(),
        db: Session = Depends(get_db),
    ):
        items = db.query(Item).all()
        return paginate(items, pagination)
"""

from typing import Any, Dict, Generic, List, TypeVar
from fastapi import Query
from pydantic import BaseModel

from app.core.config import settings

T = TypeVar("T")


class PaginationParams:
    """FastAPI-injectable pagination query parameters."""

    def __init__(
        self,
        page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
        page_size: int = Query(
            default=settings.DEFAULT_PAGE_SIZE,
            ge=1,
            le=settings.MAX_PAGE_SIZE,
            description="Number of items per page",
        ),
    ):
        self.page = page
        self.page_size = page_size

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated API response envelope."""

    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


def paginate(items: List[Any], params: PaginationParams, total: int) -> Dict[str, Any]:
    """Build a paginated response dict from a list and params."""
    total_pages = (total + params.page_size - 1) // params.page_size
    return {
        "items": items,
        "total": total,
        "page": params.page,
        "page_size": params.page_size,
        "total_pages": total_pages,
        "has_next": params.page < total_pages,
        "has_prev": params.page > 1,
    }
