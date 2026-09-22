"""
repositories/base.py
─────────────────────
Generic CRUD base repository.

Subclass this and pass the SQLAlchemy model as a type argument to get
``get``, ``get_multi``, ``create``, ``update``, and ``delete`` for free.

Example
-------
    class UserRepository(BaseRepository[User]):
        pass
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy.orm import Session

from app.db.session import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic repository providing standard CRUD operations.

    Parameters
    ----------
    model:
        The SQLAlchemy ORM model class.
    """

    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    # ── Read ───────────────────────────────────────────────────────────────────
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Fetch a single record by primary key."""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        """Fetch a paginated list of records."""
        return db.query(self.model).offset(skip).limit(limit).all()

    def count(self, db: Session) -> int:
        """Return total number of records."""
        return db.query(self.model).count()

    # ── Write ──────────────────────────────────────────────────────────────────
    def create(self, db: Session, *, obj_in: Dict[str, Any]) -> ModelType:
        """Create and persist a new record from a plain dict."""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Dict[str, Any],
    ) -> ModelType:
        """Apply a partial update to an existing record."""
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: Any) -> Optional[ModelType]:
        """Delete a record by primary key; returns the deleted object or None."""
        obj = self.get(db, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
