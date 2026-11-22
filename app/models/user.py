"""User model — maps to the 'users' collection in MongoDB."""

from typing import Optional
from pydantic import EmailStr, Field
from app.models.base import BaseDocument
from app.models.enums import UserRole


class User(BaseDocument):
    email: EmailStr
    hashed_password: str
    display_name: str = ""
    role: UserRole = UserRole.HUKUM
    family_ids: list[str] = Field(default_factory=list)  # List of MongoDB ObjectId strings of Families
    family_id: Optional[str] = None  # Active or primary Family ObjectId (backwards compatible)
    avatar_url: Optional[str] = None
    fcm_token: Optional[str] = None
    is_active: bool = True

    class Settings:
        name = "users"
        use_state_management = True

    class Config:
        json_schema_extra = {
            "example": {
                "email": "mummy@family.com",
                "display_name": "Mummy",
                "role": "Hukum",
                "family_id": "664b1f8e7a9b2c001f3e4d5a",
            }
        }
