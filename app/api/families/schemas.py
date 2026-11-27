"""Family schemas."""

from typing import Optional
from pydantic import BaseModel
from app.models.enums import UserRole


class CreateFamilyRequest(BaseModel):
    name: str


class UpdateFamilyRequest(BaseModel):
    name: str


class AddMemberToFamilyRequest(BaseModel):
    user_id: str


class FamilyResponse(BaseModel):
    id: str
    name: str
    members: list[str] = []


class FamilyMemberResponse(BaseModel):
    id: str
    username: str
    displayName: str
    role: UserRole
    email: Optional[str] = None
    avatarUrl: Optional[str] = None
    isActive: bool = True
