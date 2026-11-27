"""User model — maps to the 'users' collection in MongoDB."""

from typing import Optional
from beanie import Document
from pydantic import Field, field_validator
from app.models.base import BaseDocument
from app.models.enums import UserRole


class User(Document, BaseDocument):
    username: str
    hashed_password: str
    display_name: str = ""
    role: UserRole = UserRole.HUKUM
    family_ids: list[str] = Field(default_factory=list)  # List of MongoDB ObjectId strings of Families
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    fcm_token: Optional[str] = None
    is_active: bool = True

    @field_validator("username", mode="before")
    @classmethod
    def normalize_username(cls, v):
        if v:
            return str(v).strip().lower()
        return v

    class Settings:
        name = "users"
        use_state_management = True
