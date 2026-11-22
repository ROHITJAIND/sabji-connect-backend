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
    family_id: Optional[str] = None


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
    family_id: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True


class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    fcm_token: Optional[str] = None
