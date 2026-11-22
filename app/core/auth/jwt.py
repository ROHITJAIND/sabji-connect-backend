"""JWT authentication utilities for Sabji Connect.

Designed for mobile (Android) clients — tokens are long-lived and
transmitted via Authorization: Bearer <token> headers.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import env

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against its bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=env.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, env.JWT_SECRET_KEY, algorithm=env.JWT_ALGORITHM)


def create_refresh_token(data: dict[str, Any]) -> str:
    """Create a JWT refresh token with longer expiry."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=env.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, env.JWT_SECRET_KEY, algorithm=env.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token. Raises JWTError on failure."""
    return jwt.decode(token, env.JWT_SECRET_KEY, algorithms=[env.JWT_ALGORITHM])
