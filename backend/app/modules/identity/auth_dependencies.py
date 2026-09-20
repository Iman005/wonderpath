"""Auth-only dependencies (JWT required, no guest device fallback)."""
from fastapi import Depends, Header

from app.infrastructure.db.models import User
from app.modules.auth.dependencies import get_auth_service
from app.modules.auth.service import AuthService
from app.shared.exceptions import UnauthorizedError


def get_current_user(
    authorization: str | None = Header(default=None),
    service: AuthService = Depends(get_auth_service),
) -> User:
    if not authorization or not authorization.strip().lower().startswith("bearer "):
        raise UnauthorizedError("Missing bearer token.")
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise UnauthorizedError("Missing bearer token.")
    return service.get_user_from_access_token(token)
