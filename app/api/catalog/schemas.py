"""Catalog schemas."""

from typing import Optional
from pydantic import BaseModel, Field
from app.models.enums import ItemCategory, ItemUnit


class CatalogItemCreate(BaseModel):
    name: str
    category: ItemCategory = ItemCategory.VEGETABLES
    allowed_units: list[ItemUnit] = Field(default_factory=lambda: [ItemUnit.PIECES])
    image_url: Optional[str] = None


class CatalogItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[ItemCategory] = None
    allowed_units: Optional[list[ItemUnit]] = None
    image_url: Optional[str] = None


class CatalogItemResponse(BaseModel):
    id: str
    name: str
    category: ItemCategory
    allowedUnits: list[ItemUnit]
    imageUrl: Optional[str] = None
