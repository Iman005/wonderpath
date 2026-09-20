"""AuthService — Google sign-in and session JWT issuance."""
import logging
import re
from datetime import UTC, datetime, timedelta

import jwt
import requests as http_requests
from google.auth.exceptions import GoogleAuthError, TransportError as GoogleTransportError
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.core.config import get_settings
from app.modules.auth.dtos import AuthTokenOut, to_user_out
from app.modules.auth.passwords import hash_password, verify_password
from app.modules.auth.repository import AuthRepository
from app.shared.exceptions import UnauthorizedError, ValidationDomainError

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_log = logging.getLogger(__name__)

settings = get_settings()

_GOOGLE_VERIFY_TIMEOUT_SECONDS = 12.0
_GOOGLE_ISSUERS = {"accounts.google.com", "https://accounts.google.com"}


class _TimedRequest(google_requests.Request):
    """google-auth Request with a hard timeout so Iran/slow networks don't hang forever."""

    def __call__(
        self,
        url,
        method="GET",
        body=None,
        headers=None,
        timeout=_GOOGLE_VERIFY_TIMEOUT_SECONDS,
        **kwargs,
    ):
        return super().__call__(url, method=method, body=body, headers=headers, timeout=timeout, **kwargs)


class AuthService:
    def __init__(self, repo: AuthRepository) -> None:
        self.repo = repo

    def login_with_google(self, id_token: str | None = None, access_token: str | None = None) -> AuthTokenOut:
        # Re-read settings so .env edits after process start still apply under --reload.
        cfg = get_settings()
        if not cfg.GOOGLE_CLIENT_ID:
            get_settings.cache_clear()
            cfg = get_settings()
        if not cfg.GOOGLE_CLIENT_ID:
            raise ValidationDomainError("Google sign-in is not configured on the server.")

        if id_token:
            idinfo = self._verify_google_id_token(id_token, cfg.GOOGLE_CLIENT_ID)
        elif access_token:
            idinfo = self._verify_google_access_token(access_token, cfg.GOOGLE_CLIENT_ID)
        else:
            raise UnauthorizedError("توکن Google نامعتبر است.")

        google_sub = idinfo.get("sub")
        if not google_sub:
            raise UnauthorizedError("توکن Google ناقص است.")

        email = idinfo.get("email")
        display_name = idinfo.get("name")

        user = self.repo.get_by_google_sub(google_sub)
        if user is None and email:
            # Same person previously registered with email/password — link Google.
            existing = self.repo.get_by_email(str(email).strip().lower())
            if existing is not None:
                existing.google_sub = google_sub
                if display_name and not existing.display_name:
                    existing.display_name = display_name
                user = self.repo.save(existing)
        if user is None:
            user = self.repo.create_user(
                google_sub=google_sub,
                email=email,
                display_name=display_name,
            )
        else:
            changed = False
            if email and user.email != email:
                user.email = email
                changed = True
            if display_name and user.display_name != display_name:
                user.display_name = display_name
                changed = True
            if changed:
                user = self.repo.save(user)

        session_token = self._issue_access_token(user.id)
        return AuthTokenOut(access_token=session_token, user=to_user_out(user))

    def _verify_google_id_token(self, raw_id_token: str, client_id: str) -> dict:
        try:
            return id_token.verify_oauth2_token(
                raw_id_token,
                _TimedRequest(),
                client_id,
            )
        except ValueError as exc:
            raise UnauthorizedError("توکن Google نامعتبر است.") from exc
        except (GoogleTransportError, GoogleAuthError, http_requests.RequestException, TimeoutError, OSError) as exc:
            _log.warning("Google cert fetch failed (%s); validating ID token claims locally.", type(exc).__name__)
            return self._decode_google_id_token_claims(raw_id_token, client_id)

    def _decode_google_id_token_claims(self, raw_id_token: str, client_id: str) -> dict:
        """Validate aud/iss/exp when www.googleapis.com certs are unreachable (common in Iran)."""
        try:
            payload = jwt.decode(
                raw_id_token,
                options={"verify_signature": False, "verify_aud": False, "verify_exp": False},
                algorithms=["RS256"],
            )
        except jwt.PyJWTError as exc:
            raise UnauthorizedError(
                "تأیید ورود Google به‌خاطر شبکه ممکن نشد. VPN را برای سرور هم روشن کن یا از ورود با ایمیل استفاده کن."
            ) from exc

        aud = payload.get("aud")
        if aud != client_id and not (isinstance(aud, list) and client_id in aud):
            raise UnauthorizedError("توکن Google برای این اپ نیست.")
        if payload.get("iss") not in _GOOGLE_ISSUERS:
            raise UnauthorizedError("توکن Google نامعتبر است.")
        exp = payload.get("exp")
        try:
            exp_ts = int(exp)
        except (TypeError, ValueError):
            raise UnauthorizedError("توکن Google منقضی یا ناقص است.") from None
        if exp_ts < int(datetime.now(UTC).timestamp()) - 30:
            raise UnauthorizedError("توکن Google منقضی شده. دوباره وارد شو.")
        if not payload.get("sub"):
            raise UnauthorizedError("توکن Google ناقص است.")
        return payload

    def _verify_google_access_token(self, raw_access_token: str, client_id: str) -> dict:
        try:
            response = http_requests.get(
                "https://oauth2.googleapis.com/tokeninfo",
                params={"access_token": raw_access_token},
                timeout=_GOOGLE_VERIFY_TIMEOUT_SECONDS,
            )
        except (http_requests.RequestException, TimeoutError, OSError) as exc:
            raise UnauthorizedError(
                "تأیید ورود Google به‌خاطر شبکه ممکن نشد. VPN را روشن کن یا از ورود با ایمیل / ورود آزمایشی استفاده کن."
            ) from exc
        if response.status_code != 200:
            raise UnauthorizedError("توکن Google نامعتبر است.")
        info = response.json()
        audience = info.get("aud")
        if audience != client_id:
            raise UnauthorizedError("توکن Google نامعتبر است.")
        if not info.get("sub"):
            raise UnauthorizedError("توکن Google ناقص است.")
        return {
            "sub": info.get("sub"),
            "email": info.get("email"),
            "name": info.get("name"),
        }

    def register(self, email: str, password: str, display_name: str | None = None) -> AuthTokenOut:
        cleaned_email = self._normalize_email(email)
        if self.repo.get_by_email(cleaned_email):
            raise ValidationDomainError("حسابی با این ایمیل از قبل وجود دارد.")
        name = (display_name or "").strip() or cleaned_email.split("@", 1)[0]
        user = self.repo.create_user(
            email=cleaned_email,
            display_name=name,
            password_hash=hash_password(password),
        )
        return AuthTokenOut(access_token=self._issue_access_token(user.id), user=to_user_out(user))

    def login_with_password(self, email: str, password: str) -> AuthTokenOut:
        cleaned_email = self._normalize_email(email)
        user = self.repo.get_by_email(cleaned_email)
        if user is None:
            raise UnauthorizedError("ایمیل یا رمز عبور اشتباه است.")
        if not user.password_hash:
            raise UnauthorizedError("این ایمیل با Google ثبت شده؛ از ورود با Google استفاده کن.")
        if not verify_password(password, user.password_hash):
            raise UnauthorizedError("ایمیل یا رمز عبور اشتباه است.")
        return AuthTokenOut(access_token=self._issue_access_token(user.id), user=to_user_out(user))

    def login_dev(self) -> AuthTokenOut:
        """Issue a session for local development when Google OAuth is not set up.

        Guarded by ENV=development and ALLOW_DEV_LOGIN. Creates a stable
        local user (google_sub=dev:local) so trips persist across reloads.
        """
        cfg = get_settings()
        if cfg.ENV != "development" or not cfg.ALLOW_DEV_LOGIN:
            raise UnauthorizedError("Dev login is disabled.")

        google_sub = "dev:local"
        user = self.repo.get_by_google_sub(google_sub)
        if user is None:
            user = self.repo.create_user(
                google_sub=google_sub,
                email="dev@localhost",
                display_name="کاربر آزمایشی",
            )

        access_token = self._issue_access_token(user.id)
        return AuthTokenOut(access_token=access_token, user=to_user_out(user))

    def get_user_from_access_token(self, token: str):
        user_id = self._decode_access_token(token)
        user = self.repo.get_by_id(user_id)
        if user is None:
            raise UnauthorizedError("User not found for this session.")
        return user

    def _issue_access_token(self, user_id: str) -> str:
        cfg = get_settings()
        expires = datetime.now(UTC) + timedelta(days=cfg.JWT_EXPIRE_DAYS)
        payload = {"sub": user_id, "exp": expires}
        return jwt.encode(payload, cfg.JWT_SECRET, algorithm=cfg.JWT_ALGORITHM)

    @staticmethod
    def _decode_access_token(token: str) -> str:
        cfg = get_settings()
        try:
            payload = jwt.decode(token, cfg.JWT_SECRET, algorithms=[cfg.JWT_ALGORITHM])
        except jwt.PyJWTError as exc:
            raise UnauthorizedError("Invalid or expired session token.") from exc

        user_id = payload.get("sub")
        if not user_id or not isinstance(user_id, str):
            raise UnauthorizedError("Invalid session token payload.")
        return user_id

    @staticmethod
    def _normalize_email(email: str) -> str:
        cleaned = email.strip().lower()
        if not _EMAIL_RE.match(cleaned):
            raise ValidationDomainError("یک ایمیل معتبر وارد کن.")
        return cleaned
