import pytest

from app.modules.identity.device_identity_resolver import DeviceIdentityResolver
from app.shared.exceptions import ValidationDomainError


def test_resolves_from_header():
    resolver = DeviceIdentityResolver(header_value="abc-123", cookie_value=None)
    assert resolver.resolve() == "abc-123"


def test_resolves_from_cookie_when_header_missing():
    resolver = DeviceIdentityResolver(header_value=None, cookie_value="cookie-device-id")
    assert resolver.resolve() == "cookie-device-id"


def test_header_takes_precedence_over_cookie():
    resolver = DeviceIdentityResolver(header_value="header-id", cookie_value="cookie-id")
    assert resolver.resolve() == "header-id"


def test_raises_when_both_missing():
    resolver = DeviceIdentityResolver(header_value=None, cookie_value=None)
    with pytest.raises(ValidationDomainError):
        resolver.resolve()
