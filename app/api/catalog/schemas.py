"""Catalog schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class CatalogItemCreate(BaseModel):
    name: str
    category: str = "Vegetables"
    allowed_units: list[str] = Field(default_factory=lambda: ["pieces"])
    image_url: Optional[str] = None


class CatalogItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    allowed_units: Optional[list[str]] = None
    image_url: Optional[str] = None


class CatalogItemResponse(BaseModel):
    id: str
    name: str
    category: str
    allowedUnits: list[str]
    imageUrl: Optional[str] = None
