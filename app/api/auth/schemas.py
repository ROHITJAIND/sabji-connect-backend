"""Auth schemas."""

from typing import Optional
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str = ""
    role: str = "Hukum"  # Admin | Hukum | Sethji


class AdminUpdateUserRequest(BaseModel):
    display_name: Optional[str] = None
    role: Optional[str] = None  # Admin | Hukum | Sethji
    email: Optional[EmailStr] = None
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
    email: str
    display_name: str
    role: str
    family_ids: list[str] = []
    family_id: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True


class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    fcm_token: Optional[str] = None
    family_id: Optional[str] = None  # Active family switcher
    avatar_url: Optional[str] = None
    fcm_token: Optional[str] = None
