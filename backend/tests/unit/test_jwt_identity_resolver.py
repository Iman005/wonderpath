from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.core.config import get_settings
from app.modules.identity.jwt_identity_resolver import JwtIdentityResolver
from app.shared.exceptions import UnauthorizedError

settings = get_settings()


def _token(sub: str = "user-1", *, expired: bool = False) -> str:
    exp = datetime.now(UTC) + (timedelta(days=-1) if expired else timedelta(days=1))
    payload = {"sub": sub, "exp": exp}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def test_resolves_user_id_from_bearer_token():
    token = _token("user-abc")
    resolver = JwtIdentityResolver(f"Bearer {token}")
    assert resolver.resolve() == "user-abc"


def test_accepts_raw_token_without_bearer_prefix():
    token = _token("user-raw")
    resolver = JwtIdentityResolver(token)
    assert resolver.resolve() == "user-raw"


def test_raises_when_token_missing():
    resolver = JwtIdentityResolver(None)
    with pytest.raises(UnauthorizedError):
        resolver.resolve()


def test_raises_when_token_expired():
    token = _token("user-old", expired=True)
    resolver = JwtIdentityResolver(f"Bearer {token}")
    with pytest.raises(UnauthorizedError):
        resolver.resolve()


def test_raises_when_token_invalid():
    resolver = JwtIdentityResolver("Bearer not-a-jwt")
    with pytest.raises(UnauthorizedError):
        resolver.resolve()
