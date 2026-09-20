"""API tests for Google sign-in and session endpoints."""
from unittest.mock import patch

import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.infrastructure.db.models import User

settings = get_settings()


def _auth_header(user_id: str) -> dict[str, str]:
    token = jwt.encode({"sub": user_id, "exp": 2_000_000_000}, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return {"Authorization": f"Bearer {token}"}


@patch("app.modules.auth.service.id_token.verify_oauth2_token")
def test_google_login_creates_user_and_returns_jwt(mock_verify, client: TestClient, db_session):
    mock_verify.return_value = {
        "sub": "google-sub-123",
        "email": "traveler@example.com",
        "name": "Traveler",
    }

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        response = client.post("/auth/google", json={"id_token": "fake-google-token"})

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["user"]["email"] == "traveler@example.com"
    assert body["user"]["display_name"] == "Traveler"
    assert body["access_token"]

    payload = jwt.decode(body["access_token"], settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    user = db_session.get(User, payload["sub"])
    assert user is not None
    assert user.google_sub == "google-sub-123"


@patch("app.modules.auth.service.id_token.verify_oauth2_token")
def test_google_login_invalid_token_returns_401(mock_verify, client: TestClient):
    mock_verify.side_effect = ValueError("bad token")

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        response = client.post("/auth/google", json={"id_token": "bad-token"})

    assert response.status_code == 401
    assert response.json()["error"] == "unauthorized"


@patch("app.modules.auth.service.http_requests.get")
def test_google_login_accepts_access_token(mock_get, client: TestClient, db_session):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "aud": "test-client-id",
        "sub": "google-sub-access",
        "email": "access@example.com",
        "name": "Access User",
    }

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        response = client.post("/auth/google", json={"access_token": "fake-access-token"})

    assert response.status_code == 200, response.text
    assert response.json()["user"]["email"] == "access@example.com"
    user = db_session.query(User).filter(User.google_sub == "google-sub-access").one()
    assert user.email == "access@example.com"


def test_auth_me_requires_bearer_token(client: TestClient):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_auth_me_returns_current_user(client: TestClient, db_session):
    user = User(google_sub="sub-me", email="me@example.com", display_name="Me")
    db_session.add(user)
    db_session.commit()

    response = client.get("/auth/me", headers=_auth_header(user.id))
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == user.id
    assert body["email"] == "me@example.com"


def test_register_and_password_login(client: TestClient, db_session):
    created = client.post(
        "/auth/register",
        json={"email": "ada@example.com", "password": "secret123", "display_name": "آدا"},
    )
    assert created.status_code == 200, created.text
    assert created.json()["user"]["email"] == "ada@example.com"

    login = client.post("/auth/login", json={"email": "ada@example.com", "password": "secret123"})
    assert login.status_code == 200, login.text
    assert login.json()["access_token"]

    bad = client.post("/auth/login", json={"email": "ada@example.com", "password": "wrongpass"})
    assert bad.status_code == 401


def test_dev_login_returns_jwt(client: TestClient, db_session):
    with patch.object(settings, "ENV", "development"), patch.object(settings, "ALLOW_DEV_LOGIN", True):
        response = client.post("/auth/dev")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["access_token"]
    assert body["user"]["display_name"] == "کاربر آزمایشی"

    payload = jwt.decode(body["access_token"], settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    user = db_session.get(User, payload["sub"])
    assert user is not None
    assert user.google_sub == "dev:local"
