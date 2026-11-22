"""
Environment configuration for Sabji Connect — Family Groceries.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

# Always locate .env relative to the backend root directory
_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_PATH = _BACKEND_ROOT / ".env"


class Env(BaseSettings):
    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "Sabji Connect"
    APP_VERSION: str = "1.0.0"
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    # ── Server ───────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── CORS ─────────────────────────────────────────────────────
    CORS_ORIGINS: str = "*"

    # ── MongoDB ──────────────────────────────────────────────────
    MONGODB_URI: str
    MONGODB_DATABASE: str = "sabji_connect"

    # ── Authentication & JWT ─────────────────────────────────────
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days (mobile-friendly)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 90

    # ── Cloudinary (catalog item images) ─────────────────────────
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None

    # ── FCM Push Notifications ───────────────────────────────────
    FCM_SERVER_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=_ENV_PATH if _ENV_PATH.exists() else ".env",
        extra="ignore",
    )

    @property
    def IS_DEV(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"

    @property
    def IS_PROD(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def CORS_ORIGINS_LIST(self) -> list[str]:
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


_env_instance: Optional[Env] = None


def get_env() -> Env:
    """Get the singleton environment configuration instance."""
    global _env_instance
    if _env_instance is None:
        try:
            _env_instance = Env()  # type: ignore[call-arg]
        except Exception as e:
            raise ValueError(
                "Failed to load environment configuration. Ensure that "
                "all required environment variables are set."
            ) from e
    return _env_instance


env: Env = get_env()
