"""Family schemas."""

from typing import Optional
from pydantic import BaseModel


class CreateFamilyRequest(BaseModel):
    name: str


class UpdateFamilyRequest(BaseModel):
    name: str


class AddMemberToFamilyRequest(BaseModel):
    user_id: str


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
