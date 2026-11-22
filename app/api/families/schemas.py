"""Family schemas."""

from typing import Optional
from pydantic import BaseModel


class CreateFamilyRequest(BaseModel):
    name: str


class AddMemberToFamilyRequest(BaseModel):
    user_id: str
    role: Optional[str] = None  # e.g. "Hukum" or "Sethji" (optional, keeps existing role if omitted)


class UpdateMemberRoleRequest(BaseModel):
    role: str


class FamilyResponse(BaseModel):
    id: str
    name: str


class FamilyMemberResponse(BaseModel):
    id: str
    email: str
    displayName: str
    role: str
    avatarUrl: Optional[str] = None
    isActive: bool = True
