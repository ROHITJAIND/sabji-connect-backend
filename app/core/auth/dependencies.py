"""FastAPI dependencies for extracting and verifying the current user.

Uses standard HTTPBearer security scheme so Swagger UI displays the
Authorize 🔓 lock button, and works natively with Android (Retrofit/OkHttp/Ktor)
clients using the standard "Authorization: Bearer <token>" header.
"""

from typing import Annotated

from beanie import PydanticObjectId
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from app.core.auth.jwt import decode_token
from app.core.exceptions import AuthenticationError, NotAuthorizedError
from app.models.user import User

# Standard HTTP Bearer scheme -> enables Swagger UI "Authorize 🔓" button
# auto_error=False allows custom exception formatting
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]
) -> User:
    """Extract Bearer token from the Authorization header and return the User document."""
    if not credentials or not credentials.credentials:
        raise AuthenticationError("Authentication token missing")

    token = credentials.credentials

    try:
        payload = decode_token(token)
    except JWTError:
        raise AuthenticationError("Invalid or expired token")

    if payload.get("type") != "access":
        raise AuthenticationError("Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload")

    user = await User.get(PydanticObjectId(user_id))
    if user is None:
        raise AuthenticationError("User not found")

    if not user.is_active:
        raise AuthenticationError("User account is deactivated")

    return user


# Shorthand dependency annotations
CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(*allowed_roles: str):
    """Factory that returns a dependency enforcing role-based access.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role("Admin"))])
    """

    async def _check(user: CurrentUser) -> User:
        if user.role not in allowed_roles:
            raise NotAuthorizedError(
                f"This action requires one of: {', '.join(allowed_roles)}"
            )
        return user

    return _check
