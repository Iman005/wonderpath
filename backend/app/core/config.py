"""
Application configuration.

All environment-dependent values are read from environment variables
(via a .env file in local development). Nothing here is hardcoded so the
app can move from SQLite (local dev) to PostgreSQL (production) without
code changes.
"""
import json
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    APP_NAME: str = "WanderPath API"
    ENV: str = "development"
    DEBUG: bool = True

    # --- Database ---
    # Defaults to a local SQLite file so the project runs out of the box
    # without requiring a Postgres instance. Set DATABASE_URL in .env to
    # point at Postgres in staging/production, e.g.:
    # postgresql+psycopg2://user:pass@localhost:5432/wanderpath
    DATABASE_URL: str = "sqlite:///./wanderpath.db"

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    # Lets the Railway frontend talk to the API before the exact public URL is known.
    CORS_ORIGIN_REGEX: str = r"https://.*\.(fly\.dev|vercel\.app|up\.railway\.app)"

    @property
    def cors_origin_list(self) -> list[str]:
        text = self.CORS_ORIGINS.strip()
        if not text:
            return []
        if text.startswith("["):
            loaded = json.loads(text)
            return [str(item) for item in loaded]
        return [item.strip() for item in text.split(",") if item.strip()]

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value: object) -> object:
        if not isinstance(value, str) or not value:
            return value
        url = value
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://") :]
        if url.startswith("postgresql://") and "+psycopg2" not in url and "+psycopg" not in url:
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url

    # --- Neshan (map + place data provider) ---
    NESHAN_API_KEY: str = ""
    NESHAN_MAP_BASE_URL: str = "https://api.neshan.org/v4"
    NESHAN_PLACE_BASE_URL: str = "https://api.neshan.org/v1"
    NESHAN_MAP_STYLE_URL: str = "https://static.neshan.org/sdk/maplibre/styles/light.json"

    # --- Place/City cache ---
    PLACE_CACHE_TTL_SECONDS: int = 60 * 60 * 24 * 7  # 7 days
    ROUTE_CACHE_TTL_SECONDS: int = 60 * 60 * 24  # 24 hours

    # --- Device identity (guest fallback during auth transition) ---
    DEVICE_ID_HEADER_NAME: str = "X-Device-Id"
    DEVICE_ID_COOKIE_NAME: str = "wanderpath_device_id"
    DEVICE_ID_COOKIE_TTL_DAYS: int = 365

    # --- Auth (Google sign-in + session JWT) ---
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 30
    GOOGLE_CLIENT_ID: str = ""
    # Local-only login when Google OAuth is not configured yet.
    # Never enable in production.
    ALLOW_DEV_LOGIN: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
