"""Requested Items schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class CreateRequestedItemRequest(BaseModel):
    name: str


class ApproveRequestedItemRequest(BaseModel):
    category: str = "Vegetables"
    allowed_units: list[str] = Field(default_factory=lambda: ["pieces"])


class RequestedItemResponse(BaseModel):
    id: str
    name: str
    requestedBy: str
    requestedById: str
    familyId: Optional[str] = None
    status: str
    createdAt: Optional[str] = None
