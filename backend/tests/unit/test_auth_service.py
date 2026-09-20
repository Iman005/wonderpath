"""AuthService password register/login — repository mocked."""
from unittest.mock import MagicMock

import pytest

from app.modules.auth.passwords import hash_password, verify_password
from app.modules.auth.service import AuthService
from app.shared.exceptions import UnauthorizedError, ValidationDomainError


def _service(existing=None):
    repo = MagicMock()
    repo.get_by_email.return_value = existing
    repo.create_user.side_effect = lambda **kwargs: MagicMock(id="user-1", **kwargs)
    return AuthService(repo), repo


def test_register_rejects_duplicate_email():
    service, repo = _service(existing=MagicMock())
    with pytest.raises(ValidationDomainError, match="از قبل وجود دارد"):
        service.register("Ada@example.com", "password1")
    repo.create_user.assert_not_called()


def test_register_creates_hashed_password():
    service, repo = _service()
    result = service.register("ada@example.com", "password1", "آدا")
    saved = repo.create_user.call_args.kwargs
    assert saved["email"] == "ada@example.com"
    assert saved["display_name"] == "آدا"
    assert verify_password("password1", saved["password_hash"])
    assert result.user.id == "user-1"


def test_password_login_rejects_wrong_password():
    user = MagicMock(password_hash=hash_password("password1"), id="u1")
    service, _ = _service(existing=user)
    with pytest.raises(UnauthorizedError):
        service.login_with_password("ada@example.com", "nope-nope")


def test_password_login_google_only_account():
    user = MagicMock(password_hash=None, id="u1")
    service, _ = _service(existing=user)
    with pytest.raises(UnauthorizedError, match="Google"):
        service.login_with_password("ada@example.com", "password1")
