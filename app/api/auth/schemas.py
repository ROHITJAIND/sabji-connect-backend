"""Auth schemas."""

from typing import Optional
from pydantic import BaseModel, model_validator
from app.models.enums import UserRole


class LoginRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: str

    @model_validator(mode="before")
    @classmethod
    def extract_username(cls, data):
        if isinstance(data, dict):
            raw_user = data.get("username") or data.get("email") or ""
            data["username"] = str(raw_user).strip().lower()
        return data


class CreateUserRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: str
    display_name: str = ""
    role: UserRole = UserRole.HUKUM

    @model_validator(mode="before")
    @classmethod
    def extract_username(cls, data):
        if isinstance(data, dict):
            raw_user = data.get("username") or data.get("email") or ""
            clean_user = str(raw_user).strip().lower()
            if "@" in clean_user:
                clean_user = clean_user.split("@")[0]
            data["username"] = clean_user
        return data


class AdminUpdateUserRequest(BaseModel):
    username: Optional[str] = None
    display_name: Optional[str] = None
    role: Optional[UserRole] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    username: str
    display_name: str
    role: UserRole
    family_ids: list[str] = []
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True


class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    fcm_token: Optional[str] = None
