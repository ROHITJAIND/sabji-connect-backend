"""User model — maps to the 'users' collection in MongoDB."""

from datetime import datetime, timezone
from typing import Optional

from beanie import Document
from pydantic import EmailStr, Field


class User(Document):
    email: EmailStr
    hashed_password: str
    display_name: str = ""
    role: str = "Hukum"  # Admin | Hukum | Sethji
    family_ids: list[str] = Field(default_factory=list)  # List of MongoDB ObjectId strings of Families
    family_id: Optional[str] = None  # Active or primary Family ObjectId (backwards compatible)
    avatar_url: Optional[str] = None
    fcm_token: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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
