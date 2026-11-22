"""Requested Items schemas."""

from typing import Optional
from pydantic import BaseModel, Field
from app.models.enums import ItemCategory, ItemUnit, RequestedItemStatus


class CreateRequestedItemRequest(BaseModel):
    name: str


class ApproveRequestedItemRequest(BaseModel):
    category: ItemCategory = ItemCategory.VEGETABLES
    allowed_units: list[ItemUnit] = Field(default_factory=lambda: [ItemUnit.PIECES])


class RequestedItemResponse(BaseModel):
    id: str
    name: str
    requestedBy: str
    requestedById: str
    familyId: Optional[str] = None
    status: RequestedItemStatus
    createdAt: Optional[str] = None
