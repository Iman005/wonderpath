"""
FastAPI dependency that exposes the current owner identity to any route.

Identity resolution policy (auth transition):
- If `Authorization: Bearer <jwt>` is present → JwtIdentityResolver (logged-in
  user id becomes Trip.owner_device_id).
- Otherwise → DeviceIdentityResolver (anonymous guest UUID from X-Device-Id /
  cookie), so existing anonymous trips and API tests keep working during the
  transition. The frontend now requires Google sign-in for /app routes, but the
  backend still accepts device ids for legacy clients.

Phone/SMS auth can later add another resolver branch here without touching
trip services.
"""
from fastapi import Cookie, Header

from app.core.config import get_settings
from app.modules.identity.device_identity_resolver import DeviceIdentityResolver
from app.modules.identity.jwt_identity_resolver import JwtIdentityResolver

settings = get_settings()


def get_current_device_id(
    authorization: str | None = Header(default=None),
    x_device_id: str | None = Header(default=None, alias=settings.DEVICE_ID_HEADER_NAME),
    wanderpath_device_id: str | None = Cookie(default=None, alias=settings.DEVICE_ID_COOKIE_NAME),
) -> str:
    if authorization and authorization.strip().lower().startswith("bearer "):
        return JwtIdentityResolver(authorization).resolve()

    return DeviceIdentityResolver(header_value=x_device_id, cookie_value=wanderpath_device_id).resolve()
