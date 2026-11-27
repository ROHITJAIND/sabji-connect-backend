"""Auth services — business logic and DB operations."""

from datetime import datetime, timezone
from typing import Optional

from beanie import PydanticObjectId

from app.core.auth.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.exceptions import AuthenticationError, BadRequestError, ConflictError, NotFoundError
from app.models.enums import UserRole
from app.models.user import User
from app.api.auth.schemas import (
    AdminUpdateUserRequest,
    CreateUserRequest,
    LoginRequest,
    TokenResponse,
    UpdateProfileRequest,
    UserResponse,
)


class AuthService:
    @staticmethod
    def serialize_user(user: User) -> UserResponse:
        uname = getattr(user, "username", None) or (user.email.split("@")[0] if getattr(user, "email", None) else "user")
        if user.role == UserRole.ADMIN:
            return UserResponse(
                id=str(user.id),
                username=uname,
                email=getattr(user, "email", None),
                display_name=user.display_name or uname,
                role=user.role,
                family_ids=[],
                avatar_url=user.avatar_url,
                is_active=user.is_active,
            )

        fids = list(user.family_ids or [])

        return UserResponse(
            id=str(user.id),
            username=uname,
            email=getattr(user, "email", None),
            display_name=user.display_name or uname,
            role=user.role,
            family_ids=fids,
            avatar_url=user.avatar_url,
            is_active=user.is_active,
        )

    @staticmethod
    async def authenticate_user(body: LoginRequest) -> TokenResponse:
        identifier = body.username.strip().lower()
        user = await User.find_one(
            {
                "$or": [
                    {"username": identifier},
                    {"email": identifier},
                    {"email": f"{identifier}@sabji.com"},
                    {"email": f"{identifier}@sabjiconnect.com"},
                ]
            }
        )
        if not user or not verify_password(body.password, user.hashed_password):
            raise AuthenticationError("Invalid username or password")

        if not user.is_active:
            raise AuthenticationError("Account is deactivated")

        token_data = {"sub": str(user.id), "role": user.role}
        return TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
        )

    @staticmethod
    async def refresh_tokens(refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
        except Exception:
            raise AuthenticationError("Invalid or expired refresh token")

        if payload.get("type") != "refresh":
            raise AuthenticationError("Invalid token type")

        user_id = payload.get("sub")
        user = await User.get(PydanticObjectId(user_id))
        if not user or not user.is_active:
            raise AuthenticationError("User not found or deactivated")

        token_data = {"sub": str(user.id), "role": user.role}
        return TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
        )

    @staticmethod
    async def update_profile(user: User, body: UpdateProfileRequest) -> UserResponse:
        update_data: dict = {}
        if body.display_name is not None:
            update_data["display_name"] = body.display_name
        if body.avatar_url is not None:
            update_data["avatar_url"] = body.avatar_url
        if body.fcm_token is not None:
            update_data["fcm_token"] = body.fcm_token

        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc)
            await user.set(update_data)

        return AuthService.serialize_user(user)

    @staticmethod
    async def admin_create_user(admin: User, body: CreateUserRequest) -> UserResponse:
        if admin.role != UserRole.ADMIN:
            raise BadRequestError("Only Admin can create users")

        uname = body.username.strip().lower()
        existing = await User.find_one(
            {
                "$or": [
                    {"username": uname},
                    {"email": uname},
                    {"email": f"{uname}@sabjiconnect.com"},
                    {"email": f"{uname}@sabji.com"},
                ]
            }
        )
        if existing:
            raise ConflictError("A user with this username already exists")

        user = User(
            username=uname,
            email=None,
            hashed_password=hash_password(body.password),
            display_name=body.display_name or uname,
            role=body.role,
            family_ids=[],
        )
        await user.insert()
        return AuthService.serialize_user(user)

    @staticmethod
    async def list_users(unassigned_only: bool = False) -> list[UserResponse]:
        if unassigned_only:
            users = await User.find(
                User.role != UserRole.ADMIN,
                {"$or": [{"family_ids": {"$size": 0}}, {"family_ids": []}, {"family_ids": None}]},
                User.is_active == True,
            ).to_list()
        else:
            users = await User.find(User.is_active == True).to_list()

        return [AuthService.serialize_user(u) for u in users]

    @staticmethod
    async def admin_update_user(user_id: str, body: AdminUpdateUserRequest) -> UserResponse:
        user = await User.get(PydanticObjectId(user_id))
        if not user:
            raise NotFoundError("User not found")

        update_data = {}
        if body.username is not None and body.username.strip():
            new_uname = body.username.strip().lower()
            if new_uname != getattr(user, "username", None):
                existing = await User.find_one({"username": new_uname})
                if existing:
                    raise ConflictError("A user with this username already exists")
                update_data["username"] = new_uname
        if body.display_name is not None and body.display_name.strip():
            update_data["display_name"] = body.display_name.strip()
        if body.role is not None:
            update_data["role"] = body.role
            if body.role == UserRole.ADMIN:
                update_data["family_ids"] = []
        if body.password is not None and body.password.strip():
            update_data["hashed_password"] = hash_password(body.password.strip())
        if body.is_active is not None:
            update_data["is_active"] = body.is_active

        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc)
            await user.set(update_data)

        return AuthService.serialize_user(user)

    @staticmethod
    async def admin_delete_user(user_id: str) -> dict:
        user = await User.get(PydanticObjectId(user_id))
        if not user:
            raise NotFoundError("User not found")

        if user.role == UserRole.ADMIN:
            admin_count = await User.find(User.role == UserRole.ADMIN, User.is_active == True).count()
            if admin_count <= 1:
                raise BadRequestError("Cannot delete the last admin account")

        await user.set({"is_active": False, "updated_at": datetime.now(timezone.utc)})
        return {"id": user_id, "message": "User deactivated successfully"}
