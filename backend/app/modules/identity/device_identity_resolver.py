"""
DeviceIdentityResolver — resolves an anonymous Device ID.

Resolution order:
1. `X-Device-Id` request header (set by the frontend API client on every
   request, once it has generated/loaded a UUID from localStorage).
2. `wanderpath_device_id` cookie, as a fallback for clients that don't set
   the header explicitly.

If neither is present, this raises — device id generation for a brand
new client is expected to happen client-side (UUID in localStorage) and
sent immediately; the backend does not silently mint identities, so that
`Trip.owner_device_id` is always the value the client actually holds.
"""
from app.core.config import get_settings
from app.modules.identity.interfaces import IIdentityResolver
from app.shared.exceptions import ValidationDomainError

settings = get_settings()


class DeviceIdentityResolver(IIdentityResolver):
    def __init__(self, header_value: str | None, cookie_value: str | None) -> None:
        self._header_value = header_value
        self._cookie_value = cookie_value

    def resolve(self) -> str:
        device_id = self._header_value or self._cookie_value
        if not device_id:
            raise ValidationDomainError(
                f"Missing device identity. Send the '{settings.DEVICE_ID_HEADER_NAME}' header."
            )
        return device_id
