"""
api/v1/endpoints/auth.py
─────────────────────────
Authentication endpoints: register and login.
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import DuplicateEmailError, DuplicateUsernameError, UnauthorizedError
from app.db.session import get_db
from app.schemas.user import User, UserCreate, Token
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account."""
    try:
        return AuthService.register(db, user)
    except DuplicateUsernameError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
    except DuplicateEmailError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticate with username + password and receive a JWT access token."""
    try:
        user = AuthService.authenticate(db, form_data.username, form_data.password)
    except UnauthorizedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = AuthService.create_token(user)
    return {"access_token": access_token, "token_type": "bearer"}
