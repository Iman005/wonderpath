"""FastAPI dependency wiring for the Auth module."""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.repository import AuthRepository
from app.modules.auth.service import AuthService


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(AuthRepository(db))
