"""Auth controllers — handles HTTP request/response orchestration."""

from app.api.auth.schemas import (
    AdminUpdateUserRequest,
    CreateUserRequest,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    UpdateProfileRequest,
    UserResponse,
)
from app.api.auth.services import AuthService
from app.models.user import User


class AuthController:
    @staticmethod
    async def login(body: LoginRequest) -> TokenResponse:
        return await AuthService.authenticate_user(body)

    @staticmethod
    async def refresh(body: RefreshRequest) -> TokenResponse:
        return await AuthService.refresh_tokens(body.refresh_token)

    @staticmethod
    async def get_me(user: User) -> UserResponse:
        return AuthService.serialize_user(user)

    @staticmethod
    async def update_me(user: User, body: UpdateProfileRequest) -> UserResponse:
        return await AuthService.update_profile(user, body)

    @staticmethod
    async def admin_create_user(admin: User, body: CreateUserRequest) -> UserResponse:
        return await AuthService.admin_create_user(admin, body)

    @staticmethod
    async def list_users(unassigned_only: bool = False) -> list[UserResponse]:
        return await AuthService.list_users(unassigned_only)

    @staticmethod
    async def admin_update_user(user_id: str, body: AdminUpdateUserRequest) -> UserResponse:
        return await AuthService.admin_update_user(user_id, body)

    @staticmethod
    async def admin_delete_user(user_id: str) -> dict:
        return await AuthService.admin_delete_user(user_id)
