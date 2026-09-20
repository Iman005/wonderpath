"""
JwtIdentityResolver — resolves the authenticated user id from a bearer JWT.

Used when the client sends `Authorization: Bearer <access_token>` after
Google sign-in. The token is issued by AuthService and contains the User.id
as `sub`.
"""
import jwt

from app.core.config import get_settings
from app.modules.identity.interfaces import IIdentityResolver
from app.shared.exceptions import UnauthorizedError

settings = get_settings()


class JwtIdentityResolver(IIdentityResolver):
    def __init__(self, bearer_token: str | None) -> None:
        self._bearer_token = bearer_token

    def resolve(self) -> str:
        if not self._bearer_token:
            raise UnauthorizedError("Missing bearer token.")

        token = self._bearer_token.removeprefix("Bearer ").strip()
        if not token:
            raise UnauthorizedError("Missing bearer token.")

        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        except jwt.PyJWTError as exc:
            raise UnauthorizedError("Invalid or expired session token.") from exc

        user_id = payload.get("sub")
        if not user_id or not isinstance(user_id, str):
            raise UnauthorizedError("Invalid session token payload.")
        return user_id
