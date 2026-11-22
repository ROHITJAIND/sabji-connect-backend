"""Auth routes — HTTP endpoint definitions."""

from fastapi import APIRouter, Depends, Query

from app.api.auth.controllers import AuthController
from app.api.auth.schemas import (
    AdminUpdateUserRequest,
    CreateUserRequest,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    UpdateProfileRequest,
    UserResponse,
)
from app.core.auth.dependencies import CurrentUser, require_role

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    """Authenticate with email + password, receive JWT tokens."""
    return await AuthController.login(body)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshRequest):
    """Exchange a refresh token for a new access + refresh token pair."""
    return await AuthController.refresh(body)


@router.get("/me", response_model=UserResponse)
async def get_me(user: CurrentUser):
    """Return the current authenticated user's profile."""
    return await AuthController.get_me(user)


@router.patch("/me", response_model=UserResponse)
async def update_me(body: UpdateProfileRequest, user: CurrentUser):
    """Update current user profile (display name, avatar, FCM token)."""
    return await AuthController.update_me(user, body)


@router.post("/users", response_model=UserResponse, dependencies=[Depends(require_role("Admin"))])
async def admin_create_user(body: CreateUserRequest, admin: CurrentUser):
    """Admin-only: Create a new user in the users section."""
    return await AuthController.admin_create_user(admin, body)


@router.get("/users", response_model=list[UserResponse], dependencies=[Depends(require_role("Admin"))])
async def list_users(unassigned_only: bool = Query(False, description="Filter for users not assigned to any family")):
    """Admin-only: List users (can filter for unassigned users to add to a family)."""
    return await AuthController.list_users(unassigned_only)


@router.patch("/users/{user_id}", response_model=UserResponse, dependencies=[Depends(require_role("Admin"))])
async def admin_update_user(user_id: str, body: AdminUpdateUserRequest):
    """Admin-only: Update user details."""
    return await AuthController.admin_update_user(user_id, body)


@router.delete("/users/{user_id}", dependencies=[Depends(require_role("Admin"))])
async def admin_delete_user(user_id: str):
    """Admin-only: Delete a user."""
    return await AuthController.admin_delete_user(user_id)
